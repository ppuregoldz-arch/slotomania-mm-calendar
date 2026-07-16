# CUPED Analysis Workflow Documentation

## Overview

This document provides a comprehensive step-by-step workflow that was followed to create the complete CUPED (Controlled-experiment Using Pre-Experiment Data) daily average revenue analysis for Test ID: ahhcuJnMV1. The workflow demonstrates the systematic approach from initial requirements gathering through final results documentation.

## Workflow Summary

**Project**: CUPED Daily Average Revenue Analysis  
**Test ID**: ahhcuJnMV1  
**Analysis Period**: May 6-26, 2026  
**Total Duration**: Multi-step collaborative process  
**Final Outcome**: Complete CUPED analysis with comprehensive documentation

---

## Phase 1: Project Setup and Requirements Gathering

### Step 1.1: Project Structure Creation
**Action**: Created organized folder structure for the analysis
**Output**: Complete topic folder structure
```
outputs/cuped_daily_avg_revenue_analysis_2026-05-28/
├── topic/
├── queries/
├── tableau_workbooks/
├── files/
└── analysis_and_insights/
```
**Purpose**: Establish systematic organization following workspace documentation standards

### Step 1.2: Requirements Documentation
**Action**: Captured test configuration and requirements
**Input Provided**:
- Test ID: ahhcuJnMV1
- Start date (Promo date): 20.05.2026
- End date (Promo date): 26.05.2026 (including)
- Before period: 14 days
- Population: "During" users only (active during test period)

**Output**: `required_information.md`
**Content**: Complete test configuration, population definition, CUPED methodology requirements, expected deliverables

---

## Phase 2: SQL Query Development

### Step 2.1: Base Data Query Creation
**File**: `01_cuped_daily_avg_revenue_base_data.sql`
**Purpose**: Calculate individual user metrics and deviations
**Key Components**:
- User-level average revenue (before/during periods)
- Overall population averages
- Individual deviations from population means
- A/B test group assignments
- "During users" filtering

**Technical Challenges Resolved**:
- Correct A/B test table joins (`sm_ds.abtest_user_allocations` + `abtest_dim_group`)
- Revenue column identification (`gross_rev` not `daily_Net_revenue`)
- Proper date filtering for 2026 data

### Step 2.2: Covariance and Theta Calculation
**File**: `02_cuped_covariance_calculation.sql`
**Purpose**: Calculate statistical parameters for CUPED adjustment
**Key Calculations**:
- Sample covariance between before/during deviations
- Variance of pre-experiment period
- CUPED theta coefficient (θ = COV(Y,X) / VAR(X))
- Pearson correlation coefficient
- Pooled calculation across all users (not per group)

**Design Decision**: Calculate theta using all users together for stable CUPED adjustment factor

### Step 2.3: Y-CUPED Calculation
**File**: `03_Y_cuped.sql`
**Purpose**: Apply CUPED adjustment to create variance-reduced metrics
**Key Formula**: `Y_CUPED = Y - θ × (X - X̄)`
**Components**:
- Original experiment metrics
- CUPED-adjusted metrics
- Theta coefficient application
- Variance reduction validation

### Step 2.4: Statistical Analysis and Differences
**File**: `04_diff_calculation.sql`
**Purpose**: Calculate treatment effects and statistical measures
**Enhanced Features**:
- Group-level aggregations (Test vs Control)
- Treatment effects (difference-in-differences)
- Standard errors for confidence intervals
- Variance calculations for CUPED effectiveness assessment
- Sample sizes per group

**Iterative Improvements**:
- Added variance and standard error calculations
- Resolved Vertica-specific SQL syntax issues
- Enhanced statistical validation framework

---

## Phase 3: Documentation and Knowledge Management

### Step 3.1: Variables and Methodology Documentation
**File**: `variables_explanations.md`
**Purpose**: Comprehensive reference for all CUPED variables and statistical measures
**Sections Created**:
- Core CUPED Variables (deviations, averages, Y_CUPED)
- Statistical Measures (covariance, theta, correlation)
- Treatment Effect Analysis (group comparisons, confidence intervals)
- Usage Pipeline and Validation Requirements

**Evolution**: Document expanded through iterative additions as new statistical measures were implemented

### Step 3.2: Analysis Template Creation
**File**: `cuped_analysis_results_template.md`
**Purpose**: Reusable template for future CUPED analyses
**Structure**: 
- Test Configuration → Key Findings → Summary Results → Detailed Analysis
- Placeholder system for easy population with new test data
- Standardized reporting format

---

## Phase 4: Query Execution and Data Validation

### Step 4.1: MCP Vertica Integration
**Tool**: `user-mcp-alchemy-sm` MCP server
**Process**: 
1. Verified MCP tool availability and schema
2. Executed queries against `playtika_dwh` database
3. Handled SQL syntax differences (Vertica-specific functions)
4. Iterative query refinement based on execution results

### Step 4.2: Data Collection
**Query Execution Sequence**:
1. **Query 02**: Covariance calculation → θ=0.7880, r=0.7614
2. **Query 04**: Group statistics → Sample sizes, treatment effects, variances
3. **Variance Analysis**: Standard errors and confidence intervals

**Date Correction**: Initially executed with 2024 dates, corrected to 2026 dates and re-executed for accuracy

