# Vertica SQL Compatibility Guide - SM Package

**Purpose**: Ensure all SQL queries in the SM package are Vertica-compatible to prevent syntax errors and ensure reliable query execution.

**Last Updated**: November 2025  
**Target Database**: Vertica Analytics Platform

---

## Introduction

This guide provides Vertica-specific SQL syntax rules and patterns for SM data analysis. All queries in the SM package must follow these guidelines to ensure compatibility with Vertica.

### Key Principles

1. **Use Vertica-compatible syntax** for all SQL queries
2. **Test queries** in Vertica environment before production use
3. **Preserve business logic** when converting syntax
4. **Document syntax changes** for future reference

---

## Critical Syntax Differences

### Type Casting

**PostgreSQL/Generic SQL**:
```sql
value::float
value::integer
value::DATE
value::TIMESTAMP
```

**Vertica-Compatible**:
```sql
CAST(value AS FLOAT)
CAST(value AS INTEGER)
CAST(value AS DATE)
CAST(value AS TIMESTAMP)
```

**Example Conversion**:
```sql
-- ❌ WRONG (PostgreSQL syntax)
ROUND((null_user_ids::float / total_records::float) * 100, 2)

-- ✅ CORRECT (Vertica syntax)
ROUND((CAST(null_user_ids AS FLOAT) / CAST(total_records AS FLOAT)) * 100, 2)
```

---

## Window Functions

### MEDIAN() Window Function

**Issue**: Vertica does not support `MEDIAN()` as a window function.

**PostgreSQL/Generic SQL**:
```sql
MEDIAN(column_name) OVER (PARTITION BY partition_col)
```

**Vertica-Compatible**:
```sql
PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY column_name) OVER (PARTITION BY partition_col)
```

**Example Conversion**:
```sql
-- ❌ WRONG (Not supported in Vertica)
MEDIAN(bet_coins) OVER (PARTITION BY calc_date, is_pu)

-- ✅ CORRECT (Vertica syntax)
PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY bet_coins) OVER (PARTITION BY calc_date, is_pu)
```

**Note**: `PERCENTILE_CONT(0.5)` calculates the median (50th percentile) using continuous interpolation.

### PERCENTILE_DISC with Window Functions

**Issue**: Cannot mix `WITHIN GROUP` (aggregate syntax) with `OVER` (window syntax) in the same expression in Vertica.

