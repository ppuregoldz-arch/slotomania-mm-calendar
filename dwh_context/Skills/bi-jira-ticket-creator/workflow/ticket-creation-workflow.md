# BI Jira Ticket Creation Workflow

## Complete Step-by-Step Process

### Phase 1: Input Processing & Analysis

#### Step 1.1: Parse User Requirements
```python
def parse_user_input(user_message):
    """
    Extract key information from natural language input
    """
    parsed_data = {
        'table_name': extract_table_references(user_message),
        'wiki_urls': extract_wiki_links(user_message),
        'actions': identify_requested_actions(user_message),
        'field_specifications': extract_field_details(user_message),
        'business_context': extract_context_clues(user_message)
    }
    return parsed_data
```

**Expected Inputs:**
- Table names (dwh.sm_fact_*, staging.*, etc.)
- WIKI URLs (wiki.playtika.com links)
- Action types (add, delete, rename, consume)
- Field specifications (names, types, purposes)
- Business requirements and context

#### Step 1.2: Validate Basic Requirements
```python
def validate_basic_requirements(parsed_data):
    """
    Ensure minimum required information is present
    """
    validation_results = {
        'has_table_name': bool(parsed_data['table_name']),
        'has_clear_action': bool(parsed_data['actions']),
        'has_field_info': bool(parsed_data['field_specifications']),
        'missing_info': identify_missing_critical_info(parsed_data)
    }
    return validation_results
```

### Phase 2: WIKI Integration & Context Gathering

#### Step 2.1: Fetch WIKI Documentation
```python
def fetch_wiki_content(wiki_urls):
    """
    Retrieve WIKI documentation using MCP Confluence tools
    """
    wiki_content = {}
    for url in wiki_urls:
        page_id = extract_page_id(url)
        content = mcp_call('user-mcp-atlassian-wiki', 'confluence_get_page', {
            'page_id': page_id,
            'convert_to_markdown': True,
            'include_metadata': True
        })
        wiki_content[url] = content
    return wiki_content
```

#### Step 2.2: Parse WIKI Content
```python
def parse_wiki_content(wiki_content):
    """
    Extract structured information from WIKI documentation
    """
    parsed_wiki = {}
    for url, content in wiki_content.items():
        parsed_wiki[url] = {
            'parameter_tables': extract_parameter_tables(content),
            'json_examples': extract_json_examples(content),
            'field_mappings': extract_field_mappings(content),
            'business_context': extract_business_descriptions(content),
            'data_structures': extract_data_structures(content)
        }
    return parsed_wiki
```

### Phase 3: Intelligent Field Completion

#### Step 3.1: Analyze Missing Information
```python
def analyze_missing_fields(field_specifications):
    """
    Identify fields with missing data types or topic names
    """
    missing_analysis = {
        'missing_data_types': [],
        'missing_topic_names': [],
        'missing_descriptions': [],
        'complete_fields': []
    }
    
    for field in field_specifications:
        if not field.get('data_type'):
            missing_analysis['missing_data_types'].append(field)
        if not field.get('topic_name'):
            missing_analysis['missing_topic_names'].append(field)
        if not field.get('description'):
            missing_analysis['missing_descriptions'].append(field)
        else:
            missing_analysis['complete_fields'].append(field)
    
    return missing_analysis
```

