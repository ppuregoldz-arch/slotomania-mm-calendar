# Rules Organization

This folder contains all agent rules organized by category and activation type.

## Categories

### 01-always-live/ (ALWAYS LIVE)
Core technical standards and workflows that apply to all interactions.

### 02-agents-request-activated/ (REQUEST-ACTIVATED)  
Specialized agents that are activated only when explicitly requested or when working on specific features/tasks.

## Rule Activation

- **ALWAYS LIVE**: Rules that are applied automatically to every interaction
- **REQUEST-ACTIVATED**: Rules that are only activated when specifically requested or relevant to the task

## Current Rules Summary

### **ALWAYS LIVE RULES** (5 rules)
- **SQL Standards** - Unified query writing, formatting & documentation standards
- **Query Validation** - Data validation requirements and accuracy checks
- **Vertica Workflow** - Database connection, validation & project organization
- **Chart Style** - Visualization formatting conventions
- **Agent Identity** - Slotomania Analytics Specialist role & workspace structure

### **REQUEST-ACTIVATED AGENTS** (3 agents)

#### **Analytics WIKI Creator** - [`analytics-wiki-creator.mdc`]
- **Description**: Creates structured data requirements documentation using Playtika templates
- **Activation**: Only when explicitly asked to create data requirements WIKI pages
- **Status**: REQUEST-ACTIVATED

#### **Data Validation Agent** - [`data-validation-agent.mdc`]
- **Description**: Comprehensive data quality assurance and validation specialist
- **Activation**: Use when explicitly requested for data quality assurance and validation
- **Status**: REQUEST-ACTIVATED

#### **Agent Development Guide** - [`agent-development-guide.mdc`]
- **Description**: Standardized guide for creating new request-activated agents with consistent structure
- **Activation**: Reference guide for agent development process and standards
- **Status**: REQUEST-ACTIVATED

## Future Expansion

The `02-agents-request-activated/` folder is designed to hold future specialized agents as they are developed. Each agent should be self-contained with clear activation triggers and specific use cases. Use the Agent Development Guide for creating new agents.