### Step 4.3: Results Validation
**Key Findings Discovered**:
- Strong correlation (r=0.76) suggesting good CUPED potential
- Actual 189% variance increase (CUPED failure)
- No significant treatment effects in either method
- Regular analysis outperformed CUPED in precision

---

## Phase 5: Results Analysis and Documentation

### Step 5.1: Statistical Calculations
**Manual Calculations Performed**:
- Treatment effects (difference-in-differences): Regular (-$0.0163), CUPED (-$0.0413)
- Standard errors: Regular (0.0349), CUPED (0.0591)
- 95% Confidence intervals: Regular (-0.0847, +0.0521), CUPED (-0.1571, +0.0745)
- Variance reduction assessment: -189% (failure indicator)

### Step 5.2: Final Results Documentation
**File**: `cuped_analysis_results_ahhcuJnMV1.md`
**Structure Evolution**:
- **Initial**: Standard academic format
- **Final**: Executive summary format (Test Config → Key Findings → Summary Table → Details)

**Critical Analysis**:
- CUPED methodology unsuccessful despite strong correlation
- Investigation recommendations for implementation review
- Business impact assessment (no significant treatment effect)

---

## Phase 6: Workflow Documentation

### Step 6.1: Comprehensive Workflow Creation
**File**: `cuped_analysis_workflow.md` (this document)
**Purpose**: Document the complete methodology for future reference and reproducibility

---

## Key Technical Decisions Made

### 1. **Population Definition**
- **Decision**: Use "during users" only (active during experiment period)
- **Rationale**: Ensure analysis focuses on engaged users who could be affected by treatment

### 2. **Theta Calculation Approach**  
- **Decision**: Pool all users together for theta calculation
- **Rationale**: CUPED theory assumes stable relationship across groups; pooling provides more stable estimate

### 3. **SQL Implementation Strategy**
- **Decision**: Build modular queries with progressive complexity
- **Rationale**: Enable validation at each step and facilitate debugging

### 4. **Documentation Philosophy**
- **Decision**: Create both template and specific analysis files
- **Rationale**: Enable reusability while preserving specific analysis context

### 5. **Date Correction Protocol**
- **Decision**: Re-execute all queries when date error discovered
- **Rationale**: Ensure data integrity and accurate business context

---

## Lessons Learned

### 1. **CUPED Implementation Challenges**
- Strong correlation doesn't guarantee CUPED success
- Implementation verification is critical when results contradict theory
- Variance reduction validation should be built into the analysis

### 2. **Collaborative Analysis Process**
- Step-by-step approval process ensures accuracy and alignment
- Iterative query development allows for refinement and error correction
- Documentation alongside development prevents knowledge loss

### 3. **Technical Implementation**
- MCP integration enables direct database execution and validation
- SQL syntax differences require platform-specific adjustments
- Query modularization facilitates debugging and validation

### 4. **Business Communication**
- Executive summary format improves stakeholder communication
- Clear success/failure indicators enable quick decision making
- Investigation recommendations provide actionable next steps

---

## Reproducibility Guidelines

To reproduce this analysis for a different test:

### 1. **Setup Phase**
- Create topic folder structure using workspace standards
- Document test configuration in `required_information.md`

### 2. **Query Development**
- Adapt SQL queries for new test ID and date ranges
- Validate A/B test table joins for specific test structure
- Test queries incrementally (base data → covariance → Y-CUPED → differences)

### 3. **Execution Phase**
- Execute via MCP Vertica connection
- Validate data at each step before proceeding
- Handle any SQL syntax or data quality issues

### 4. **Documentation Phase**
- Use template for consistent reporting structure
- Calculate confidence intervals and treatment effects manually
- Provide investigation recommendations for unexpected results

### 5. **Quality Assurance**
- Verify CUPED assumptions (correlation strength, variance reduction)
- Validate treatment effect calculations using difference-in-differences
- Review business interpretation and statistical significance

---

## File Deliverables Summary

| File | Purpose | Status | Lines |
|------|---------|--------|-------|
| `required_information.md` | Test configuration and requirements | ✅ Complete | 45 |
| `01_cuped_daily_avg_revenue_base_data.sql` | Base user metrics and deviations | ✅ Complete | 105 |
| `02_cuped_covariance_calculation.sql` | Theta and correlation calculations | ✅ Complete | 134 |
| `03_Y_cuped.sql` | CUPED-adjusted metrics | ✅ Complete | 140 |
| `04_diff_calculation.sql` | Treatment effects and statistics | ✅ Complete | 248 |
| `variables_explanations.md` | Methodology documentation | ✅ Complete | 303 |
| `cuped_analysis_results_template.md` | Reusable template | ✅ Complete | 90 |
| `cuped_analysis_results_ahhcuJnMV1.md` | Final analysis results | ✅ Complete | 126 |
| `cuped_analysis_workflow.md` | This workflow document | ✅ Complete | - |

**Total Project Artifacts**: 9 files  
**Total Lines of Code/Documentation**: 1,191+ lines  
**Analysis Outcome**: CUPED methodology unsuccessful for this test case

---

*Workflow documented on: May 28, 2026*  
*Project Status: Complete with Investigation Recommendations*  
*Methodology: Collaborative Step-by-Step CUPED Implementation*