#### Step 3.2: Execute Auto-Completion
```python
def execute_intelligent_completion(missing_analysis, wiki_data, table_schema):
    """
    Auto-complete missing field information using multiple sources
    PRIORITY ORDER: JSON examples > Pattern recognition > Schema analysis > Defaults
    """
    completion_results = []
    
    for field in missing_analysis['missing_data_types']:
        # Data type inference with JSON priority
        data_type_result = infer_data_type_with_json_priority(
            field_name=field['name'],
            json_examples=wiki_data.get('json_examples', {}),  # HIGHEST PRIORITY
            table_schema=table_schema,
            pattern_rules=DATA_TYPE_PATTERNS
        )
        
        completion_results.append({
            'field': field,
            'completion_type': 'data_type',
            'result': data_type_result['data_type'],
            'confidence': data_type_result['confidence'],
            'source': data_type_result['source'],
            'analysis_method': data_type_result['method']
        })
    
    for field in missing_analysis['missing_topic_names']:
        # Topic name discovery
        topic_result = find_topic_name(
            field_name=field['name'],
            wiki_mappings=wiki_data.get('field_mappings', {}),
            pattern_rules=TOPIC_NAME_PATTERNS
        )
        
        completion_results.append({
            'field': field,
            'completion_type': 'topic_name',
            'result': topic_result['topic_name'],
            'confidence': topic_result['confidence'],
            'source': topic_result['source']
        })
    
    return completion_results

def infer_data_type_with_json_priority(field_name, json_examples, table_schema, pattern_rules):
    """
    Infer data type with JSON example analysis as highest priority
    """
    # STEP 1: JSON Value Analysis (Highest Priority)
    json_result = analyze_json_values_for_data_type(field_name, json_examples)
    if json_result:
        return {
            'data_type': json_result['data_type'],
            'confidence': json_result['confidence'],
            'source': 'json_value_analysis',
            'method': 'json_examples',
            'details': json_result['reason']
        }
    
    # STEP 2: Coins/Balance Special Handling
    coins_patterns = ['coins', 'balance', 'reward', 'amount', 'prize', 'gems']
    if any(pattern in field_name.lower() for pattern in coins_patterns):
        # Check if JSON shows large numbers
        large_values_detected = check_for_large_values(field_name, json_examples)
        if large_values_detected:
            return {
                'data_type': 'DOUBLE PRECISION',
                'confidence': 0.95,
                'source': 'coins_pattern_with_large_values',
                'method': 'pattern_recognition',
                'details': f'Coins/balance field with large values detected'
            }
    
    # STEP 3: Pattern Recognition (Standard Rules)
    for pattern, data_type in pattern_rules.items():
        if re.match(pattern, field_name, re.IGNORECASE):
            return {
                'data_type': data_type,
                'confidence': 0.85,
                'source': 'pattern_matching',
                'method': 'pattern_recognition',
                'details': f'Matched pattern: {pattern}'
            }
    
    # STEP 4: Schema Analysis (Similar Columns)
    similar_column = find_most_similar_column(field_name, table_schema)
    if similar_column and similar_column['similarity'] > 0.8:
        return {
            'data_type': similar_column['data_type'],
            'confidence': 0.75,
            'source': 'schema_analysis',
            'method': 'similar_column',
            'details': f'Similar to: {similar_column["name"]}'
        }
    
    # STEP 5: Conservative Default
    return {
        'data_type': 'VARCHAR(255)',
        'confidence': 0.40,
        'source': 'default_fallback',
        'method': 'conservative_default',
        'details': 'No strong indicators found, using safe default'
    }

def analyze_json_values_for_data_type(field_name, json_examples):
    """
    Analyze JSON example values to determine most appropriate data type
    """
    field_values = []
    
    # Extract all values for this field from JSON examples
    for example in json_examples:
        if isinstance(example, dict):
            value = extract_nested_field_value(example, field_name)
            if value is not None:
                field_values.append(value)
    
    if not field_values:
        return None
    
    # Analyze numeric values
    numeric_values = [v for v in field_values if isinstance(v, (int, float))]
    if numeric_values:
        max_value = max(abs(v) for v in numeric_values)
        has_decimals = any(isinstance(v, float) or '.' in str(v) for v in numeric_values)
        
        # Large numbers (coins, balance, rewards) - Use DOUBLE PRECISION
        if max_value >= 1000000:  # 1 million or larger
            return {
                'data_type': 'DOUBLE PRECISION',
                'confidence': 0.95,
                'reason': f'Large numeric values detected (max: {max_value:,.0f})'
            }
        
        # Regular decimal numbers
        elif has_decimals:
            return {
                'data_type': 'DOUBLE',
                'confidence': 0.90,
                'reason': f'Decimal values detected (range: {min(numeric_values)} to {max(numeric_values)})'
            }
        
        # Integer values
        elif max_value > 2147483647:  # Larger than INT max
            return {
                'data_type': 'BIGINT',
                'confidence': 0.90,
                'reason': f'Large integer values detected (max: {max_value})'
            }
        else:
            return {
                'data_type': 'INTEGER',
                'confidence': 0.85,
                'reason': f'Integer values detected (range: {min(numeric_values)} to {max(numeric_values)})'
            }
    
    # Analyze string values
    string_values = [str(v) for v in field_values if isinstance(v, str)]
    if string_values:
        max_length = max(len(s) for s in string_values)
        avg_length = sum(len(s) for s in string_values) / len(string_values)
        
        # Determine appropriate VARCHAR size with buffer
        if max_length <= 10:
            varchar_size = 20
        elif max_length <= 50:
            varchar_size = 100
        elif max_length <= 255:
            varchar_size = 255
        else:
            varchar_size = min(int(max_length * 1.5), 65000)  # 50% buffer, max 65000
        
        return {
            'data_type': f'VARCHAR({varchar_size})',
            'confidence': 0.85,
            'reason': f'String values detected (max length: {max_length}, avg: {avg_length:.1f})'
        }
    
    # Boolean values
    bool_values = [v for v in field_values if isinstance(v, bool)]
    if bool_values:
        return {
            'data_type': 'BOOLEAN',
            'confidence': 0.95,
            'reason': 'Boolean values detected'
        }
    
    return None

def check_for_large_values(field_name, json_examples):
    """
    Check if field contains large numeric values (>1M) indicating coins/balance
    """
    for example in json_examples:
        if isinstance(example, dict):
            value = extract_nested_field_value(example, field_name)
            if isinstance(value, (int, float)) and abs(value) >= 1000000:
                return True
    return False
```

