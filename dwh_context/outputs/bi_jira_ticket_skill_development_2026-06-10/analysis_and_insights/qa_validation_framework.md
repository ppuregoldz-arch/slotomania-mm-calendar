# QA Validation Framework for BI Jira Tickets

## Overview
Comprehensive quality assurance system to validate BI Jira tickets before creation, ensuring data integrity, naming consistency, and technical accuracy.

## Validation Categories

### 1. Technical Validation

#### Data Type Validation
```python
VALID_VERTICA_TYPES = {
    'VARCHAR': {'max_length': 65000, 'requires_length': True},
    'CHAR': {'max_length': 65000, 'requires_length': True}, 
    'INTEGER': {'aliases': ['INT']},
    'BIGINT': {},
    'SMALLINT': {},
    'NUMERIC': {'requires_precision': True, 'max_precision': 1024},
    'DECIMAL': {'requires_precision': True, 'max_precision': 1024},
    'FLOAT': {},
    'REAL': {},
    'DOUBLE PRECISION': {'aliases': ['DOUBLE']},
    'BOOLEAN': {'aliases': ['BOOL']},
    'DATE': {},
    'TIME': {},
    'TIMESTAMP': {},
    'TIMESTAMPTZ': {},
    'INTERVAL': {},
    'BINARY': {'requires_length': True},
    'VARBINARY': {'requires_length': True}
}
```

#### Common Data Type Issues
- **Missing Length**: VARCHAR without length specification
- **Excessive Length**: VARCHAR(10000) for simple codes
- **Wrong Type**: Using VARCHAR for numeric IDs
- **Deprecated Types**: Using TEXT instead of VARCHAR
- **Invalid Precision**: DECIMAL with precision > 1024

#### Table Name Validation
```python
VALID_SCHEMAS = [
    'dwh',           # Data warehouse main schema
    'staging',       # Staging area
    'temp',          # Temporary tables
    'dev',           # Development schema
    'analytics',     # Analytics workspace
    'bi'             # BI specific tables
]

TABLE_NAME_PATTERNS = [
    r'^[a-z][a-z0-9_]*[a-z0-9]$',  # Must start with letter, end with letter/number
    r'^[a-z]{2,}_',                 # Must have meaningful prefix (not just 'a_' or 'x_')
    r'.*_(fact|dim|snapshot|temp|staging)$'  # Common table type suffixes
]
```

### 2. Naming Convention Validation

#### Field Name Rules
- **Format**: snake_case only (user_id, not userId or UserID)
- **Length**: 3-63 characters (Vertica limit is 128, but prefer shorter)
- **Reserved Words**: Check against Vertica reserved word list
- **Descriptive**: Avoid generic names (data, field, temp, col1)
- **Consistency**: Match patterns in existing table columns
- **Topic Mapping**: Validate against WIKI topic field definitions (itemsCount, multiplier, itemMaxAmountIncrease)

#### Reserved Words Check
```python
VERTICA_RESERVED_WORDS = [
    'user', 'order', 'group', 'limit', 'offset', 'table', 'column',
    'index', 'constraint', 'trigger', 'function', 'procedure',
    'select', 'insert', 'update', 'delete', 'create', 'drop', 'alter'
    # ... full list from Vertica documentation
]
```

#### Common Naming Issues
- **Reserved Words**: Using 'user' instead of 'user_id'
- **Abbreviations**: Over-abbreviated names (usr_id vs user_id)
- **Inconsistency**: Mixed naming styles in same table
- **Case Issues**: camelCase or PascalCase instead of snake_case

### 3. Business Logic Validation

#### Value Reasonableness
- **Enum Values**: Check if suggested values make business sense
- **Size Constraints**: VARCHAR size appropriate for expected values
- **Default Values**: Defaults align with business logic
- **NULL Handling**: NOT NULL constraints for required business fields

#### JSON Example Validation
```python
def validate_json_example(json_str, field_definitions):
    """
    Validate JSON example against field definitions
    - Check all new fields are included
    - Verify data types match
    - Ensure values are realistic
    - Include primary/foreign keys
    """
    pass
```

