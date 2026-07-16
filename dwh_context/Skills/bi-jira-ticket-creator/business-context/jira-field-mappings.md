# BI Jira Field Mappings and Business Context

## Jira Project Configuration

### Project: BI Team (BIT)
- **Project Key**: BIT
- **Project ID**: 12900
- **Category**: Technologies
- **Description**: Business Intelligence team project for data-related tasks

### Required Custom Fields

#### Game Field (customfield_12804)
- **Field Type**: Single Select
- **Required**: Yes
- **Options**: BB, BF, BFS, BK, CC, GOP3, HOF, JPT, MONOP, OVO, PH, PK, REDECOR, SGH, SM, VDS, WOOGA, WSOP, YOUDA, Other
- **Default for Slotomania**: SM
- **Usage**: Identifies which game the BI task relates to

#### Team Field (customfield_11214)  
- **Field Type**: Single Select
- **Required**: Yes
- **Options**: Alpha, Astra, Omega, Terra, Delta, Gama, Lamda
- **Default**: Terra
- **Usage**: Assigns ticket to specific BI team for execution

### Standard Fields Configuration
- **Issue Type**: Task (standard for BI schema changes)
- **Priority**: Normal (default, can be overridden)
- **Assignee**: Boaz Priel (default BI lead, can be overridden)

## Field Mapping Intelligence

### Data Type Inference Patterns

#### JSON Value Analysis Priority
**CRITICAL**: Always analyze JSON examples first to determine appropriate data types based on actual values.

```python
def analyze_json_values_for_data_type(field_name, json_examples):
    """
    Analyze JSON example values to determine most appropriate data type
    Priority: JSON analysis > Pattern matching > Default rules
    """
    for example in json_examples:
        if field_name in example:
            value = example[field_name]
            
            # Large number analysis (coins, balance, rewards)
            if isinstance(value, (int, float)) and abs(value) > 1000000:
                return {
                    'data_type': 'DOUBLE PRECISION',
                    'confidence': 0.95,
                    'reason': f'Large numeric value detected: {value}'
                }
            
            # Regular numeric analysis
            elif isinstance(value, float):
                return {
                    'data_type': 'DOUBLE',
                    'confidence': 0.90,
                    'reason': f'Decimal value detected: {value}'
                }
            
            elif isinstance(value, int):
                if abs(value) > 2147483647:  # > INT max
                    return 'BIGINT'
                else:
                    return 'INTEGER'
            
            # String length analysis
            elif isinstance(value, str):
                max_length = max(len(str(v)) for v in get_all_string_values(field_name, json_examples))
                recommended_length = min(max_length * 1.5, 65000)  # 50% buffer
                return f'VARCHAR({int(recommended_length)})'
    
    return None  # Fall back to pattern matching
```

#### Count/Quantity Fields
```
Pattern: *_count, *_items, *_quantity
Data Type: INTEGER DEFAULT 0
Confidence: High (90%+)
Examples: extreme_items_count, user_count, session_quantity
```

#### Amount/Value Fields
```
Pattern: *_amount, *_prize, *_value, *_revenue
Data Type: DOUBLE
Confidence: High (90%+)
Examples: revenue_amount, min_prize, total_value
```

#### Coins/Balance Fields (High Precision Required)
```
Pattern: *_coins, *_balance, *_reward, *coins_amount, *_gems
Data Type: DOUBLE PRECISION
Confidence: High (95%+)
Reason: Large numbers with high precision needed (e.g., 1.8E10, 5.2343E8)
Examples: coins_balance, reward_amount, gems_count, min_coins_amount
```

#### Multiplier/Rate Fields
```
Pattern: *_multiplier, *_rate, *_percent
Data Type: DOUBLE  
Confidence: High (90%+)
Examples: regular_multiplier, conversion_rate, success_percent
```

#### Delta/Change Fields
```
Pattern: *_delta, *_change, *_increase, *_decrease
Data Type: DOUBLE
Confidence: High (85%+)
Examples: revenue_delta, price_change, value_increase
```

#### Identifier Fields
```
Pattern: *_id, *_key (excluding *_guid)
Data Type: BIGINT
Confidence: High (90%+)
Examples: user_id, session_key, transaction_id
```

#### GUID/UUID Fields
```
Pattern: *_guid, *_uuid, card_id (specific cases)
Data Type: VARCHAR(36)
Confidence: High (95%+)
Examples: card_guid, session_uuid, unique_identifier
```

#### Boolean/Flag Fields
```
Pattern: is_*, has_*, *_flag, *_enabled
Data Type: BOOLEAN DEFAULT FALSE
Confidence: High (90%+)
Examples: is_active, has_premium, enabled_flag
```

#### Timestamp Fields
```
Pattern: *_ts, *_timestamp, *_time
Data Type: BIGINT (for Unix timestamps) or TIMESTAMP
Confidence: High (90%+)
Examples: created_ts, last_update_timestamp, event_time
```

#### Status/Category Fields
```
Pattern: *_status, *_type, *_category
Data Type: VARCHAR(50)
Confidence: Medium (75%)
Examples: user_status, payment_type, event_category
```

