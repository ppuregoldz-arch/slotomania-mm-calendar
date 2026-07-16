# Data Assistant - SM Package: Deployment Summary

## Overview
The **Data Assistant - SM Package** is a unified, comprehensive solution for Slotomania data analysis that consolidates knowledge from all SM sources with advanced protection mechanisms, complexity assessment, and prompt training capabilities.

## Package Purpose
This package serves as a **generalized data assistant** for any SM stakeholder, providing:
- **Unified business insights** regardless of specific role
- **Advanced protection mechanisms** with mandatory validation flows
- **Sophisticated complexity assessment** including request complexity and token usage
- **Prompt training agenda** to ensure clear, actionable requests
- **Comprehensive data context** from all existing SM sources
- **SM-specific critical rules** for revenue, aggregation, and currency handling

## Key Features

### Advanced Complexity Assessment
Every analysis includes systematic complexity estimation with **dual assessment**:

#### Query Complexity (Traffic Light System)
- **🟢 GREEN (1-2 hours validation)**: Simple aggregations, standard KPIs
- **🟡 YELLOW (0.5-1 day validation)**: Multi-table joins, cohort analysis
- **🔴 RED (1-3 days validation)**: Advanced attribution, complex funnels
- **⚫ BLACK (3+ days validation)**: Experimental frameworks, cross-system validation

#### Request Complexity Assessment
- **📝 SIMPLE**: Single metric, clear scope, < 100 tokens
- **📊 MODERATE**: Multiple metrics, defined timeframe, 100-500 tokens
- **🔍 COMPLEX**: Multi-dimensional analysis, complex logic, 500-1000 tokens
- **🚀 ADVANCED**: Predictive modeling, cross-system analysis, > 1000 tokens

### Documentation Standards
- **Consistent file naming**: Use `sm_` prefix and descriptive names
- **Package organization**: Maintain clear folder structure and organization
- **Output formatting**: Always use tables for structured data and results
- **Business context**: Always explain why metrics and insights matter

### Sophisticated Protection Mechanisms

#### Mandatory Validation Flow
1. **Query Complexity Assessment** - Evaluate joins, calculations, data volume
2. **Request Complexity Assessment** - Analyze clarity, scope, token usage
3. **Prompt Quality Evaluation** - Assess request clarity and specificity
4. **Multi-level Validation** - Source data, business logic, cross-table consistency
5. **Two-Step Aggregation Check** - Verify correct aggregation methodology
6. **Currency Separation Check** - Verify real money vs virtual currency separation
7. **Confidence Assessment** - Systematic reliability scoring with traffic lights

#### Enhanced Validation Framework
- **Raw data validation** with 1-3 specific users
- **Source data cross-validation** with transaction/activity tables
- **Business logic verification** with known benchmarks
- **Two-step aggregation validation** for all period comparisons
- **Currency separation validation** for revenue analysis
- **Edge case testing** for boundary conditions
- **Statistical validation** for large datasets

### Prompt Training Agenda

#### Mandatory Prompt Assessment
Before processing ANY request, evaluate:
- **Clarity**: Is the request specific and unambiguous?
- **Scope**: Are the metrics, timeframe, and segments clearly defined?
- **Complexity**: Is the request appropriately scoped for the user's needs?
- **Actionability**: Will the results drive business decisions?

#### Prompt Improvement Process
1. **Assess current prompt quality** using rubric
2. **Identify improvement areas** (clarity, specificity, scope)
3. **Suggest specific improvements** with examples
4. **Request clarification** if needed before proceeding
5. **Document prompt evolution** for learning

### Unified Business Context
- **Complete data model** from all SM sources
- **Cross-domain insights** (monetization, economy, product, user behavior)
- **Role-agnostic analysis** focused on business value
- **Comprehensive metrics** from all specialized areas

## Package Structure

### Core Rules (`.cursor/rules/`)
- **`data_assistant_unified.mdc`**: Main unified assistant with complexity assessment
- **`query_validator_advanced.mdc`**: Comprehensive validation methodology
- **`prompt_training_engine.mdc`**: Prompt improvement and clarification system
- **`complexity_assessment_engine.mdc`**: Advanced complexity evaluation including request analysis
- **`documentation_standards.mdc`**: Consistent naming, organization, and output formatting
- **`mcp.json`**: Database connection configuration

