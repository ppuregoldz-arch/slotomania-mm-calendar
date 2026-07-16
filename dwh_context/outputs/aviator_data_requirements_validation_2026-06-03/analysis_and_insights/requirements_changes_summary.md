# Aviator Data Requirements - Changes Summary Analysis

## Executive Summary

The RnD implementation significantly expands and modifies the original BA data requirements. Key changes include **event expansion** (4 → 6 events), **topic renaming**, **data type modifications**, and **field additions/removals**. While most analytical capabilities are preserved, several areas require attention for data quality and analytical completeness.

---

## 1. Major Schema Changes

### 1.1 Topic and Event Structure Changes

| Change Type | Original (BA) | Implementation (RnD) | Impact |
|-------------|---------------|----------------------|---------|
| **Topic Name** | `aviator_user_progress` | `aviator_user_history` | ⚠️ **Medium** - Naming convention change, requires pipeline updates |
| **Event Count** | 4 events | 6 events | ⚠️ **High** - Expanded event granularity, improved tracking |
| **Event Types** | `purchase`, `round_started`, `round_ended`, `user_rewarded` | `FROZEN`, `READY_TO_PLAY`, `OFFER_DECLINED`, `ROUND_STARTED`, `ROUND_ENDED`, `USER_REWARDED` | ⚠️ **High** - Better state tracking, requires consumer updates |

### 1.2 Event Mapping Changes

| Original Event | RnD Events | Business Logic Change |
|----------------|------------|----------------------|
| `purchase` | `FROZEN` + `READY_TO_PLAY` | **Split into two phases**: Configuration freeze vs. gameplay readiness |
| `round_started` | `ROUND_STARTED` | ✅ **Direct mapping** - No change |
| `round_ended` | `ROUND_ENDED` | ✅ **Enhanced** - Now includes `gameResult` on final round |
| `user_rewarded` | `USER_REWARDED` | ✅ **Direct mapping** - Captures actual delivery vs computed |
| *New Event* | `OFFER_DECLINED` | 🆕 **Added** - Tracks paid offer declines (REST endpoint) |

---

## 2. Data Type and Field Changes

### 2.1 Critical Data Type Modifications

| Field | Original Type | New Type | Risk Assessment |
|-------|---------------|----------|-----------------|
| `session_id` | `integer` | `String` | 🟡 **Medium Risk** - Join compatibility with existing tables |
| `segment_id` | `varchar` | `Long` | 🟡 **Medium Risk** - Type mismatch in segment joins |
| `transaction_id` | `integer` | `String` (nullable) | 🔴 **High Risk** - Payment table join compatibility |
| `origin_transaction_id` | `integer` | `String` | 🔴 **High Risk** - Payment table join compatibility |
| `base_amount` | `double precision` | `BigDecimal` | 🟢 **Low Risk** - Better precision for financial data |
| `final_reward` | `double precision` | `BigDecimal` | 🟢 **Low Risk** - Better precision for financial data |

### 2.2 Field Population Changes

| Field | Original Events | New Events | Impact |
|-------|-----------------|------------|---------|
| `round_num` | All events (1-4) | Events 4,5 only | ⚠️ **Medium** - Requires joins for complete round tracking |
| `base_amount` | Event 4 only | Event 1 only | ⚠️ **Medium** - Earlier availability, requires join for event 4 |
| `total_rounds_count` | Events 2,3,4 | Events 1,4,5 | 🟢 **Low** - Better coverage including freeze event |

---

## 3. Removed and Missing Fields Analysis

### 3.1 Fields Removed from Streaming Events

| Removed Field | Original Purpose | RnD Resolution | Risk Level |
|---------------|------------------|----------------|------------|
| `tier_id` | User tier tracking | ❓ **BI-side handling or separate enhancement** | 🟡 **Medium** - May impact segmentation analysis |
| `prestige_level` | User progression | ❓ **BI-side handling or separate enhancement** | 🟡 **Medium** - May impact player lifecycle analysis |
| `current_parameter_value` | Configuration tracking | ❓ **Out of service scope** | 🟡 **Medium** - Limits configuration analysis |
| `SKU_id` | Product tracking | 🔄 **Derivable via `aviatorTransactionId` + Goods Router join** | 🟢 **Low** - Alternative access method available |