#### Step 3.3: Calculate Confidence Scores
```python
def calculate_confidence_scores(completion_results):
    """
    Assess reliability of auto-completions
    """
    confidence_categories = {
        'high_confidence': [],      # 85%+ - Auto-apply
        'medium_confidence': [],    # 70-85% - User review
        'low_confidence': [],       # <70% - Manual specification
        'failed_completion': []     # No completion possible
    }
    
    for result in completion_results:
        confidence = result['confidence']
        if confidence >= 0.85:
            confidence_categories['high_confidence'].append(result)
        elif confidence >= 0.70:
            confidence_categories['medium_confidence'].append(result)
        elif confidence > 0:
            confidence_categories['low_confidence'].append(result)
        else:
            confidence_categories['failed_completion'].append(result)
    
    return confidence_categories
```

### Phase 4: QA Validation

#### Step 4.1: Technical Validation
```python
def perform_technical_validation(field_specifications, table_schema):
    """
    Validate technical aspects of field specifications
    """
    validation_results = {
        'data_type_validation': validate_vertica_data_types(field_specifications),
        'naming_convention_check': validate_naming_conventions(field_specifications),
        'reserved_words_check': check_reserved_words(field_specifications),
        'table_existence_check': validate_table_exists(table_schema['table_name']),
        'schema_consistency': check_schema_consistency(field_specifications, table_schema)
    }
    return validation_results
```

#### Step 4.2: Business Logic Validation  
```python
def perform_business_validation(field_specifications, wiki_data):
    """
    Validate business logic and contextual accuracy
    """
    business_validation = {
        'topic_mapping_accuracy': validate_topic_mappings(field_specifications, wiki_data),
        'json_structure_compliance': validate_json_structure(field_specifications, wiki_data),
        'business_context_alignment': validate_business_context(field_specifications, wiki_data),
        'value_consistency_check': validate_example_values(field_specifications, wiki_data)
    }
    return business_validation
```

