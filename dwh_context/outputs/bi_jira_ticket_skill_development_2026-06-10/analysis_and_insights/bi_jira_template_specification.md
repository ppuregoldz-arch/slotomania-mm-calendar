# BI Jira Ticket Template Specification

## Template Structure

### Ticket Metadata
- **Project**: BI Team (BIT)
- **Issue Type**: Task
- **Priority**: Normal
- **Game**: SM (for Slotomania-related tickets)
- **Team**: Terra (default, unless specified otherwise)
- **Assignee**: Boaz Priel (default, can be overridden)
- **Summary**: User-provided title/description

### Description Template Format

```markdown
**Topic Name**: [Business context/project name]

**Table Name**: [Full qualified table name]

**Action**: [Add Column / Delete Column / Consuming New Table / Other]

**Changes Structure**:
| Action | Field Name (Vertica) | Field Name (Topic) | Data Type |
|--------|---------------------|-------------------|-----------|
| [Specific action] | [Technical column name] | [Business-friendly name] | [SQL data type] |

**JSON Example**:
```json
{
  "field_name": "example_value",
  "another_field": "another_example"
}
```

**WIKI Page**: [URL if documentation exists]

**Additional Notes**: [Any specific requirements, context, or considerations]
```

## Field Definitions

### Topic Name
- **Purpose**: Provides business context for the change
- **Examples**: "Revenue Analysis", "User Segmentation", "RV Performance Tracking"
- **Format**: Free text, business-oriented

### Table Name  
- **Purpose**: Identifies the specific database table to be modified
- **Format**: Fully qualified name (schema.table_name)
- **Examples**: "dwh.sm_fact_payments", "dwh.sm_user_profile_snapshot"

### Action
- **Purpose**: Specifies the type of database change required
- **Options**:
  - Add Column
  - Delete Column  
  - Consuming New Table
  - Modify Column (future enhancement)
  - Create Index (future enhancement)

### Changes Structure Table
- **Action**: Specific operation (Add Column, Delete Column, etc.)
- **Field Name (Vertica)**: Technical column name as it appears in database
- **Field Name (Topic)**: Business-friendly name for documentation
- **Data Type**: SQL data type specification (VARCHAR(50), INT, TIMESTAMP, etc.)

### JSON Example
- **Purpose**: Provides sample data format for new fields
- **Format**: Valid JSON showing expected field structure and sample values
- **Use Case**: Helps developers understand data format and testing

### WIKI Page
- **Purpose**: Links to existing documentation if available
- **Format**: Full URL to confluence or other documentation system
- **Optional**: Not all tickets will have associated documentation

### Additional Notes
- **Purpose**: Capture any special requirements, context, or considerations
- **Examples**: 
  - Default values for new columns
  - Business rules or constraints
  - Impact on existing queries or reports
  - Dependencies on other changes

## Usage Guidelines

### When to Use This Template
- Database schema modifications
- New table consumption/integration
- Column additions or removals
- Data structure changes affecting BI processes

### Template Flexibility
- Template serves as starting structure
- Fields can be adapted based on specific ticket requirements
- Additional sections can be added as needed
- Some fields may be omitted if not relevant

### Quality Assurance & Validation

### Automated QA Checks
The system will perform comprehensive validation before presenting the ticket for approval:

#### 1. **Data Type Validation**
- **Vertica Compatibility**: Verify data types are valid Vertica SQL types
- **Size Specifications**: Check VARCHAR lengths are reasonable (not too small/large)
- **Numeric Precision**: Validate DECIMAL/NUMERIC precision and scale
- **Date/Time Types**: Ensure proper TIMESTAMP, DATE, TIME specifications
- **Common Patterns**: Flag unusual type choices (e.g., VARCHAR for numeric IDs)