### Data Sources (`data_sources/`)
- **`sm_complete_data_context.md`**: Unified data model from all SM sources (includes 7+ new critical tables)
- **`sm_data_lineage.md`**: Complete table relationships and dependencies
- **`sm_business_context.md`**: Comprehensive business logic and metrics (includes machine analysis, Slotobucks flow, consumption rates)
- **`sm_coin_hyperinflation_context.md`**: ⚠️ CRITICAL - Normal coin amount ranges (trillions+ are normal)

### Documentation (`documentation/`)
- **`sm_unified_metrics_dictionary.md`**: Complete metrics from all SM sources
- **`sm_analysis_methodology.md`**: Unified analysis standards
- **`prompt_improvement_guide.md`**: How to write effective data requests

### Examples (`examples/`)
- **`unified_analysis_examples.md`**: 14+ cross-domain analysis examples (includes machine RTP, Slotobucks flow, consumption rate, CZ deluxe + recent payer, FTD analysis)
- **`complexity_assessment_examples.md`**: Complexity evaluation examples
- **`prompt_training_examples.md`**: Prompt improvement examples

### Templates (`templates/`)
- **`analysis_project_template.md`**: Unified project structure
- **`validation_checklist.md`**: Comprehensive validation framework

### Prompt Documentation (`prompt_documentation/`)
- **`prompt_reflection_guide.md`**: How to reflect on and improve prompts
- **`prompt_improvement_tracker.md`**: Track prompt quality improvements
- **`prompt_examples/`**: Collection of effective and ineffective prompts

## SM-Specific Features

### Game-Specific Metrics
- **Slot Machine Performance**: Spin activity, bet amounts, win rates, machine-level RTP analysis
- **Machine-Level Analysis**: RTP by machine type, payout analysis, machine performance tracking
- **Virtual Currency Economy**: Coins, gems, slotobucks analysis
- **Slotobucks Flow Analysis**: IN/OUT tracking, event type breakdown, tier-based analysis
- **Balance Management**: Balance distribution, velocity, consumption rates
- **Consumption Rate Analysis**: Total, payment, and bonus consumption rates
- **Bonus Systems**: Bonus tracking, consumption, effectiveness, purchase flag analysis
- **FTD Analysis**: First-time deposit identification and product-level FTD tracking

### Monetization Framework
- **Real Money Revenue**: IAP purchases with virtual coins
- **Virtual Currency Redemption**: Slotobucks redemption analysis
- **Product Performance**: SKU and product group analysis
- **Value-for-Money**: Product value analysis and pricing optimization

### User Segmentation
- **CZ Deluxe Segments**: Engagement-based segmentation (0-5, 5-10, 10-20, etc.)
- **CZ Deluxe + Recent Payer**: Dual segmentation combining engagement level with recent payment activity (14-day window)
- **VIP Tiers**: Tier-based analysis (Tier 1-3, Tier 4+)
- **Paying Status**: Paying vs non-paying users
- **Level-Based Analysis**: New, Mid-Level, Advanced, Expert players

## SM-Specific Data References

### Primary Sources
- **Revenue Authority**: `agg.agg_sm_daily_users_stats.daily_Net_revenue` ⭐ (AUTHORITATIVE)
- **Detailed Revenue**: `dwh.sm_fact_payments` (with `tran_status_id = 2` filter)
- **Virtual Currency**: `dwh.sm_fact_virtual_payment_slotobucks` (separate from real money)
- **Slotobucks Flow**: `dwh.sm_fact_internal_purchase_balance_update_slotobucks` (IN/OUT tracking)
- **User Attributes**: `dwh.sm_user_profile_datamining_snapshot` (CZ deluxe segments)
- **Bonus Tracking**: `dwh.fact_sm_bonus_history` with `dwh.dim_sm_bonus_type` (bonus types)
- **Product Mapping**: `sm_draft.SM_DIM_Products` or `dwh.dim_sku_types`
- **Transaction Sources**: `dwh.sm_dim_transaction_source_type` (transaction source types)
- **Machine Analysis**: `dwh.fact_sm_spin_history_kafka` + `dwh.sm_fact_machines_characteristics_data` (machine RTP/payouts)
- **FTD Analysis**: `dwh.v_fact_currency_transactions` (first-time deposit identification)

### Critical Filters
- **Revenue**: `tran_status_id = 2` (approved only - MANDATORY)
- **Test Data**: `is_test = 0`, `artificial_ind = 0`
- **Date Exclusion**: Exclude current date for incomplete period analysis