### 4. Documentation Validation

#### WIKI Page Validation
```python
def validate_wiki_page(url):
    """
    Validate WIKI page if provided
    - URL accessibility
    - Content relevance
    - Schema documentation presence
    - Business context availability
    """
    pass
```

#### Cross-Reference Validation
- **Existing Schemas**: Check against known table structures
- **Data Dictionary**: Validate against business glossary
- **Query Patterns**: Reference existing SQL in queries/ folder
- **Context Documentation**: Cross-check with context/ files

## Validation Sources Integration

### Internal Knowledge Base
```python
VALIDATION_SOURCES = {
    'context_docs': 'context/*.md',
    'query_history': 'queries/**/*.sql', 
    'table_schemas': 'context/*table*.md',
    'business_glossary': 'context/slotomania_glossary.mdc',
    'data_context': 'context/SM_ANALYST_DATA_CONTEXT.md'
}
```

### External Sources (When Available)
- **WIKI Pages**: User-provided documentation URLs (validated via MCP Confluence tools)
- **Schema Catalogs**: Enterprise data catalog APIs
- **Confluence**: Company documentation systems (accessed via user-mcp-atlassian-wiki)
- **Data Lineage**: Tools showing table relationships
- **Jira Field Validation**: Real-time validation of required fields and options

## QA Report Structure

### Validation Report Template
```markdown
# QA Validation Report

## Summary
- **Overall Status**: ✅ PASSED | ⚠️ WARNINGS | ❌ FAILED
- **Critical Issues**: 0
- **Warnings**: 2
- **Suggestions**: 3

## Technical Validation

### ✅ Data Types
- VARCHAR(50): Valid Vertica type with appropriate length
- TIMESTAMP: Standard temporal type

### ✅ Table Names  
- dwh.sm_fact_payments: Exists, accessible, follows conventions

### ⚠️ Field Names
- revenue_source: Follows snake_case ✅
- user_segment_new: Long but descriptive ⚠️

## Business Logic Validation

### ✅ Value Consistency
- Revenue source values align with known categories
- JSON example includes required keys

### 💡 Suggestions
- Consider adding NOT NULL constraint for revenue_source
- Default value should be 'unknown' to match existing patterns
- Include user_id in JSON example for context

## Documentation Validation

### ✅ WIKI Page
- URL accessible: https://wiki.company.com/revenue-tracking
- Contains relevant schema documentation
- Business context clearly defined

## Recommendations
1. **Change VARCHAR(10) to VARCHAR(50)** for revenue_source (current max value is 12 chars)
2. **Add NOT NULL constraint** if revenue_source is always required
3. **Consider index on revenue_source** if used frequently in queries
```

## Implementation Approach

### Pre-Generation Validation
1. **Parse user input** for technical terms and WIKI references
2. **Fetch WIKI documentation** if provided using MCP Confluence tools
3. **Intelligent Field Completion**: Auto-fill missing information using available data sources
4. **Validate against known schemas** and WIKI patterns
5. **Check for common mistakes** and typos
6. **Gather validation data** from all available sources

### Template Enhancement
1. **Generate base template** from user input
2. **Apply validation rules** and flag issues
3. **Suggest corrections** for identified problems
4. **Enhance with best practices** and standards

### Interactive QA Process
1. **Present template with QA report** including WIKI validation results
2. **Highlight issues** with severity levels and WIKI references
3. **Provide specific suggestions** for improvements based on documentation
4. **Allow user to accept/modify** recommendations
5. **Auto-populate required fields** (Game=SM, Team=Terra) based on defaults
6. **Handle post-creation updates** for any field corrections needed

## Error Prevention Strategies

### Intelligent Auto-Correction
- **Spelling Correction**: Fix common typos in table/field names
- **Type Standardization**: Convert 'string' to 'VARCHAR', 'int' to 'INTEGER'
- **Case Normalization**: Convert to proper snake_case automatically
- **Pattern Matching**: Suggest standard patterns for similar fields