### 3.2 Deferred Implementation Fields

| Field | Status | Business Impact |
|-------|--------|-----------------|
| `max_leaderboard_value` | 🟡 **Pending BI-13 decision** | Limits competitive analysis capabilities |
| `min_leaderboard_value` | 🟡 **Pending BI-13 decision** | Limits competitive analysis capabilities |
| `rewardId` (cross-topic linkage) | 🟡 **Deferred - BI-12** | May complicate bonus tracking across systems |

---

## 4. New Fields and Enhancements

### 4.1 Analytical Value-Add Fields

| New Field | Type | Events | Analytical Value |
|-----------|------|--------|------------------|
| `eventType` | Enum | 1-6 | **High** - Event routing and consumer logic |
| `configId` | String | 1-6 | **High** - Configuration catalog joins for analytics |
| `historyReason` | Enum (5 values) | 5 | **Medium** - Detailed round outcome classification |
| `entryPath` | Enum | 1 | **High** - PAID vs BONUS funnel analysis |
| `bonusGameSequenceIdx` | int | 1 | **Medium** - BOGO chain analytics |
| `parentGameId` | String | 1 | **Medium** - BOGO traceability |
| `durationMs` | Long | 5 | **High** - Precise timing analysis (vs ETL-only in original) |
| `growthFormula` | Complex Object | 1,4,5 | **High** - Replaces separate config fields with structured snapshot |

### 4.2 Enhanced Game Result Tracking

| Field | Description | Analytical Impact |
|-------|-------------|-------------------|
| `gameResult.bundleIds` | Threshold bundles awarded | **High** - Milestone achievement tracking |
| `gameResult.appliedOnTopMultiplier` | Promotional multiplier | **High** - Promo effectiveness measurement |
| `gameResult.winningRoundIdx` | Best-performing round | **Medium** - Multi-round strategy analysis |

---

## 5. Data Quality Risk Assessment

### 5.1 High-Risk Areas

#### **Transaction ID Compatibility** 🔴
- **Risk**: Type change from `integer` to `String` may break existing payment joins
- **Affected Tables**: `dwh.sm_fact_payments`, revenue analysis queries
- **Mitigation**: Validate join compatibility, may require casting in analytical queries

#### **Session ID Type Change** 🔴  
- **Risk**: String vs integer mismatch with existing session tracking
- **Affected Analysis**: Session-based engagement metrics, user journey analysis
- **Mitigation**: Confirm compatibility with session dimension tables

#### **Missing User Dimensions** 🟡
- **Risk**: `tier_id` and `prestige_level` not in streaming events
- **Impact**: Limited user segmentation capabilities in real-time analysis
- **Mitigation**: Requires joins with user profile tables or separate enhancement

### 5.2 Medium-Risk Areas

#### **Round Number Population** 🟡
- **Risk**: `roundIdx` only populated on events 4,5 instead of all events
- **Impact**: Requires joins to get round context for purchase/reward events
- **Mitigation**: Derivable via `gameId` joins but adds query complexity

#### **Leaderboard Data Deferral** 🟡
- **Risk**: Competitive analysis capabilities limited without min/max leaderboard values
- **Impact**: Cannot analyze competitive pressure effects in real-time
- **Mitigation**: Pending BI-13 resolution for implementation approach

### 5.3 Low-Risk Areas

#### **Enhanced Precision** 🟢
- **Benefit**: `BigDecimal` types for financial fields improve accuracy
- **Impact**: Better precision for revenue calculations
- **Action**: Update analytical queries to handle BigDecimal formatting

#### **Expanded Event Granularity** 🟢
- **Benefit**: More detailed state transition tracking
- **Impact**: Better funnel analysis and debugging capabilities
- **Action**: Update event consumers to handle expanded event types

