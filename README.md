# Data Assistant - SM Package

**A unified, comprehensive solution for Slotomania data analysis with protection mechanisms, complexity assessment, and prompt training**

This package provides a generalized data assistant for SM analysis, aligned with cross-studio standards and adapted to SM data structures and business logic.

## Package Purpose

Enable any SM stakeholder to perform rigorous analysis with:
- Unified business insights across roles
- Validation-first workflow and quality gates
- Dual complexity assessment (query + request)
- Prompt training and documentation discipline
- Consolidated SM data context and lineage
- SM-specific critical data rules and validation

## Package Contents

### Core Rules (`.cursor/rules/`)
- `data_assistant_unified.mdc`: Unified assistant with complexity + validation
- `query_validator_advanced.mdc`: SM-focused validation methodology
- `prompt_training_engine.mdc`: Prompt improvement and clarification
- `complexity_assessment_engine.mdc`: Dual complexity evaluation
- `documentation_standards.mdc`: Naming, organization, and output formatting
- `mcp.json`: Optional MCP servers (DB, Confluence, etc.)

### Data Sources (`data_sources/`)
- `sm_complete_data_context.md`: Unified SM data model
- `sm_data_lineage.md`: Table relationships and dependencies
- `sm_business_context.md`: SM business logic and KPIs
- `sm_coin_hyperinflation_context.md`: ⚠️ **CRITICAL** - Normal coin amount ranges (trillions+ are normal)

### Documentation (`documentation/`)
- `sm_unified_metrics_dictionary.md`: Core metrics/KPIs
- `sm_analysis_methodology.md`: Analysis standards and sample queries
- `prompt_improvement_guide.md`: How to write effective requests

### Examples (`examples/`)
- `unified_analysis_examples.md`: 9+ SM-specific analysis examples
- `complexity_assessment_examples.md`: Complexity framework examples
- `prompt_training_examples.md`: Prompt improvement examples

### Templates (`templates/`)
- `analysis_project_template.md`: SM-specific project structure
- `validation_checklist.md`: SM-specific validation requirements

### Prompt Documentation (`prompt_documentation/`)
- `prompt_reflection_guide.md`: How to reflect on and improve prompts
- `prompt_improvement_tracker.md`: Track prompt quality improvements
- `prompt_examples/`: Collection of effective and ineffective prompts

## Key SM Data References

### Primary Sources
- **Revenue Authority**: `agg.agg_sm_daily_users_stats.daily_Net_revenue` ⭐ (AUTHORITATIVE)
- **Detailed Revenue**: `dwh.sm_fact_payments` (use filters: `tran_status_id = 2`, `is_test = 0`, `artificial_ind = 0`)
- **Virtual Currency**: `dwh.sm_fact_virtual_payment_slotobucks` (separate from real money)
- **Slotobucks Flow**: `dwh.sm_fact_internal_purchase_balance_update_slotobucks` (IN/OUT tracking)
- **User Attributes**: `dwh.sm_user_profile_datamining_snapshot` (CZ deluxe segments)
- **Bonus Tracking**: `dwh.fact_sm_bonus_history` with `dwh.dim_sm_bonus_type` (bonus types)
- **Product Mapping**: `sm_draft.SM_DIM_Products` or `dwh.dim_sku_types`
- **Transaction Sources**: `dwh.sm_dim_transaction_source_type` (transaction source types)
- **Machine Analysis**: `dwh.fact_sm_spin_history_kafka` + `dwh.sm_fact_machines_characteristics_data` (machine RTP/payouts)
- **FTD Analysis**: `dwh.v_fact_currency_transactions` (first-time deposit identification)

### Critical Filters
- **Revenue**: `tran_status_id = 2` (approved only - ~96% of transactions are pending/failed)
- **Test Data**: `is_test = 0`, `artificial_ind = 0`
- **Date Exclusion**: Exclude current date for incomplete period analysis

## Critical SM-Specific Rules

### Revenue Calculation Rules
1. **PRIMARY**: Always use `agg.agg_sm_daily_users_stats.daily_Net_revenue` for revenue totals
2. **SECONDARY**: Use `dwh.sm_fact_payments` ONLY with `tran_status_id = 2` filter
3. **WARNING**: Without status filter, revenue is 18-25x inflated (includes pending/failed transactions)
4. **CROSS-VALIDATE**: Always verify fact table results match aggregated table

### Two-Step Aggregation (MANDATORY)
**ALL KPI calculations MUST use two-step aggregation:**
1. **Step 1**: Calculate daily metrics with `GROUP BY calc_date`
2. **Step 2**: Average daily metrics for period comparisons