#### Step 4.3: Generate QA Report
```python
def generate_qa_report(technical_validation, business_validation, completion_results):
    """
    Create comprehensive QA validation report
    """
    qa_report = {
        'overall_status': determine_overall_status(technical_validation, business_validation),
        'critical_issues': identify_critical_issues(technical_validation, business_validation),
        'warnings': identify_warnings(technical_validation, business_validation),
        'suggestions': generate_improvement_suggestions(completion_results),
        'auto_completion_summary': summarize_completions(completion_results),
        'confidence_assessment': assess_overall_confidence(completion_results)
    }
    return qa_report
```

### Phase 5: Template Generation

#### Step 5.1: Build Ticket Structure
```python
def build_ticket_template(field_specifications, wiki_data, user_context):
    """
    Generate structured Jira ticket template
    """
    template = {
        'summary': generate_ticket_summary(field_specifications, user_context),
        'topic_name': extract_topic_name(wiki_data, user_context),
        'table_name': user_context['table_name'],
        'action_type': determine_action_type(field_specifications),
        'changes_structure': build_changes_table(field_specifications),
        'json_example': build_json_example(field_specifications, wiki_data),
        'wiki_page': user_context.get('wiki_urls', [''])[0],
        'additional_notes': generate_additional_notes(field_specifications, user_context)
    }
    return template
```

#### Step 5.2: Format for Jira
```python
def format_for_jira(template):
    """
    Format template into Jira markdown format
    """
    formatted_description = f"""
**Topic Name**: {template['topic_name']}

**Table Name**: {template['table_name']}

**Action**: {template['action_type']}

**Changes Structure**:
{format_changes_table(template['changes_structure'])}

**JSON Example**:
```json
{format_json_example(template['json_example'])}
```

**WIKI Page**: {template['wiki_page']}

**Additional Notes**:
{template['additional_notes']}
"""
    return formatted_description
```

### Phase 6: User Review & Approval

#### Step 6.1: Present Results to User
```python
def present_review_package(template, qa_report, completion_results):
    """
    Show user the complete ticket package for review
    """
    review_package = {
        'formatted_ticket': format_for_display(template),
        'qa_validation_report': format_qa_report(qa_report),
        'auto_completion_details': format_completion_results(completion_results),
        'confidence_summary': summarize_confidence_levels(completion_results)
    }
    return review_package
```

#### Step 6.2: Handle User Feedback
```python
def process_user_feedback(review_package, user_feedback):
    """
    Process user modifications and approval
    """
    if user_feedback['status'] == 'approved':
        return prepare_for_creation(review_package)
    elif user_feedback['status'] == 'modifications_requested':
        return apply_user_modifications(review_package, user_feedback['changes'])
    elif user_feedback['status'] == 'needs_clarification':
        return request_additional_information(user_feedback['questions'])
    else:
        return handle_rejection(user_feedback['reason'])
```

### Phase 7: Jira Ticket Creation

#### Step 7.1: Populate Required Fields
```python
def populate_jira_fields(template, user_preferences=None):
    """
    Set all required Jira fields for ticket creation
    """
    jira_fields = {
        'project_key': 'BIT',
        'issue_type': 'Task',
        'summary': template['summary'],
        'description': template['formatted_description'],
        'assignee': user_preferences.get('assignee', 'Boaz Priel'),
        'additional_fields': {
            'customfield_12804': {'value': 'SM'},  # Game field
            'customfield_11214': {'value': 'Terra'},  # Team field
            'priority': {'name': 'Normal'}
        }
    }
    return jira_fields
```

