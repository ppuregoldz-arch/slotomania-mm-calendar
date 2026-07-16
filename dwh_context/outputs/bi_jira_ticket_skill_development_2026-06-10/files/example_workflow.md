# BI Jira Ticket Creation Workflow Example

## Example Scenario

**User Input (Free Form)**:
"I need to add a new column to track revenue sources in the payments table for the RV analysis project. The column should store values like 'organic', 'applovin_rv', 'facebook_ads' etc."

## Generated Template Preview

### Jira Ticket Details
- **Project**: BI Team (BIT)
- **Issue Type**: Task
- **Priority**: Normal
- **Game**: SM
- **Team**: Terra
- **Assignee**: Boaz Priel
- **Summary**: Add revenue_source column to dwh.sm_fact_payments for RV analysis

### Description Content
```markdown
**Topic Name**: RV Analysis Project

**Table Name**: dwh.sm_fact_payments

**Action**: Add Column

**Changes Structure**:
| Action | Field Name (Vertica) | Field Name (Topic) | Data Type |
|--------|---------------------|-------------------|-----------|
| Add Column | revenue_source | Revenue Source | VARCHAR(50) |

**JSON Example**:
```json
{
  "revenue_source": "applovin_rv",
  "user_id": 12345,
  "amount": 9.99
}
```

**WIKI Page**: [To be provided if available]

**Additional Notes**: 
- Column will store revenue source attribution for payment tracking
- Expected values: 'organic', 'applovin_rv', 'facebook_ads', 'other'
- Default value should be NULL for existing records
- New payments should populate this field based on user acquisition source
```

## QA Validation & Approval Process

### Step 1: Automated QA Validation
System performs comprehensive validation and generates QA report:

```markdown
# QA Validation Report

## Summary
- **Overall Status**: ⚠️ WARNINGS FOUND
- **Critical Issues**: 0
- **Warnings**: 2  
- **Suggestions**: 1

## Technical Validation
### ✅ Data Types
- VARCHAR(50): Valid Vertica type with appropriate length

### ✅ Table Names
- dwh.sm_fact_payments: Exists, accessible, follows naming conventions

### ⚠️ Field Names  
- revenue_source: Follows snake_case ✅
- Potential improvement: Consider 'payment_source' to match existing 'payment_*' columns

## Business Logic Validation
### ✅ Value Consistency
- Revenue source values align with known marketing categories
- JSON example structure matches table pattern

### 💡 Suggestions
- Add NOT NULL constraint if revenue_source is always required
- Consider adding index on revenue_source for query performance
```

### Step 1: Automated Field Completion
System identifies missing information and auto-completes:

```markdown
# Auto-Completion Results
## Missing Data Types - Completed
- extreme_items_count: Missing → INTEGER DEFAULT 0 (90% confidence)
  - Source: Pattern matching (*_count → INTEGER)
  - Validation: Similar field 'activeGoldItems' in same table
  
- regular_multiplier: Missing → DOUBLE (95% confidence)  
  - Source: WIKI JSON example shows decimal values
  - Validation: Field 'multiplier' found in quantityPerItemType structure

## Missing Topic Names - Completed  
- extreme_items_count: Missing → itemsCount (88% confidence)
  - Source: WIKI parameter table mapping
  - Validation: Found in quantityPerItemType.EXTREME.itemsCount
```

### Step 2: Review Generated Template with QA Report
User reviews ticket content, QA validation, AND auto-completion results:
- ✅ Approve as-is (including auto-completions)
- ❌ Request modifications to auto-completed fields
- 🔄 Ask for alternative auto-completion suggestions

### Step 3: Modifications (if needed)
**Example user feedback**: "Apply the QA suggestion to use 'payment_source' and add the NOT NULL constraint"

**Updated template with QA improvements**:
| Action | Field Name (Vertica) | Field Name (Topic) | Data Type |
|--------|---------------------|-------------------|-----------|
| Add Column | payment_source | Payment Source | VARCHAR(50) NOT NULL DEFAULT 'unknown' |

**QA Re-validation**:
```markdown
# Updated QA Report
## Summary  
- **Overall Status**: ✅ PASSED
- **All issues resolved**: Field name improved, constraints added
```

### Step 4: Final Approval
User confirms: "Perfect, create the ticket"

### Step 5: Jira Ticket Creation
System uses MCP tools to create actual Jira ticket with QA-validated content.

## Complex Example

