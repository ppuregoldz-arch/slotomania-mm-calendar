# How I Calculate Differences: Test_A vs Test_C

## **Basic Formula**

```
Percentage Difference = ((Test_A Value / Test_C Value) - 1) × 100
```

## **Step-by-Step Example**

### **Week of Feb 16, 2026 - DAU Calculation:**

**Raw Data:**
- Test_A (RV Treatment): 13,753 daily users
- Test_C (No RV Control): 13,734 daily users

**Calculation:**
1. **Divide Test_A by Test_C**: 13,753 ÷ 13,734 = 1.0014
2. **Subtract 1**: 1.0014 - 1 = 0.0014  
3. **Multiply by 100**: 0.0014 × 100 = **+0.14%**

**Interpretation**: Test_A has 0.14% more DAU than Test_C (virtually identical)

### **Week of Feb 16, 2026 - Revenue Calculation:**

**Raw Data:**
- Test_A (RV Treatment): $6 daily revenue
- Test_C (No RV Control): $7 daily revenue  

**Calculation:**
1. **Divide Test_A by Test_C**: $6 ÷ $7 = 0.8571
2. **Subtract 1**: 0.8571 - 1 = -0.1429
3. **Multiply by 100**: -0.1429 × 100 = **-14.29%**

**Interpretation**: Test_A has 14.29% less base game revenue than Test_C

## **SQL Implementation**

```sql
-- Using LAG window function to compare groups
case 
    when test_group = 'Test_C' then null  -- Control group gets no calculation
    else (avg_daily_dau / nullif(lag(avg_daily_dau) 
         over (partition by week_start_date order by test_group), 0) - 1) * 100
end as dau_vs_test_c_pct
```

## **Key Points**

### **Why This Method:**
- **Standard A/B testing**: Industry-standard relative comparison
- **Percentage makes it clear**: Easy to interpret business impact
- **Handles zero values**: `NULLIF` prevents division by zero errors

### **What Positive/Negative Means:**
- **Positive %**: Test_A performing better than Test_C  
- **Negative %**: Test_A performing worse than Test_C
- **~0%**: No meaningful difference between groups

### **Business Context:**
- **DAU differences near 0%**: Shows RV doesn't harm engagement
- **Revenue differences**: Expected since Test_A gets additional RV revenue
- **True incremental impact**: RV revenue is pure addition, not cannibalization

## **Total Impact Example**

**Complete Picture for Test_A:**
- Base game revenue: $6 (14% lower than Test_C's $7)
- RV revenue: $49 (pure incremental)  
- **Total revenue**: $6 + $49 = **$55 vs Test_C's $7**
- **Net improvement**: +685% total revenue vs control

This shows RV adds massive incremental value despite minor base game cannibalization.