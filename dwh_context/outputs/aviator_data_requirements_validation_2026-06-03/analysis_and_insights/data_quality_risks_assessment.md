# Aviator Data Quality Risks Assessment

## Executive Summary

This assessment identifies **critical data compatibility risks** that could impact analytical capabilities and downstream system integrations. The primary concerns center on **transaction ID type changes**, **missing user dimensions**, and **leaderboard data deferrals**. Immediate validation and mitigation strategies are required before production launch.

---

## Critical Risk Assessment (🔴 High Priority)

### 1. Transaction ID Type Compatibility 🔴

**Risk Description**: Transaction IDs changed from `integer` to `String`, potentially breaking payment table joins
```sql
-- BEFORE (Original)
transaction_id: integer
origin_transaction_id: integer

-- AFTER (Implementation)  
aviatorTransactionId: String (nullable)
originTransactionId: String
```

**Impact Analysis**:
- **Payment Joins**: Critical for revenue analysis and purchase attribution
- **Affected Tables**: `dwh.sm_fact_payments`, `dwh.sm_goods_router_*`
- **Query Impact**: All analytical queries joining Aviator to payment data

**Specific Risks**:
```sql
-- This type of join may fail:
SELECT a.game_id, p.revenue_usd, p.product_name
FROM sm_aviator a
LEFT JOIN dwh.sm_fact_payments p 
  ON a.origin_transaction_id = p.transaction_id  -- String vs Integer mismatch?

-- Risk scenarios:
-- 1. Implicit casting failures in Vertica
-- 2. Performance degradation from type conversions  
-- 3. Silent data mismatches if casting rules change
```

**Validation Required**:
```sql
-- Test current payment table transaction_id types
SELECT DISTINCT 
  DATA_TYPE, 
  CHARACTER_MAXIMUM_LENGTH,
  NUMERIC_PRECISION
FROM V_CATALOG.COLUMNS 
WHERE TABLE_SCHEMA = 'dwh' 
  AND TABLE_NAME = 'sm_fact_payments' 
  AND COLUMN_NAME = 'transaction_id';

-- Test sample join compatibility
SELECT COUNT(*) 
FROM sample_aviator_data a
LEFT JOIN dwh.sm_fact_payments p 
  ON a.origin_transaction_id::varchar = p.transaction_id::varchar;
```

**Mitigation Strategies**:
1. **Pre-Launch Testing**: Validate joins with sample data
2. **Explicit Casting**: Use `::varchar` conversions in analytical queries
3. **Performance Testing**: Measure impact of type conversions
4. **Documentation**: Update all analytical query templates

### 2. Session ID Type Change Impact 🔴

**Risk Description**: Session ID changed from `integer` to `String`
```sql  
-- BEFORE: session_id: integer
-- AFTER: sessionId: String
```

**Impact Analysis**:
- **Session Tracking**: Integration with existing session analytics
- **User Journey Analysis**: Multi-feature session analysis
- **Performance**: String-based joins vs integer joins

**Validation Required**:
```sql
-- Check session dimension table types
SELECT DATA_TYPE 
FROM V_CATALOG.COLUMNS 
WHERE TABLE_SCHEMA = 'dwh' 
  AND TABLE_NAME LIKE '%session%' 
  AND COLUMN_NAME LIKE '%session%id%';

-- Test session join compatibility
SELECT s.session_id, a.game_id
FROM dwh.user_sessions s
LEFT JOIN aviator_events a ON s.session_id = a.session_id;
```

**Mitigation**:
1. Verify session tracking infrastructure supports String IDs
2. Update session analysis queries with appropriate casting
3. Test performance impact of String-based session joins

---

## High Risk Assessment (🟡 Medium-High Priority) 

### 3. Missing User Dimension Fields 🟡

**Risk Description**: Key user fields removed from streaming events
```sql
-- REMOVED FIELDS:
tier_id: integer          -- Out of service scope (BI-3)
prestige_level: integer    -- Out of service scope (BI-3) 
current_parameter_value: varchar  -- Out of service scope (BI-4)
```

**Impact Analysis**:
- **User Segmentation**: Limited real-time user context  
- **Performance Analysis**: Cannot segment by tier/prestige in streaming
- **Dashboard Limitations**: Requires additional joins for user context

**Current State**: ❓ **Resolution pending** - "BI-side handling or separate enhancement"