**Why**: Single-step aggregation severely undercounts users (8-10x error)

### Currency Separation (MANDATORY)
1. **Real Money Revenue**: Actual USD from `dwh.sm_fact_payments.net_amount` (Financial KPI)
2. **Slotobucks Redemption**: Virtual currency from `dwh.sm_fact_virtual_payment_slotobucks.transaction_amount` (Currency Injection Analysis)
3. **NEVER ADD**: Real money + slotobucks (different currencies, different purposes)
4. **Report Separately**: Always show USD revenue and virtual currency redemption as distinct metrics

### Coin Hyperinflation - CRITICAL CONTEXT ⚠️
**SM operates with EXTREME hyperinflation in virtual currency (coins). Coin amounts that would be errors in other games are NORMAL and EXPECTED in SM.**

**Normal Coin Amount Ranges:**
- **Trillions (10^12)**: Common for median values (e.g., median balance ~73-99 trillion)
- **Sextillions (10^21)**: Common for payment quantities (e.g., median payment ~7.6 sextillion)
- **Septillions (10^24)**: Common for P95 percentiles (e.g., P95 balance ~8-10 septillion)
- **Undecillions (10^32)**: Common for maximum values (e.g., max balance ~460 undecillion)

**DO NOT FLAG HIGH COIN AMOUNTS AS ERRORS:**
- ✅ Coin amounts in trillions/sextillions/septillions/octillions/undecillions are **NORMAL**
- ❌ Only flag negative amounts, zero amounts with activity, or logical inconsistencies
- ❌ Do NOT suggest data cleaning for large coin amounts
- ❌ Do NOT question data quality based on coin magnitude alone

**Reference**: See `data_sources/sm_coin_hyperinflation_context.md` for detailed ranges, validation guidelines, and example queries.

## Validation Requirements (SM-specific)

Always validate using source data tables with SM filters:
1. Filter approved transactions only (`tran_status_id = 2`) in revenue queries
2. Cross-validate revenue vs `agg.agg_sm_daily_users_stats`
3. Verify two-step aggregation methodology for all period comparisons
4. Separate real money revenue from virtual currency redemption
5. Document validation users and raw data checks
6. Verify user counts are in hundreds of thousands, not tens of thousands
7. **DO NOT flag high coin amounts as errors** - trillions+ are normal in SM (see hyperinflation context)

## Quick Start

### Step 1: Environment Setup
1. Copy `sm_data_assistant_package/` into your Cursor workspace
2. Verify `.cursor/rules/` are loaded by Cursor
3. Set up environment variables for MCP connectivity (see `.cursor/rules/mcp.json`)
4. Test database connection with a simple query

### Step 2: First Analysis
1. Review `data_sources/sm_complete_data_context.md` for SM data context
2. Review `data_sources/sm_data_context.md` in `sm_context_queries/` for detailed context
3. Use `templates/analysis_project_template.md` to plan your analysis
4. Follow `documentation/sm_analysis_methodology.md` for standards
5. Apply appropriate complexity assessment (🟢🟡🔴⚫)

### Step 3: Validation Workflow
1. Run main analysis query and capture results
2. Select 1-3 validation users for cross-checking
3. Extract raw data for validation
4. Run single-user filtered queries
5. Cross-validate with source tables
6. Verify two-step aggregation methodology
7. Complete validation checklist

### Step 4: Documentation & Delivery
1. Document all validation steps and results
2. Record prompt quality using provided templates
3. Generate business insights and recommendations
4. Share results with stakeholders

## SM-Specific Features

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

## Quality Monitoring

### Data Quality Metrics
- **Completeness**: >95% of expected records present
- **Freshness**: Data updated within SLA requirements
- **Accuracy**: >98% validation pass rate
- **Consistency**: Cross-table validation successful
- **Aggregation Methodology**: 100% two-step aggregation compliance

### Performance Monitoring
- **Query Execution**: <30 seconds for standard queries
- **Resource Usage**: Within acceptable limits
- **Scalability**: Handles expected data volumes
- **Error Rate**: <1% for production queries

### Validation Monitoring
- **Level Coverage**: All required validation levels completed
- **Cross-Table Consistency**: No significant discrepancies
- **Statistical Validation**: Distributions and correlations reasonable
- **Business Logic**: All critical rules validated
- **Two-Step Aggregation**: All period comparisons use correct methodology
- **Currency Separation**: Real money and virtual currency never mixed

