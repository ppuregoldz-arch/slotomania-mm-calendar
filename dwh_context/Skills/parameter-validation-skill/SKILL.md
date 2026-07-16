# Parameter Validation Skill

## Purpose
Validate parameter changes before production deployment to ensure correct implementation and identify potential issues.

## When to Use This Skill
**Use this skill when asked to validate a parameter.**

**Examples:**
- "Validate the cz_price_cut_test parameter changes"
- "Run validation for rv_opportunistic_config_buckets"
- "Check if the DPU_Segment update worked correctly"

## Data Source
- **Yesterday** = previous parameter value
- **Today** = new parameter value (before production deployment)
- Both values taken from `dwh.sm_user_profile_datamining_snapshot`
- Use date filtering to distinguish yesterday vs today snapshots

## Documentation Structure
Parameter documentation follows this structure:
```
context/business-knowledge/parameters/<param_name>/
│
├── definition.md
├── change-timeline.md
└── changes/
    ├── YYYY-MM-DD-change-description.md
    └── ...
```

## Prerequisites
- Access to Vertica MCP server (user-mcp-alchemy-sm)
- Parameter documentation exists in `context/business-knowledge/parameters/`
- Datamining table contains both yesterday and today parameter values

## Process
Follow the 4-step validation workflow documented in `workflow/validation-workflow.md`:

1. **Understand the Change** - Review documentation and identify expected impact
2. **Validate the Change** - Execute validation queries and perform checks
3. **Impact Analysis** - Analyze results by parameter type with appropriate metrics
4. **Summary** - Generate structured validation report with findings

## Final Deliverable
Every validation produces a structured **Validation Report** containing:
- Business description and change summary
- Population and value validation results
- Impact analysis with relevant tables/charts
- Manually validated user examples
- Detected anomalies and analysis
- Comprehensive findings for PASS/FAIL determination

## Integration
- Uses MCP Vertica server for SQL execution
- Reads parameter documentation from `context/business-knowledge/parameters/`
- Creates validation reports in `outputs/` folder structure
- Updates parameter documentation with validation results