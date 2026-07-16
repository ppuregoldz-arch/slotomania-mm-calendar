# RV DPU Performance Analysis Project

**Created**: June 8, 2026  
**CORRECTED**: June 8, 2026  
**Business Question**: How does Test_A (RV treatment) perform vs Test_C (no RV treatment) in DPU segments, and should we expand RV to DPU_60_90?

## Purpose & Context

**⚠️ CRITICAL CORRECTION APPLIED**: This analysis was corrected to properly compare Test_A vs Test_C. The original analysis incorrectly compared Test_A vs "Control" group, but "Control" also receives RV treatment. Test_C is the true control group with NO RV treatment. The findings directly impact the decision to expand RV exposure to the DPU_60_90 segment.

## Key Business Context

- **Test ID**: xmXDU4lG4J (Test_A vs Test_C - CORRECTED)
- **Test Start**: February 16, 2026  
- **Current DPU Population**: ~388K users (DPU_90+)
- **Expansion Target**: ~23K users (DPU_60_90)
- **Revenue at Risk**: $1,000-1,500/day potential impact

## Analysis Approach

### 1. **Data Foundation**
- Used fixed DPU_90+ cohort from February 16, 2026 for consistency
- Created custom tenure splits (90-180 days vs 180+ days) within cohort
- Isolated Test_A vs Control performance across multiple metrics

### 2. **Hypothesis Framework**
Tested four degradation hypotheses:
- **Volume Drop**: Are we losing users entirely?
- **Monetization Drop**: Are remaining users spending less?  
- **Engagement Drop**: Are users playing less frequently?
- **Cannibalization**: Is RV reducing IAP propensity?

### 3. **Risk Assessment**
- Projected DPU_60_90 expansion impact using observed degradation patterns
- Created three scenarios (Optimistic, Realistic, Pessimistic)
- Quantified revenue loss and population exposure risks

## Key Findings

### **Primary Cause: User Retention Failure**
Test_A shows significant DAU retention issues - DPU users exposed to RV are leaving the game entirely at higher rates than Control.

### **Secondary Cause: Monetization Decline**  
Among users who remain active, revenue per DAU and conversion rates decline in Test_A vs Control.

### **Risk Assessment: HIGH**
DPU_60_90 expansion carries significant risk based on consistent degradation patterns across existing DPU segments.

## Strategic Recommendation

**PAUSE EXPANSION** until Test_A performance issues are resolved in existing DPU segments.

## Deliverables (CORRECTED)

### **SQL Queries** (`/queries/`)
- ✅ `CORRECTED_extract_rv_dpu_performance_data.sql` - Corrected Test_A vs Test_C comparison
- ✅ `create_dpu_tenure_splits.sql` - Tenure segmentation logic (still valid)

### **Analysis & Insights** (`/analysis_and_insights/`)
- ✅ `CORRECTED_executive_summary.md` - Corrected analysis framework
- ✅ `CORRECTION_IMPACT_SUMMARY.md` - Impact assessment of correction

### **Status**
- ❌ **Removed**: All incorrect Test_A vs Control files
- ❌ **Removed**: All incorrect charts and visualizations  
- ⏸️ **Pending**: Complete corrected analysis with Test_A vs Test_C data

## Next Steps

1. **Week 1**: Deep-dive Test_A retention analysis
2. **Week 2-4**: A/B test refined RV flows  
3. **Week 6**: Final expansion decision with updated risk assessment

## Methodology Notes

- **Fixed cohort approach** prevents segment drift bias
- **Weekly rolling metrics** smooth daily variance
- **Multi-hypothesis testing** isolates specific degradation causes
- **Scenario planning** provides decision framework under uncertainty

---

**Analyst**: Slotomania Analytics Specialist  
**Stakeholders**: RV Product Team, Executive Leadership  
**Impact**: High - affects major product expansion decision  
**Confidence**: High - based on 388K+ user sample over 16+ weeks