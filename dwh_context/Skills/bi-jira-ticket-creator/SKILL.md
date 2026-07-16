---
name: bi-jira-ticket-creator
description: Create BI Jira tickets from natural language input with QA validation, WIKI integration, and intelligent field completion. Use when user wants to create Jira tickets for database schema changes, table modifications, or BI-related tasks.
---

# BI Jira Ticket Creator Skill

## Purpose
Streamline creation of Business Intelligence Jira tickets by converting natural language requirements into structured, QA-validated tickets with automatic field completion and WIKI integration.

## When to Use This Skill
**Use this skill when asked to create BI Jira tickets.**

**Examples:**
- "Create a Jira ticket to add revenue_source column to payments table"
- "I need a BI ticket for removing old columns from user profile table"
- "Generate Jira ticket for stamp cards table schema changes"
- "Create ticket for consuming new segmentation table data"

## Skill Capabilities

### Core Features
- **Natural Language Processing**: Parse free-form user requirements
- **QA Validation**: Comprehensive technical validation against multiple sources
- **WIKI Integration**: Fetch and validate against Confluence documentation
- **Intelligent Field Completion**: Auto-complete missing data types and topic names
- **Required Field Population**: Automatically set Game, Team, and other mandatory fields
- **Structured Template**: Generate consistent ticket format with all required sections

### Validation Sources
- **WIKI Documentation**: Real-time Confluence content fetching and parsing
- **Table Schema Analysis**: Existing column patterns and data type validation
- **Context Repository**: Internal documentation and query history
- **Business Logic**: Cross-referencing with established naming conventions
- **Vertica Compatibility**: Data type and constraint validation

## Default Configuration

### Jira Settings
- **Project**: BI Team (BIT)
- **Issue Type**: Task
- **Priority**: Normal
- **Game**: SM (for Slotomania-related tickets)
- **Team**: Terra (default, unless specified otherwise)
- **Assignee**: Boaz Priel (default, can be overridden)

### MCP Server Requirements
- **Jira Server**: `user-mcp-atlassian-jira-may` for ticket management
- **WIKI Server**: `user-mcp-atlassian-wiki` for documentation access
- **Vertica Server**: `user-mcp-alchemy-sm` for schema validation

## Workflow Overview

### Step 1: Input Processing
1. **Parse natural language** user requirements
2. **Extract key information**: table names, field changes, action types
3. **Identify WIKI references** if provided

### Step 2: WIKI Integration
1. **Fetch WIKI documentation** using MCP Confluence tools
2. **Parse content** for field mappings, JSON examples, parameter tables
3. **Extract business context** and validation data

### Step 3: Intelligent Field Completion
1. **Detect missing information** (data types, topic names, descriptions)
2. **Apply pattern recognition** and table schema analysis
3. **Search WIKI content** for missing field mappings
4. **Calculate confidence scores** for all auto-completions

### Step 4: QA Validation
1. **Technical validation**: Data types, naming conventions, constraints
2. **Business logic validation**: Field purposes, value consistency
3. **WIKI cross-reference**: Validate against documentation
4. **Generate validation report** with confidence scores and issues

### Step 5: User Review & Approval
1. **Present formatted ticket** with complete structure
2. **Show QA validation results** and auto-completion details
3. **Allow modifications** based on findings
4. **Get explicit approval** before ticket creation

### Step 6: Ticket Creation
1. **Populate required fields** automatically (Game, Team, etc.)
2. **Create Jira ticket** using MCP tools
3. **Handle post-creation updates** if needed
4. **Provide ticket link** and summary to user

## Template Structure

### Basic Ticket Information
- **Summary**: Descriptive title based on user requirements
- **Project, Issue Type, Priority**: Standard BI settings
- **Game, Team, Assignee**: Auto-populated defaults

### Description Template
```markdown
**Topic Name**: [Business context from WIKI or user input]

**Table Name**: [Full qualified table name]

**Action**: [Add Column / Delete Column / Rename Column / Consuming New Table / Multiple Actions]

**Changes Structure**:
| Action | Field Name (Vertica) | Field Name (Topic) | Data Type |
|--------|---------------------|-------------------|-----------|
| [Action] | [Technical column name] | [Business field name] | [SQL data type with constraints] |

**JSON Example**:
```json
[Complete JSON structure with existing and new fields]
```

**WIKI Page**: [URL if documentation exists]

**Additional Notes**: [Context, requirements, business logic]
```

## Quality Assurance Features

### Auto-Completion Intelligence
- **High Confidence (85%+)**: Auto-applied without user review
- **Medium Confidence (70-85%)**: Presented for user review
- **Low Confidence (<70%)**: Flagged for manual specification
- **Pattern Recognition**: Field naming conventions and business purposes
- **Schema Analysis**: Similar column detection and type inference

### Validation Checks
- **Data Types**: Vertica compatibility and appropriate sizing
- **Naming Conventions**: Snake_case compliance and reserved word checking
- **Business Logic**: Value consistency and constraint appropriateness
- **WIKI Alignment**: Field mapping accuracy and documentation compliance
- **Table Validation**: Existence checking and accessibility verification

## Error Handling

### Missing Information
- **Incomplete Specifications**: Prompt for clarification or auto-complete with confidence scoring
- **Invalid Table Names**: Suggest corrections based on known schemas
- **Conflicting Requirements**: Flag inconsistencies and request resolution

### Technical Issues
- **WIKI Access Problems**: Gracefully handle unavailable documentation
- **Jira API Errors**: Provide clear error messages and retry mechanisms
- **Validation Failures**: Offer specific suggestions for resolution

## Success Metrics

### Implementation Success
- **First Live Ticket**: BIT-26997 (Stamp Cards schema updates)
- **Validation Accuracy**: 100% successful ticket creation rate
- **Auto-Completion Effectiveness**: 90%+ confidence on field completions
- **User Satisfaction**: Approval workflow prevents errors effectively

### Process Efficiency
- **Time Reduction**: From requirements to ticket in under 5 minutes
- **Error Prevention**: QA validation catches issues before creation
- **Consistency**: All tickets follow standardized format
- **Knowledge Integration**: WIKI content automatically incorporated

## Usage Instructions

### Basic Usage
```
User: "I need to add multiplier columns to the stamp cards table, here's the WIKI: [URL]"
```

### Complex Multi-Action Usage
```
User: "Update dwh.fact_payments table:
- Rename old_revenue to legacy_revenue  
- Delete temp_columns from last month
- Add new segmentation fields based on this WIKI: [URL]"
```

### The skill will:
1. Parse all requested changes
2. Fetch and validate against WIKI
3. Auto-complete missing field information
4. Generate comprehensive QA report
5. Present structured ticket for approval
6. Create ticket with all required fields populated
7. Provide final ticket link and summary

## Integration Notes

This skill integrates with the existing analytical workspace structure documented in `outputs/bi_jira_ticket_skill_development_2026-06-10/` and leverages the comprehensive QA validation framework and intelligent field completion system developed during the initial implementation phase.

For detailed technical specifications, see:
- `business-context/jira-field-mappings.md` - Jira field requirements and mappings
- `workflow/ticket-creation-workflow.md` - Complete step-by-step process documentation