#### Name/Description Fields
```
Pattern: *_name, *_title, *_description
Data Type: VARCHAR(255)
Confidence: Medium (70%)
Examples: feature_name, campaign_title, error_description
```

### Topic Name Mapping Patterns

#### Slotomania Stamp Cards Context
Based on WIKI: `https://wiki.playtika.com/spaces/SLOT/pages/232892814/Stamp+Cards+BI+BA+events`

```
quantityPerItemType Structure:
├── itemsCount → *_items_count fields
├── multiplier → *_multiplier fields
├── itemMaxAmount → *_max_amount, *_max_prize fields
├── itemMinAmount → *_min_amount, *_min_prize fields
├── itemMaxAmountIncrease → *_delta, *_max_delta fields
└── itemMinAmountIncrease → *_delta_min fields
```

#### Common Topic Mapping Rules
```
Database Field → Topic Field
*_count → itemsCount
*_multiplier → multiplier
*_amount → itemMaxAmount (for max) or itemMinAmount (for min)
*_delta → itemMaxAmountIncrease (default) or itemMinAmountIncrease (if _min)
*_ts → timestamp
*_id → id
```

## Business Logic Validation Rules

### Vertica Data Type Compliance
- **VARCHAR**: Must specify length, max 65000 characters
- **NUMERIC/DECIMAL**: Must specify precision, max 1024
- **No TEXT type**: Use VARCHAR(n) instead
- **Boolean types**: Use BOOLEAN, not BIT or TINYINT
- **Timestamps**: Prefer BIGINT for Unix timestamps or TIMESTAMP for formatted dates
- **Coins/Balance Fields**: Always use DOUBLE PRECISION for large monetary values (e.g., 1.8E10)
- **JSON Value Priority**: Always check JSON examples first to determine appropriate data type and sizing

### Naming Convention Enforcement
- **Snake_case only**: user_id not userId or UserID
- **No reserved words**: Avoid 'user', 'order', 'group', 'limit' without suffixes
- **Descriptive names**: Avoid generic terms like 'data', 'field', 'temp'
- **Length limits**: 3-63 characters recommended (Vertica max is 128)

### Business Context Rules
- **Slotomania tables**: Use 'sm_' prefix for fact tables
- **DWH schema**: Most tables in 'dwh' schema
- **Staging patterns**: Use 'staging' schema for temporary tables
- **Default values**: Provide sensible defaults for new columns
- **NULL handling**: Explicit NOT NULL or DEFAULT specifications

## WIKI Integration Patterns

### Field Discovery Methods

#### Parameter Tables
Search for HTML tables with parameter definitions:
```html
<table>
  <tr><th>Parameter name</th><th>Type</th><th>Description</th></tr>
  <tr><td>itemsCount</td><td>Integer</td><td>Amount of items</td></tr>
</table>
```

#### JSON Examples
Extract field names from JSON code blocks:
```json
{
  "quantityPerItemType": {
    "REGULAR": {
      "itemsCount": 5,
      "multiplier": 0.29
    }
  }
}
```

#### Mapping Sections
Look for explicit field mapping documentation:
```
quantityPerItemType.REGULAR.itemsCount - new field
quantityPerItemType.REGULAR.multiplier - business multiplier value
```

### Confidence Scoring Logic

#### High Confidence (85%+)
- **Direct WIKI match**: Field name found in parameter tables
- **Strong pattern match**: Clear naming convention (e.g., *_count → INTEGER)
- **Schema validation**: Similar field found in same table

#### Medium Confidence (70-85%)
- **Fuzzy WIKI match**: Similar field name in documentation
- **Pattern inference**: Reasonable business logic guess
- **Cross-table analysis**: Similar field in related table

#### Low Confidence (<70%)
- **Generic fallback**: VARCHAR(255) default
- **Weak pattern**: Ambiguous naming pattern
- **No references**: No similar fields or documentation

## Error Handling Patterns

### Missing Information Recovery
```
If data_type is missing:
1. **Check WIKI JSON examples for field** (HIGHEST PRIORITY)
   - Analyze actual values to determine type and sizing
   - Look for large numbers (>1M) indicating DOUBLE PRECISION needed
   - Check string lengths for appropriate VARCHAR sizing
2. **Apply pattern recognition rules** based on field naming
3. **Analyze existing table schema** for similar column patterns
4. **Use conservative default** (VARCHAR with appropriate length)

If topic_name is missing:
1. Search WIKI parameter tables
2. Check JSON structure mapping
3. Apply business logic patterns
4. Flag for manual review if uncertain
```

### Validation Failure Recovery
```
If table doesn't exist:
1. Check for similar table names
2. Suggest typo corrections
3. Verify schema access permissions

If field type conflicts:
1. Show existing field definition
2. Suggest compatible alternatives
3. Flag potential data migration needs
```

### User Correction Handling
```
If user modifies auto-completions:
1. Update confidence scores based on feedback
2. Learn new patterns for future use
3. Re-validate modified fields
4. Update ticket with corrections
```

This business context enables intelligent, accurate, and consistent BI Jira ticket creation with minimal user input while maintaining high technical accuracy.