**Mitigation Options**:
```sql
-- Option 1: ETL-time enrichment
WITH enriched_aviator AS (
  SELECT a.*, 
         u.tier_id,
         u.prestige_level  
  FROM sm_aviator a
  LEFT JOIN dwh.sm_user_profile_datamining_snapshot u
    ON a.user_id = u.user_id 
    AND a.event_date = u.snapshot_date
)

-- Option 2: Real-time dimension lookup (performance cost)
SELECT a.*, u.tier_id, u.prestige_level
FROM aviator_streaming a
LEFT JOIN dwh.sm_user_profile_datamining_snapshot u
  ON a.user_id = u.user_id
  AND u.snapshot_date = (
    SELECT MAX(snapshot_date) 
    FROM dwh.sm_user_profile_datamining_snapshot u2 
    WHERE u2.user_id = a.user_id 
      AND u2.snapshot_date <= a.event_date
  );
```

**Recommendations**:
1. **Clarify Resolution**: Get definitive answer on user dimension strategy
2. **Performance Planning**: If joins required, plan for query performance impact  
3. **Dashboard Design**: Plan user segmentation approach for Aviator dashboards

### 4. Round Number Population Gaps 🟡

**Risk Description**: `roundIdx` only populated on events 4,5 (ROUND_STARTED, ROUND_ENDED) instead of all events

**Impact Analysis**:
- **Event Correlation**: Harder to correlate purchase/reward events to specific rounds
- **Query Complexity**: Requires joins to determine round context for Events 1,2,3,6
- **Real-time Analysis**: Limited round-based filtering for non-round events

**Current State**: 
```sql
-- Event Population Matrix:
-- Event 1 (FROZEN): roundIdx = NULL
-- Event 2 (READY_TO_PLAY): roundIdx = NULL  
-- Event 3 (OFFER_DECLINED): roundIdx = NULL
-- Event 4 (ROUND_STARTED): roundIdx = populated
-- Event 5 (ROUND_ENDED): roundIdx = populated  
-- Event 6 (USER_REWARDED): roundIdx = NULL
```

**Mitigation Strategy**:
```sql
-- Derive round context via window functions
WITH round_enriched AS (
  SELECT *,
    CASE 
      WHEN round_idx IS NOT NULL THEN round_idx
      ELSE LAG(round_idx) OVER (
        PARTITION BY game_id 
        ORDER BY event_ts, 
        CASE event_type 
          WHEN 'ROUND_STARTED' THEN 1 
          WHEN 'ROUND_ENDED' THEN 2 
          ELSE 3 
        END
      )
    END AS derived_round_idx
  FROM aviator_events
)
```

### 5. Leaderboard Data Deferral 🟡

**Risk Description**: Competitive analysis fields deferred pending BI-13 decision
```sql  
-- DEFERRED FIELDS:
max_leaderboard_value: double precision
min_leaderboard_value: double precision
```

**Impact Analysis**:
- **Competitive Analysis**: Cannot measure social proof impact on player behavior
- **Game Balancing**: Limited insights into leaderboard influence on timing decisions
- **Feature Optimization**: Missing key behavioral driver data

**Current Status**: 🟡 **Pending BI-13** - Options under discussion:
- Option A: 2 scalars (Top Wins + Low Cashouts computed)
- Option B: List of 5 computed values  
- Option C: Full per-statistic snapshot

**Business Impact**:
```sql
-- ANALYTICAL LIMITATIONS:
-- Cannot answer: How does leaderboard display affect player lock timing?
-- Cannot measure: Competitive pressure impact on round outcomes
-- Cannot optimize: Leaderboard value ranges for maximum engagement
```

**Mitigation**:
1. **Priority Assessment**: Determine analytical priority for competitive analysis
2. **Workaround Planning**: Consider config-based leaderboard value derivation
3. **Implementation Timeline**: Push for BI-13 resolution before launch if critical

---

## Medium Risk Assessment (🟡 Medium Priority)

### 6. SKU ID Access Method Change 🟡

**Risk Description**: SKU tracking moved from direct field to derivable via joins
```sql
-- BEFORE: SKU_id: integer (direct in events)
-- AFTER: Derivable via aviatorTransactionId + Goods Router join
```

**Impact**: 
- **Query Complexity**: Additional join required for product analysis
- **Performance**: Potential performance impact from cross-topic joins
- **Data Freshness**: Dependency on Goods Router data availability