### Context-Aware Suggestions
- **Similar Fields**: Reference existing columns with similar purposes
- **Table Patterns**: Align with existing table structure patterns
- **Business Rules**: Apply known business logic constraints
- **Performance Considerations**: Suggest indexes, constraints for efficiency

## Intelligent Field Completion System

### Missing Data Type Auto-Detection

#### Table Schema Analysis
```sql
-- Example: Analyze existing table structure
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns 
WHERE table_name = 'sm_fact_stamp_card' 
AND table_schema = 'dwh'
ORDER BY ordinal_position;
```

#### Data Type Intelligence Rules
```python
def infer_data_type(field_name, context_table=None, wiki_examples=None):
    """
    Intelligent data type inference based on multiple sources
    """
    # Pattern-based inference
    if 'count' in field_name.lower() or 'items' in field_name.lower():
        return 'INTEGER DEFAULT 0'
    
    if 'multiplier' in field_name.lower() or 'delta' in field_name.lower():
        return 'DOUBLE'
    
    if 'amount' in field_name.lower() or 'prize' in field_name.lower():
        return 'DOUBLE'  # Based on existing amount fields
    
    if 'id' in field_name.lower() and 'guid' not in field_name.lower():
        return 'BIGINT'
    
    if 'guid' in field_name.lower() or 'uuid' in field_name.lower():
        return 'VARCHAR(36)'
    
    if 'flag' in field_name.lower() or 'is_' in field_name.lower():
        return 'BOOLEAN DEFAULT FALSE'
    
    # Context table analysis
    if context_table:
        similar_columns = find_similar_columns(field_name, context_table)
        if similar_columns:
            return similar_columns[0]['data_type']
    
    # WIKI example analysis
    if wiki_examples:
        return infer_from_wiki_examples(field_name, wiki_examples)
    
    return 'VARCHAR(255)'  # Safe default
```

#### Similar Column Detection
- **Pattern Matching**: Find columns with similar naming patterns
- **Semantic Analysis**: Match business purpose (amounts, counts, IDs)
- **Table Context**: Analyze existing columns in same table
- **Cross-Table Analysis**: Reference similar tables (fact vs dimension patterns)

### Missing Topic Name Auto-Detection

#### WIKI Content Analysis
```python
def find_topic_name_in_wiki(field_name, wiki_content):
    """
    Search WIKI content for topic field names
    """
    # Direct field mapping from WIKI
    field_mappings = extract_field_mappings(wiki_content)
    
    # Search in JSON examples
    json_examples = extract_json_examples(wiki_content)
    for example in json_examples:
        if field_name in example or similar_field_found(field_name, example):
            return extract_topic_name(field_name, example)
    
    # Search in parameter tables
    parameter_tables = extract_parameter_tables(wiki_content)
    for table in parameter_tables:
        match = find_parameter_match(field_name, table)
        if match:
            return match['parameter_name']
    
    # Pattern-based inference
    return infer_topic_name_from_pattern(field_name)
```

#### Topic Name Intelligence Rules
```python
TOPIC_MAPPING_PATTERNS = {
    '*_count': 'itemsCount',
    '*_multiplier': 'multiplier', 
    '*_delta*': 'itemMaxAmountIncrease',
    '*_min_*': 'itemMinAmountIncrease',
    '*_max_*': 'itemMaxAmountIncrease',
    '*_amount': 'itemMaxAmount',
    '*_prize': 'itemMaxAmount',
    '*_items_*': 'itemsCount'
}
```

#### WIKI Search Strategies
1. **Direct Parameter Match**: Search parameter tables for exact field names
2. **JSON Example Mining**: Extract field names from JSON examples
3. **Mapping Section Analysis**: Find explicit field mapping documentation
4. **Pattern Recognition**: Use established patterns (quantityPerItemType.*.fieldName)
5. **Business Context**: Infer from business description and field purpose

### Automatic Field Enhancement Workflow

