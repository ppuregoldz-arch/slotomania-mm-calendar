# BI Jira Ticket Creation Skill Development

## Conversation Summary
**Date**: June 10, 2026  
**Topic**: Development of automated BI Jira ticket creation process  
**Participants**: User and Slotomania Analytics Specialist  

## Context & Background

The user initially asked about opening Jira, which led to discovering they needed a streamlined process for creating Business Intelligence (BI) related Jira tickets. These tickets are used for managing database schema changes, table modifications, and data structure updates.

## Problem Identified

Manual creation of BI Jira tickets for database changes is repetitive and time-consuming. The user needs a standardized way to create tickets for:
- Adding columns to tables
- Deleting columns from tables  
- Consuming new tables
- Other database schema modifications

## Solution Approach

Develop a Cursor skill that:
1. Takes free-form natural language input describing the desired changes
2. Converts this into a structured BI Jira ticket template
3. Shows formatted ticket for approval before submission
4. Creates the actual Jira ticket using MCP tools

## Workflow Process

### Step 1: User Input
- User provides free-form description of database changes needed
- Natural language, no specific format required

### Step 2: Template Generation  
- System parses input and structures it into standardized BI ticket format
- All required fields populated based on user input
- Consistent formatting applied

### Step 3: Review & Approval
- Formatted ticket shown to user for review
- User can request modifications or approve as-is
- No ticket created until explicit approval given

### Step 4: Intelligent Field Completion  
- System automatically fills missing data types using pattern recognition and table analysis
- System searches WIKI content for missing topic names using multiple search strategies
- Confidence scoring applied to all auto-completions
- High-confidence completions auto-applied, others flagged for review

### Step 5: Jira Ticket Creation
- Upon approval, system uses MCP tools to create actual Jira ticket
- Ticket created in correct project with proper assignee and auto-completed fields

## Technical Implementation

### Default Settings
- **Project**: BI Team (BIT)
- **Issue Type**: Task  
- **Priority**: Normal
- **Game**: SM (for Slotomania-related tickets)
- **Team**: Terra (default, unless specified otherwise)
- **Assignee**: Boaz Priel (unless specified otherwise)

### MCP Server Used
- **Server**: `user-mcp-atlassian-jira-may`
- **Primary Tool**: `jira_create_issue`
- **Supporting Tools**: `jira_get_all_projects`, `jira_search_fields`, `jira_get_field_options`, `jira_update_issue`

## Template Structure Defined

### Basic Ticket Info
- **Summary**: Descriptive title of the change
- **Assignee**: Boaz Priel (default, can be overridden)

### Description Template
```
**Topic Name**: [Business context/project name]

**Table Name**: [Full table name, e.g., dwh.sm_fact_payments]

**Action**: [Add Column / Delete Column / Consuming New Table]

**Changes Structure**:
| Action | Field Name (Vertica) | Field Name (Topic) | Data Type |
|--------|---------------------|-------------------|-----------|
| [Action] | [Column name] | [Business name] | [Data type] |

**JSON Example**: 
```json
{
  "field_name": "example_value"
}
```

**WIKI Page**: [Link if exists]

**Additional Notes**: [Context, requirements, etc.]
```

## Key Benefits

1. **Standardization**: All BI tickets follow consistent format with proper field mappings
2. **Efficiency**: Reduces time from description to ticket creation with intelligent auto-completion
3. **Accuracy**: QA validation ensures technical correctness and WIKI cross-referencing
4. **Intelligence**: Auto-completes missing data types and topic names using multiple data sources
5. **Review Process**: Built-in approval step with confidence scoring prevents errors
6. **Automation**: Leverages MCP tools for seamless Jira integration with required field population
7. **Quality Assurance**: Comprehensive validation against data types, naming conventions, and business logic
8. **Continuous Learning**: System improves through pattern recognition and user feedback

## Next Steps

1. Create the Cursor skill implementation
2. Test with sample ticket creation scenarios
3. Refine template based on real-world usage
4. Deploy for team use

## Additional Considerations Discussed

### Suggested Enhancements
- Business justification field
- Impact assessment (Low/Medium/High)
- Dependencies tracking
- Rollback plan specification
- Environment deployment path
- Default values for new columns
- Nullable/not null constraints
- Estimated effort tracking

### Questions for Future Refinement
- Should we include default values for new columns?
- Do we need nullable/not null constraint specifications?
- Should estimated effort or due dates be included?
- Are there specific labels or components to auto-assign?

## Technical Notes

The solution leverages the existing MCP infrastructure with comprehensive Jira tools available in the `user-mcp-atlassian-jira-may` server, including capabilities for creating, updating, searching, and managing Jira issues programmatically. The system automatically handles required custom fields (Game, Team) and provides WIKI-based validation for technical accuracy.

## Implementation Success

**First Live Ticket Created**: BIT-26997 - Stamp Cards table schema updates
- **Link**: https://jira.playtika.com/browse/BIT-26997  
- **Status**: Successfully created with QA validation
- **WIKI Integration**: Validated against Stamp Cards BI/BA events documentation
- **Team Assignment**: Corrected to "Terra" (default team setting established)