**User Input**:
"We're consuming the new user segmentation table that the data team created. We need to add fields for CZ bucket, tier level, and user lifecycle stage to our main user profile table."

**Generated Template**:
```markdown
**Topic Name**: User Segmentation Enhancement

**Table Name**: dwh.sm_user_profile_snapshot

**Action**: Add Column

**Changes Structure**:
| Action | Field Name (Vertica) | Field Name (Topic) | Data Type |
|--------|---------------------|-------------------|-----------|
| Add Column | cz_bucket_new | CZ Bucket Segment | VARCHAR(20) |
| Add Column | tier_level | User Tier Level | INT |
| Add Column | lifecycle_stage | User Lifecycle Stage | VARCHAR(30) |

**JSON Example**:
```json
{
  "user_id": 12345,
  "cz_bucket_new": "high_value",
  "tier_level": 5,
  "lifecycle_stage": "engaged_spender"
}
```

**WIKI Page**: [Link to user segmentation documentation]

**Additional Notes**:
- Data will be populated from new dwh.user_segmentation_master table
- Requires daily ETL job to update values
- CZ bucket values: 'low_value', 'medium_value', 'high_value', 'whale'
- Tier levels: 1-10 integer scale
- Lifecycle stages: 'new_user', 'engaged_free', 'engaged_spender', 'at_risk', 'churned'
- Coordinate with data engineering team for ETL implementation
```

## Error Handling Examples

### Insufficient Information
**User Input**: "Add a column to the payments table"

**System Response**: 
"I need more details to create the ticket. Could you provide:
- What should the column be named?
- What type of data will it store?
- What's the business purpose/context?"

### Clarification Needed
**User Input**: "Delete the old revenue field from payments"

**System Response**:
"Which specific revenue field should be deleted? I see several possibilities:
- revenue_usd
- revenue_local  
- gross_revenue
- net_revenue

Please specify the exact field name."

## Enhanced Integration Flow with QA

1. **Natural Language Processing**: Parse user input for key information
2. **Pre-Validation**: Check table existence, validate naming patterns
3. **WIKI Integration**: Fetch and validate against provided WIKI documentation
4. **Intelligent Field Completion**: Auto-fill missing data types and topic names
   - **Data Type Inference**: Analyze similar columns, patterns, and WIKI examples
   - **Topic Name Discovery**: Search WIKI content for parameter mappings
   - **Confidence Scoring**: Rate auto-completion reliability
5. **Template Population**: Fill template fields with completed information
6. **Comprehensive QA Validation**: 
   - Data type validation against Vertica specifications
   - Naming convention compliance checking
   - Cross-reference with existing schemas and WIKI documentation
   - Business logic validation using WIKI examples
   - Field mapping validation against topic structure
   - Auto-completion confidence assessment
7. **QA Report Generation**: Create detailed validation report with auto-completion results
8. **User Review**: Present formatted ticket, QA report, AND auto-completion details
9. **Iterative Refinement**: Allow modifications based on QA findings and auto-completions
10. **Final Validation**: Re-run QA checks on modified content
11. **Required Fields Population**: Auto-populate Game=SM, Team=Terra, other required fields
12. **MCP Integration**: Use `jira_create_issue` tool to create QA-validated ticket
13. **Post-Creation Updates**: Handle any corrections (like Team field updates)
14. **Confirmation**: Provide ticket number, link, auto-completion summary, and final QA status

## QA Validation Sources Used
- **Internal**: Context documentation, query history, table schemas, business glossary
- **External**: User-provided WIKI pages, Confluence documentation, schema catalogs
- **Real-time**: Table existence checks, naming pattern validation, field option validation
- **Historical**: Existing column patterns, established naming conventions
- **MCP Integration**: Jira field validation, required field population, custom field mapping

## Real-World Implementation Success

**Example: Stamp Cards Schema Update (BIT-26997)**
- **User Input**: Complex multi-action schema changes with WIKI reference
- **Auto-Completion**: Successfully inferred missing data types and topic names
- **QA Validation**: Successfully validated against WIKI documentation
- **Field Mapping**: Correctly mapped topic fields (itemsCount, multiplier, etc.)
- **Required Fields**: Auto-populated Game=SM, Team=Terra
- **JSON Integration**: Complete JSON example with existing and new fields
- **Confidence Scores**: 90%+ confidence on all auto-completed fields
- **Result**: Successfully created and updated ticket with intelligent field completion