**PostgreSQL/Generic SQL** (INCORRECT - doesn't work in Vertica):
```sql
PERCENTILE_DISC(0.75) WITHIN GROUP (ORDER BY bet_coins) OVER (PARTITION BY calc_date)
```

**Vertica-Compatible Solution**: Use a subquery/CTE approach

**Option 1: Subquery with Aggregate First**:
```sql
-- Step 1: Calculate percentiles in subquery
WITH percentile_calc AS (
    SELECT 
        calc_date,
        is_pu,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY bet_coins) as p75_bet_coins
    FROM (
        SELECT 
            calc_date,
            CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END as is_pu,
            bet_coins
        FROM agg.agg_sm_daily_users_stats a
        LEFT JOIN dwh.sm_fact_payments x
            ON a.user_id = x.user_id
            AND x.tran_date BETWEEN a.calc_date - 14 AND a.calc_date
    ) sub
    GROUP BY calc_date, is_pu
)
-- Step 2: Join back to original data
SELECT 
    a.calc_date,
    a.is_pu,
    p.p75_bet_coins
FROM agg.agg_sm_daily_users_stats a
LEFT JOIN percentile_calc p
    ON a.calc_date = p.calc_date
    AND a.is_pu = p.is_pu
```

**Option 2: Window Function with PERCENTILE_CONT** (Simpler for window context):
```sql
-- ✅ CORRECT: Use PERCENTILE_CONT as window function
PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY bet_coins) OVER (PARTITION BY calc_date, is_pu)
```

**Note**: `PERCENTILE_CONT` works as both aggregate and window function in Vertica. Use `PERCENTILE_DISC` only when you need discrete percentiles (actual values from dataset).

### PERCENTILE_CONT vs PERCENTILE_DISC

- **PERCENTILE_CONT**: Continuous interpolation (may return values not in dataset)
- **PERCENTILE_DISC**: Discrete percentile (returns actual values from dataset)

**For SM Analysis**: Use `PERCENTILE_CONT` for most cases (medians, quartiles) unless you specifically need discrete values.

---

## Date Functions

### DATEDIFF Function

**PostgreSQL/Generic SQL**:
```sql
DATEDIFF('dd', date1, date2)  -- 'dd' for days
DATEDIFF('mm', date1, date2)  -- 'mm' for months
```

**Vertica-Compatible**:
```sql
DATEDIFF('day', date1, date2)   -- 'day' for days
DATEDIFF('month', date1, date2) -- 'month' for months
```

**Example Conversion**:
```sql
-- ❌ WRONG (PostgreSQL syntax)
DATEDIFF('dd', last_login_date, date) as days_from_login

-- ✅ CORRECT (Vertica syntax)
DATEDIFF('day', last_login_date, date) as days_from_login
```

**Common DATEDIFF Units in Vertica**:
- `'day'` or `'dd'` - Days (both work, but 'day' is preferred)
- `'month'` or `'mm'` - Months
- `'year'` or `'yy'` - Years
- `'hour'` - Hours
- `'minute'` - Minutes

### DATE_TRUNC Function

**Status**: ✅ Supported in Vertica with same syntax

```sql
DATE_TRUNC('month', calc_date)
DATE_TRUNC('year', calc_date)
DATE_TRUNC('day', timestamp_col)
```

**No conversion needed** - works the same in Vertica.

### CURRENT_DATE and Date Arithmetic

**Status**: ✅ Supported in Vertica

```sql
CURRENT_DATE
CURRENT_DATE - 1
CURRENT_DATE - INTERVAL '30 days'
```

**No conversion needed** - works the same in Vertica.

---

## Common Query Patterns

### Pattern 1: Median Calculation with Window Function

**Use Case**: Calculate median bet coins by date and paying user flag

```sql
-- ✅ CORRECT Vertica Pattern
SELECT DISTINCT
    calc_date,
    CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END as is_pu,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY bet_coins) 
        OVER (PARTITION BY calc_date, CASE WHEN x.user_id IS NOT NULL THEN 1 ELSE 0 END) as median_wager
FROM agg.agg_sm_daily_users_stats a
LEFT JOIN dwh.sm_fact_payments x
    ON a.user_id = x.user_id
    AND x.tran_date BETWEEN a.calc_date - 14 AND a.calc_date
WHERE calc_date >= CURRENT_DATE - 30;
```

### Pattern 2: Multiple Percentiles with Window Functions

**Use Case**: Calculate multiple percentiles (25th, 50th, 75th, 95th) for balance distribution

```sql
-- ✅ CORRECT Vertica Pattern
SELECT DISTINCT
    calc_date,
    CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END as is_pu,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY balance_end_day) 
        OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS balance_p25,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance_end_day) 
        OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS balance_p50,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY balance_end_day) 
        OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS balance_p75,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY balance_end_day) 
        OVER (PARTITION BY calc_date, CASE WHEN b.user_id IS NOT NULL THEN 1 ELSE 0 END) AS balance_p95
FROM agg.agg_sm_daily_users_stats a
LEFT JOIN dwh.sm_fact_payments b
    ON a.user_id = b.user_id
    AND b.tran_date BETWEEN a.calc_date - 14 AND a.calc_date
WHERE calc_date >= CURRENT_DATE - 365;
```

### Pattern 3: Type Casting in Calculations

**Use Case**: Calculate percentage of null values

```sql
-- ✅ CORRECT Vertica Pattern
SELECT 
    calc_date,
    total_records,
    ROUND((CAST(null_user_ids AS FLOAT) / CAST(total_records AS FLOAT)) * 100, 2) AS null_user_id_pct,
    ROUND((CAST(null_revenue AS FLOAT) / CAST(total_records AS FLOAT)) * 100, 2) AS null_revenue_pct
FROM (
    SELECT 
        calc_date,
        COUNT(*) AS total_records,
        COUNT(CASE WHEN user_id IS NULL THEN 1 END) AS null_user_ids,
        COUNT(CASE WHEN daily_Net_revenue IS NULL THEN 1 END) AS null_revenue
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date >= CURRENT_DATE - 7
    GROUP BY calc_date
) sub;
```

### Pattern 4: Date Difference Calculation

**Use Case**: Calculate days since last login for churn analysis

```sql
-- ✅ CORRECT Vertica Pattern
SELECT 
    user_id,
    date,
    last_login_date,
    DATEDIFF('day', last_login_date, date) as days_from_login
FROM (
    SELECT
        user_id,
        date,
        MAX(calc_date) as last_login_date
    FROM agg.agg_sm_daily_users_stats
    WHERE calc_date < date
    GROUP BY user_id, date
) sub;
```

---

## Quick Reference Table

| PostgreSQL/Generic | Vertica-Compatible | Notes |
|-------------------|-------------------|-------|
| `value::float` | `CAST(value AS FLOAT)` | Type casting |
| `value::integer` | `CAST(value AS INTEGER)` | Type casting |
| `value::DATE` | `CAST(value AS DATE)` | Type casting |
| `MEDIAN(col) OVER (...)` | `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY col) OVER (...)` | Median calculation |
| `PERCENTILE_DISC(p) WITHIN GROUP (...) OVER (...)` | Use subquery or `PERCENTILE_CONT(p) WITHIN GROUP (...) OVER (...)` | Cannot mix aggregate + window |
| `DATEDIFF('dd', ...)` | `DATEDIFF('day', ...)` | Date difference |
| `DATE_TRUNC(...)` | `DATE_TRUNC(...)` | ✅ Same syntax |
| `CURRENT_DATE` | `CURRENT_DATE` | ✅ Same syntax |

---

## Migration Checklist

When converting queries to Vertica-compatible syntax:

- [ ] **Type Casting**: Replace all `::` casting with `CAST(... AS ...)`
- [ ] **MEDIAN()**: Replace `MEDIAN()` window functions with `PERCENTILE_CONT(0.5)`
- [ ] **PERCENTILE_DISC OVER**: Convert to subquery or use `PERCENTILE_CONT`
- [ ] **DATEDIFF**: Change `'dd'` to `'day'` (or verify unit syntax)
- [ ] **Test Query**: Execute in Vertica to verify syntax
- [ ] **Validate Results**: Ensure results match expected business logic
- [ ] **Preserve Filters**: Ensure SM-specific filters remain intact:
  - `tran_status_id = 2` for revenue queries
  - Two-step aggregation for period comparisons
  - Currency separation (real money vs virtual currency)

---

## SM-Specific Considerations

### Preserve Critical SM Patterns

When converting syntax, **DO NOT** change:

1. **Revenue Filters**: Always keep `tran_status_id = 2` filter
2. **Two-Step Aggregation**: Maintain two-step aggregation methodology
3. **Currency Separation**: Keep real money and virtual currency separate
4. **Date Exclusions**: Maintain current date exclusion logic
5. **Test User Exclusions**: Preserve test user filtering

### Example: Converting Complex Query

**Original Query** (with incompatible syntax):
```sql
SELECT 
    calc_date,
    MEDIAN(bet_coins) OVER (PARTITION BY calc_date) as median_bet,
    PERCENTILE_DISC(0.75) WITHIN GROUP (ORDER BY bet_coins) OVER (PARTITION BY calc_date) as p75_bet,
    (null_count::float / total_count::float) * 100 as null_pct
FROM agg.agg_sm_daily_users_stats
WHERE calc_date >= CURRENT_DATE - 30;
```

**Vertica-Compatible Query**:
```sql
SELECT 
    calc_date,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY bet_coins) OVER (PARTITION BY calc_date) as median_bet,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY bet_coins) OVER (PARTITION BY calc_date) as p75_bet,
    (CAST(null_count AS FLOAT) / CAST(total_count AS FLOAT)) * 100 as null_pct
FROM agg.agg_sm_daily_users_stats
WHERE calc_date >= CURRENT_DATE - 30;
```

---

## Testing and Validation

### Before Using in Production

1. **Syntax Check**: Verify query parses without errors
2. **Result Validation**: Compare results with known benchmarks
3. **Performance Check**: Ensure query performance is acceptable
4. **Business Logic**: Verify SM-specific business rules are preserved

### Common Error Messages

**Error**: `Syntax error at or near "::"`  
**Solution**: Replace `::` with `CAST(... AS ...)`

**Error**: `Function MEDIAN does not exist`  
**Solution**: Use `PERCENTILE_CONT(0.5)` instead

**Error**: `Cannot use aggregate function with window function`  
**Solution**: Use subquery approach or `PERCENTILE_CONT` as window function

**Error**: `Invalid date part 'dd'`  
**Solution**: Use `'day'` instead of `'dd'` in DATEDIFF

---

## Additional Resources

- **Vertica SQL Reference**: [docs.vertica.com](https://docs.vertica.com/)
- **Window Functions**: See Vertica documentation on analytical functions
- **Date Functions**: See Vertica date/time function reference

---

## Version History

- **November 2025**: Initial version created for SM package compatibility

---

**Note**: This guide focuses on SM package-specific patterns. For general Vertica SQL syntax, refer to official Vertica documentation.