#### 2. **Naming Convention Validation**
- **Snake Case**: Verify field names use snake_case (user_id, not userId or UserID)
- **Reserved Words**: Check against Vertica reserved word list
- **Length Limits**: Ensure field names don't exceed Vertica limits (128 characters)
- **Descriptive Names**: Flag overly generic names (temp, data, field, etc.)
- **Consistency**: Check naming patterns against existing table columns

#### 3. **Table Name Validation**
- **Schema Verification**: Confirm schema exists (dwh, staging, etc.)
- **Table Existence**: Validate table exists in the database
- **Naming Pattern**: Check follows established naming conventions
- **Permission Check**: Verify user has access to modify specified table

#### 4. **Business Logic Validation**
- **JSON Structure**: Validate JSON examples are properly formatted
- **Value Reasonableness**: Check sample values make business sense
- **Constraint Logic**: Verify DEFAULT values match data type
- **NULL Handling**: Ensure NULL/NOT NULL specifications are logical

#### 5. **Documentation Cross-Reference**
- **WIKI Page Validation**: If WIKI URL provided, verify it's accessible
- **Schema Documentation**: Cross-reference against known table schemas
- **Data Dictionary**: Check against existing data definitions
- **Column Descriptions**: Verify against established business definitions

### QA Validation Sources

#### Internal Knowledge Base
- **Context Repository**: Cross-reference against `context/` documentation
- **Query History**: Check against existing SQL patterns in `queries/`
- **Table Schemas**: Validate against known table structures
- **Business Glossary**: Verify terminology against established definitions

#### External Validation (When Provided)
- **WIKI Pages**: Parse and validate against provided documentation
- **Schema Docs**: Cross-reference with external schema documentation
- **Data Catalogs**: Validate against enterprise data catalog entries
- **Style Guides**: Check against company naming conventions

### Validation Workflow

#### Step 1: Pre-Template QA
1. **Parse user input** for technical terms and table references
2. **Validate table existence** and accessibility
3. **Check naming conventions** against established patterns
4. **Verify data types** against Vertica specifications

#### Step 2: Template Generation with QA Flags
1. **Generate template** with validated information
2. **Flag potential issues** with warning indicators
3. **Suggest corrections** for common mistakes
4. **Highlight uncertainties** requiring user confirmation

#### Step 3: QA Report Generation
```markdown
## QA Validation Report

### ✅ Passed Checks
- Table name: dwh.sm_fact_payments (exists, accessible)
- Data type: VARCHAR(50) (valid Vertica type)
- Field name: revenue_source (follows naming conventions)

### ⚠️ Warnings
- Field name 'rev_src' is very abbreviated, consider 'revenue_source'
- VARCHAR(10) might be too small for revenue source values

### ❌ Issues Found
- Data type 'TEXT' not recommended, use VARCHAR(n) instead
- Field name 'user-id' contains hyphen, should be 'user_id'
- Table 'payments' not found, did you mean 'dwh.sm_fact_payments'?

### 💡 Suggestions
- Consider adding NOT NULL constraint for required fields
- Default value 'unknown' aligns with existing patterns
- JSON example should include primary key field (user_id)
```

### Enhanced Error Prevention

#### Common Mistake Detection
- **Typos**: Check against known table/column names
- **Case Issues**: Flag mixed case in field names
- **Type Mismatches**: Detect ID fields as VARCHAR vs INT
- **Size Problems**: Flag unrealistic VARCHAR sizes
- **Missing Constraints**: Suggest NOT NULL for required fields

#### Intelligent Suggestions
- **Auto-correction**: Suggest correct spellings for known terms
- **Pattern Matching**: Recommend standard patterns for similar fields
- **Best Practices**: Suggest improvements based on existing schemas
- **Consistency**: Align with existing table column patterns

## Integration Points

### MCP Tool Usage
- Template will be populated programmatically via MCP `jira_create_issue`
- Field mappings ensure proper Jira field population
- Structured format enables consistent ticket creation

### Validation Requirements
- Table name validation against known schemas
- Data type validation against Vertica specifications
- Required field completion checking
- Format consistency verification