**Mitigation**:
```sql
-- Establish reliable join pattern for SKU derivation
SELECT a.game_id, 
       a.aviator_transaction_id,
       gr.sku_id,
       gr.product_name
FROM aviator_events a
LEFT JOIN dwh.goods_router_bonus_history gr
  ON a.aviator_transaction_id = gr.transaction_id
WHERE a.aviator_transaction_id IS NOT NULL;
```

### 7. Event Timing Dependencies 🟡

**Risk Description**: Complex event sequencing requires careful validation
```sql
-- Expected Sequences:
-- SUCCESS: 1,2,4,5,4,5,6 (2-round completion)
-- DECLINE: 1,2,3 (offer declined)
-- PARTIAL: 1,2,4,5 (single round, incomplete?)
```

**Validation Requirements**:
```sql
-- Detect invalid sequences
WITH sequences AS (
  SELECT game_id,
         LISTAGG(event_type, ',') WITHIN GROUP (ORDER BY event_ts) as sequence,
         COUNT(*) as event_count
  FROM aviator_events
  GROUP BY game_id
)
SELECT sequence, COUNT(*) as occurrence_count
FROM sequences  
WHERE sequence NOT IN (
  '1,2,4,5,4,5,6',  -- Standard 2-round
  '1,2,3',          -- Decline
  '1,2,4,5,6'       -- Single round  
)
GROUP BY sequence;
```

---

## Low Risk Assessment (🟢 Low Priority)

### 8. Enhanced Precision Benefits 🟢

**Positive Change**: Financial fields upgraded to `BigDecimal`
```sql
-- BEFORE: double precision (limited precision)
-- AFTER: BigDecimal (arbitrary precision)
```

**Benefits**:
- More accurate financial calculations
- Eliminates floating-point rounding errors  
- Better precision for large monetary values

**Considerations**:
- Query formatting may need updates for BigDecimal display
- Potential performance differences (minimal)

### 9. Expanded Event Granularity 🟢 

**Positive Change**: 4 events → 6 events provides better tracking
```sql
-- Enhanced tracking capabilities:
-- - Purchase split into configuration + availability phases
-- - Offer decline tracking added
-- - Better state transition monitoring
```

**Benefits**:
- More granular funnel analysis
- Better debugging and monitoring
- Enhanced user journey understanding

---

## Risk Mitigation Timeline

### Pre-Launch (Critical - Week 1)
1. **🔴 Transaction ID Compatibility Testing**
   - Validate all payment table joins
   - Test performance with type casting
   - Update analytical query templates

2. **🔴 Session ID Verification** 
   - Confirm session infrastructure compatibility
   - Test session-based analytical queries

3. **🟡 User Dimension Strategy Clarification**
   - Get definitive answer from RnD on tier/prestige access
   - Plan analytical workarounds if needed

### Launch Week (High Priority)
4. **🟡 Event Sequence Monitoring**
   - Implement real-time sequence validation
   - Set up alerts for invalid event patterns

5. **🟡 Performance Monitoring**
   - Monitor join performance with new data types
   - Track query execution times

### Post-Launch (Medium Priority)  
6. **🟡 Leaderboard Implementation Follow-up**
   - Push for BI-13 resolution
   - Implement leaderboard analysis once decided

7. **🟡 SKU Derivation Optimization**
   - Optimize Goods Router joins for performance
   - Create reusable SKU analysis patterns

---

## Recommended Actions

### Immediate (This Week)
- [ ] **Test transaction ID join compatibility** with sample data
- [ ] **Validate session ID infrastructure** supports String type  
- [ ] **Get definitive answer** on user dimension access strategy
- [ ] **Create testing plan** for analytical query compatibility

### Before Launch
- [ ] **Update all analytical query templates** with proper type casting
- [ ] **Implement event sequence validation** monitoring
- [ ] **Prepare user dimension join patterns** if needed
- [ ] **Test end-to-end analytical pipeline** with new schema

### Post-Launch  
- [ ] **Monitor data quality** in production
- [ ] **Optimize join performance** based on actual usage
- [ ] **Follow up on leaderboard implementation** (BI-13)
- [ ] **Document lessons learned** for future feature launches

---

## Conclusion

While the RnD implementation provides enhanced analytical capabilities, **critical data compatibility risks must be addressed before launch**. The transaction ID and session ID type changes pose the highest risk to existing analytical infrastructure. With proper validation and mitigation, these risks can be managed effectively while preserving the analytical benefits of the enhanced schema design.