#### Step 1: Missing Field Detection
```python
def detect_missing_fields(user_request):
    """
    Identify fields with missing information
    """
    missing_fields = []
    for field in parsed_fields:
        issues = []
        if not field.get('data_type'):
            issues.append('missing_data_type')
        if not field.get('topic_name'):
            issues.append('missing_topic_name')
        if not field.get('description'):
            issues.append('missing_description')
        
        if issues:
            missing_fields.append({'field': field, 'missing': issues})
    
    return missing_fields
```

#### Step 2: Intelligent Auto-Completion
```python
def auto_complete_fields(missing_fields, wiki_content, table_schema):
    """
    Automatically complete missing field information
    """
    completed_fields = []
    
    for field_info in missing_fields:
        field = field_info['field']
        missing = field_info['missing']
        
        # Auto-complete data type
        if 'missing_data_type' in missing:
            field['data_type'] = infer_data_type(
                field['name'], 
                table_schema, 
                wiki_content
            )
            field['data_type_source'] = 'auto_inferred'
        
        # Auto-complete topic name
        if 'missing_topic_name' in missing:
            field['topic_name'] = find_topic_name_in_wiki(
                field['name'], 
                wiki_content
            )
            field['topic_name_source'] = 'wiki_search'
        
        # Auto-complete description
        if 'missing_description' in missing:
            field['description'] = generate_field_description(
                field['name'], 
                field.get('data_type'),
                wiki_content
            )
            field['description_source'] = 'auto_generated'
        
        completed_fields.append(field)
    
    return completed_fields
```

#### Step 3: Confidence Scoring
```python
def calculate_confidence_score(field):
    """
    Calculate confidence level for auto-completed fields
    """
    score = 100  # Start with full confidence
    
    if field.get('data_type_source') == 'auto_inferred':
        # High confidence for pattern-based inference
        if pattern_match_strong(field['name']):
            score *= 0.9  # 90% confidence
        else:
            score *= 0.7  # 70% confidence
    
    if field.get('topic_name_source') == 'wiki_search':
        # High confidence for direct WIKI matches
        if direct_wiki_match(field['name']):
            score *= 0.95  # 95% confidence
        else:
            score *= 0.8   # 80% confidence
    
    return score
```

### Enhanced QA Validation Report

#### Auto-Completion Results
```markdown
# Enhanced QA Validation Report

## Auto-Completion Results
### ✅ Data Types Completed
- extreme_items_count: INTEGER DEFAULT 0 (90% confidence - pattern match)
- regular_multiplier: DOUBLE (85% confidence - similar column analysis)
- golden_delta: DOUBLE (95% confidence - WIKI example match)

### ✅ Topic Names Completed  
- extreme_items_count → itemsCount (95% confidence - direct WIKI match)
- regular_multiplier → multiplier (90% confidence - pattern recognition)
- golden_delta → itemMaxAmountIncrease (88% confidence - WIKI mapping)

## Validation Sources Used
- **Table Schema**: dwh.sm_fact_stamp_card existing columns analyzed
- **WIKI Content**: Parameter tables and JSON examples parsed
- **Pattern Recognition**: Business naming conventions applied
- **Cross-Reference**: Similar tables and columns referenced
```

### Implementation Priority

#### High-Confidence Auto-Completion (Auto-Apply)
- **Direct WIKI Matches**: Field names found in parameter tables
- **Strong Patterns**: *_count → INTEGER, *_multiplier → DOUBLE
- **Existing Columns**: Match patterns from same table

#### Medium-Confidence Auto-Completion (User Review)
- **Semantic Inference**: Business logic-based guessing
- **Cross-Table Analysis**: Patterns from similar tables
- **Partial WIKI Matches**: Close but not exact matches

#### Low-Confidence Auto-Completion (Flag for Review)
- **Generic Defaults**: VARCHAR(255) fallbacks
- **Uncertain Patterns**: Ambiguous field purposes
- **No Reference Data**: Completely unknown field types

This comprehensive QA framework ensures high-quality, consistent, and error-free BI Jira tickets while leveraging all available knowledge sources for validation.