## Implementation Guidelines

### Data Validation Standards
- **Revenue validation**: Always use aggregated table as primary source
- **Status filter enforcement**: Always apply `tran_status_id = 2` for payments
- **Two-step aggregation**: Mandatory for all period comparisons
- **Currency separation**: Always separate real money from virtual currency
- **Cross-platform consistency**: Ensure data consistency across platforms

### Business Logic Verification
- **Revenue calculations**: Verify against aggregated table
- **User counts**: Verify in hundreds of thousands, not tens of thousands
- **Aggregation methodology**: Verify two-step aggregation usage
- **Currency handling**: Verify real money and virtual currency separation
- **Monetization flows**: Validate purchase and redemption data

### Performance Optimization
- **Large dataset handling**: Optimize queries for SM's extensive user base
- **Cross-platform analysis**: Efficient multi-platform data aggregation
- **Economy analysis**: Handle complex currency flow data
- **Real-time validation**: Ensure data freshness for live game analysis

## Quality Assurance

### Validation Checklist
- [ ] Query complexity assessed and documented
- [ ] Request clarity evaluated and improved if needed
- [ ] Data sources cross-validated
- [ ] Business logic verified against known benchmarks
- [ ] Two-step aggregation methodology verified
- [ ] Currency separation verified
- [ ] Results formatted consistently with tables
- [ ] Confidence level assigned and explained
- [ ] Prompt quality documented for future reference

### Success Metrics
- **Query Accuracy**: 95%+ validation success rate
- **Prompt Clarity**: 90%+ improvement in request specificity
- **Business Impact**: Clear actionable insights delivered
- **User Satisfaction**: Positive feedback on analysis quality
- **Efficiency**: Reduced time to actionable insights
- **Aggregation Compliance**: 100% two-step aggregation usage

## Deployment Status

### Completed Components
- Core data sources (business context, data lineage, complete data context)
- MCP configuration for SM database connection
- Basic package structure and README
- All rule files customized for SM
- Documentation folder with SM-specific content
- Examples folder with 9+ SM analysis examples
- Templates for standardized SM analysis workflows
- Prompt documentation for training and improvement

### Production Ready
- ✅ Complete package structure matching BB/CC standards
- ✅ All required files present and comprehensive
- ✅ SM data context accurate and complete
- ✅ Query examples validated and documented
- ✅ Rules customized for SM-specific patterns
- ✅ Cross-studio consistency maintained
- ✅ Ready for production deployment

## Next Steps
1. Deploy package to Cursor workspace
2. Verify `.cursor/rules/` are loaded by Cursor
3. Test database connection with sample queries
4. Train team on SM-specific rules and validation requirements
5. Begin using package for SM data analysis
6. Monitor validation compliance and quality metrics
7. Continuously improve based on usage feedback

## Critical SM-Specific Considerations

### Revenue Calculation Rules
1. **PRIMARY**: Always use `agg.agg_sm_daily_users_stats.daily_Net_revenue` for revenue totals
2. **SECONDARY**: Use `dwh.sm_fact_payments` ONLY with `tran_status_id = 2` filter
3. **WARNING**: Without status filter, revenue is 18-25x inflated
4. **CROSS-VALIDATE**: Always verify fact table results match aggregated table

### Two-Step Aggregation (MANDATORY)
**ALL KPI calculations MUST use two-step aggregation:**
1. **Step 1**: Calculate daily metrics with `GROUP BY calc_date`
2. **Step 2**: Average daily metrics for period comparisons

**Why**: Single-step aggregation severely undercounts users (8-10x error)

### Currency Separation (MANDATORY)
1. **Real Money Revenue**: Actual USD from `dwh.sm_fact_payments.net_amount`
2. **Slotobucks Redemption**: Virtual currency from `dwh.sm_fact_virtual_payment_slotobucks.transaction_amount`
3. **NEVER ADD**: Real money + slotobucks (different currencies, different purposes)
4. **Report Separately**: Always show USD revenue and virtual currency redemption as distinct metrics

---

**Package Version**: 1.0  
**Last Updated**: January 2025  
**Target Audience**: All SM stakeholders  
**Complexity Level**: Intermediate to Advanced  
**Validation Framework**: Required  
**Quality Monitoring**: Active  
**Success Metrics**: Defined and Tracked  
**Deployment Status**: ✅ **PRODUCTION READY** - All components complete