---

## 6. Analytical Capability Assessment

### 6.1 Core Business Questions Coverage

| Business Question | Original Capability | New Capability | Status |
|-------------------|-------------------|----------------|--------|
| **Conversion rate analysis** | ✅ Full | ✅ **Enhanced** | 🟢 Better with entry path tracking |
| **ARPPU measurement** | ✅ Full | ✅ **Enhanced** | 🟢 Better precision with BigDecimal |
| **Player timing behavior** | ✅ Full | ✅ **Enhanced** | 🟢 More granular with durationMs |
| **Configuration optimization** | ✅ Full | ✅ **Enhanced** | 🟢 Better with growthFormula snapshots |
| **Segment performance** | ⚠️ Limited | ⚠️ **Same limitations** | 🟡 Still missing tier/prestige in streams |
| **Competitive analysis** | ✅ Planned | ❓ **Deferred** | 🟡 Pending leaderboard implementation |

### 6.2 New Analytical Opportunities

| Capability | Enabled By | Business Value |
|------------|------------|----------------|
| **Offer decline analysis** | `OFFER_DECLINED` event | Track paid offer rejection rates |
| **BOGO chain analytics** | `bonusGameSequenceIdx` + `parentGameId` | Measure bonus game effectiveness |
| **Configuration impact tracking** | `configId` + `growthFormula` | Live A/B testing of economy parameters |
| **Detailed outcome classification** | `historyReason` enum | Better understanding of player behavior patterns |
| **Promotional effectiveness** | `appliedOnTopMultiplier` + `bundleIds` | Measure promo impact on engagement |

---

## 7. Recommendations

### 7.1 Immediate Actions Required

1. **🔴 Validate Transaction ID Joins**
   - Test compatibility between new String transaction IDs and existing payment tables
   - Update analytical queries with appropriate casting if needed
   - Document any performance implications

2. **🔴 Session ID Compatibility Check**  
   - Verify String session IDs work with existing session tracking infrastructure
   - Update dimensional models if necessary

3. **🟡 Plan User Dimension Strategy**
   - Clarify how `tier_id` and `prestige_level` will be obtained for analysis
   - Document required joins or request separate enhancement

4. **🟡 Leaderboard Implementation Decision**
   - Finalize BI-13 decision on leaderboard field implementation
   - Plan analytical workarounds if deferred

### 7.2 Analytical Preparation

1. **Update Query Templates**
   - Modify standard Aviator analysis queries for new event structure
   - Create reusable patterns for the 6-event model

2. **Documentation Updates** 
   - Update analytical context with final schema
   - Create field mapping guide for analysts

3. **Dashboard Preparation**
   - Plan dashboard updates for enhanced tracking capabilities
   - Design visualizations for new analytical dimensions

### 7.3 Launch Readiness Validation

1. **End-to-End Testing**
   - Validate complete event flow from purchase to reward
   - Test analytical queries against sample data

2. **Business Question Verification**
   - Confirm all core KPIs can be calculated with new schema
   - Document any analytical limitations

3. **Stakeholder Alignment**
   - Final BI sign-off on schema changes
   - RnD confirmation of implementation timeline

---

## 8. Conclusion

The RnD implementation significantly **enhances** the original BA requirements with better granularity, precision, and analytical capabilities. While some **data quality risks** exist around transaction ID compatibility and missing user dimensions, the overall changes **improve analytical capabilities** for Aviator feature measurement.

**Key Success Factors:**
- ✅ Enhanced event granularity provides better funnel analysis
- ✅ New fields enable previously impossible analytical insights  
- ✅ Better financial precision with BigDecimal types
- ⚠️ Need to address transaction ID and session compatibility
- ⚠️ Plan for user dimension access strategy

**Recommendation**: **Proceed with implementation** after addressing transaction ID compatibility and finalizing user dimension strategy. The enhanced schema provides superior analytical capabilities despite the identified risks.