### Continuous Improvement
- **Prompt Quality**: Regular assessment and improvement
- **Validation Framework**: Ongoing refinement and updates
- **Documentation**: Continuous updates and improvements
- **Training**: Regular team training and knowledge sharing

## Success Metrics

### Technical Success
- **Data Quality**: >95% validation pass rate
- **Performance**: Query execution within SLA
- **Accuracy**: Business logic validation successful
- **Documentation**: Complete and up-to-date
- **Aggregation Compliance**: 100% two-step aggregation usage

### Business Success
- **Stakeholder Satisfaction**: Requirements fully met
- **Decision Quality**: Insights actionable and valuable
- **ROI**: Positive return on analysis investment
- **Operational Impact**: Process improvements implemented

### Process Success
- **Timeline**: Completed within planned timeframe
- **Validation**: All required checks completed
- **Knowledge Transfer**: Team capabilities enhanced
- **Continuous Improvement**: Lessons learned captured

## Risk Management

### Technical Risks
- **Data Quality Issues**: Implement monitoring and alerting
- **Revenue Inflation**: Always use status filter (`tran_status_id = 2`)
- **Aggregation Errors**: Always use two-step aggregation
- **Currency Confusion**: Always separate real money from virtual currency
- **Performance Bottlenecks**: Regular optimization and testing
- **System Dependencies**: Map and monitor critical dependencies
- **Backup Plans**: Identify alternative approaches and data sources

### Business Risks
- **Stakeholder Expectations**: Regular communication and updates
- **Timeline Risks**: Early identification and mitigation
- **Resource Constraints**: Plan for resource availability
- **Communication Risks**: Clear communication channels and protocols

## Learning Resources

### Getting Started
- `examples/unified_analysis_examples.md` - 9+ comprehensive SM analysis examples
- `templates/` - Project and validation templates
- `documentation/` - Methodology and standards guides
- `data_sources/sm_complete_data_context.md` - Complete SM data context

### Advanced Topics
- `examples/complexity_assessment_examples.md` - Complexity framework
- `examples/prompt_training_examples.md` - Prompt improvement
- `documentation/sm_analysis_methodology.md` - Advanced techniques
- `data_sources/sm_data_lineage.md` - Data relationships and flows

### Best Practices
- Always start with complexity assessment
- Follow validation framework completely
- Use two-step aggregation for all period comparisons
- Always filter revenue with `tran_status_id = 2`
- Separate real money revenue from virtual currency
- Document all steps and decisions
- Continuously improve prompt quality

## Troubleshooting

### Common Issues
- **Connection Problems**: Check environment variables and network
- **Performance Issues**: Review query optimization and indexing
- **Validation Failures**: Check data quality and business logic
- **Revenue Inflation**: Verify `tran_status_id = 2` filter is applied
- **User Count Errors**: Verify two-step aggregation is used
- **Currency Confusion**: Verify real money and virtual currency are separated
- **Complexity Misclassification**: Review assessment criteria

### Support Resources
- Check `DEPLOYMENT_SUMMARY.md` for detailed setup
- Review example files for guidance
- Use validation checklist for quality assurance
- Review `data_sources/sm_complete_data_context.md` for data context
- Contact data team for complex issues

## Critical Warnings

### Revenue Analysis
- ⚠️ **NEVER use** `dwh.sm_fact_payments` without `tran_status_id = 2` filter (18-25x inflated)
- ✅ **ALWAYS use** `agg.agg_sm_daily_users_stats.daily_Net_revenue` as primary source
- ✅ **ALWAYS cross-validate** fact table results with aggregated table

### Aggregation Methodology
- ⚠️ **NEVER use** single-step aggregation for period comparisons (8-10x undercount)
- ✅ **ALWAYS use** two-step aggregation (daily metrics, then average)

### Currency Separation
- ⚠️ **NEVER add** real money revenue + virtual currency redemption
- ✅ **ALWAYS report** real money (USD) and virtual currency separately

### Data Quality
- ⚠️ **Domain Fragmentation**: 85% of SM assets misclassified across domains
- ⚠️ **Stale Profile Data**: `sm.sm_user_profile` often outdated (use snapshot tables)
- ⚠️ **Transaction Status**: 96% of transactions pending/failed (must filter)

---

**Last Updated**: January 2025  
**Package Version**: 1.0  
**Target Audience**: All SM stakeholders  
**Complexity Level**: Intermediate to Advanced  
**Validation Framework**: Required  
**Quality Monitoring**: Active  
**Success Metrics**: Defined and Tracked  
**Status**: ✅ **PRODUCTION READY**