#### Step 7.2: Create Jira Ticket
```python
def create_jira_ticket(jira_fields):
    """
    Create the actual Jira ticket using MCP tools
    """
    try:
        result = mcp_call('user-mcp-atlassian-jira-may', 'jira_create_issue', jira_fields)
        return {
            'success': True,
            'ticket_key': result['issue']['key'],
            'ticket_url': f"https://jira.playtika.com/browse/{result['issue']['key']}",
            'ticket_details': result['issue']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'suggested_fixes': suggest_creation_fixes(e)
        }
```

#### Step 7.3: Handle Post-Creation Updates
```python
def handle_post_creation_updates(ticket_result, required_updates):
    """
    Apply any necessary updates after ticket creation
    """
    if not required_updates:
        return ticket_result
    
    for update in required_updates:
        try:
            mcp_call('user-mcp-atlassian-jira-may', 'jira_update_issue', {
                'issue_key': ticket_result['ticket_key'],
                'fields': '{}',
                'additional_fields': update['fields']
            })
        except Exception as e:
            log_update_error(ticket_result['ticket_key'], update, e)
    
    return ticket_result
```

### Phase 8: Completion & Reporting

#### Step 8.1: Generate Success Report
```python
def generate_success_report(ticket_result, completion_results, qa_report):
    """
    Create final success report for user
    """
    success_report = {
        'ticket_created': {
            'key': ticket_result['ticket_key'],
            'url': ticket_result['ticket_url'],
            'status': 'Created successfully'
        },
        'auto_completion_summary': {
            'fields_completed': count_completed_fields(completion_results),
            'average_confidence': calculate_average_confidence(completion_results),
            'high_confidence_count': count_high_confidence(completion_results)
        },
        'qa_validation_summary': {
            'overall_status': qa_report['overall_status'],
            'critical_issues_resolved': len(qa_report['critical_issues']),
            'warnings_addressed': len(qa_report['warnings'])
        },
        'next_steps': generate_next_steps_recommendations(ticket_result)
    }
    return success_report
```

#### Step 8.2: Update Documentation
```python
def update_success_metrics(ticket_result, completion_results):
    """
    Track success metrics for continuous improvement
    """
    metrics_update = {
        'successful_creations': increment_counter(),
        'auto_completion_accuracy': track_accuracy(completion_results),
        'user_satisfaction': track_approval_rate(),
        'process_efficiency': calculate_time_savings()
    }
    return metrics_update
```

## Error Handling Workflows

### Missing Information Recovery
```
If critical information is missing:
1. **Apply JSON value analysis first** (check actual values for type/sizing)
2. **Apply intelligent auto-completion** using pattern recognition
3. **Flag uncertain completions** for user review with confidence scores
4. **Provide specific suggestions** for missing data with reasoning
5. **Allow iterative refinement** until complete

Special handling for coins/balance fields:
- Always check JSON examples for large values (>1M)
- Use DOUBLE PRECISION for fields with large monetary values
- Consider value ranges when determining precision requirements
```

### Validation Failures
```
If validation fails:
1. Identify specific failure points
2. Provide clear error descriptions
3. Suggest concrete fixes
4. Allow user to override with confirmation
```

### Jira API Issues
```
If ticket creation fails:
1. Parse API error response
2. Suggest field corrections
3. Retry with adjusted parameters
4. Escalate to manual creation if needed
```

## Success Criteria

### Technical Success
- ✅ Ticket created without errors
- ✅ All required fields populated correctly
- ✅ QA validation passes with no critical issues
- ✅ Auto-completion confidence >80% average

### User Experience Success  
- ✅ Natural language input processed correctly
- ✅ User approval obtained before creation
- ✅ Clear feedback provided throughout process
- ✅ Final ticket link and summary delivered

### Business Process Success
- ✅ Consistent ticket format maintained
- ✅ WIKI documentation properly integrated
- ✅ Team assignment and routing correct
- ✅ Audit trail and documentation updated

This comprehensive workflow ensures reliable, efficient, and user-friendly BI Jira ticket creation while maintaining high quality standards and technical accuracy.