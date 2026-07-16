# Slotomania Analytics Context

**Purpose**: Organized knowledge base for Slotomania analytics, data context, and approved queries.

## 📁 Context Structure

### 🎯 [squads/](squads/)
Feature-specific contexts organized by product squads/domains.

- **[rv/](squads/rv/)** - Rewarded Video squad (complete)
  - General RV context, tables, and approved queries
  - Shiny Show specialized placement context
- **Future squads**: Purchase Tools, Mid Term, Engagement, etc.

### 🧠 [business-knowledge/](business-knowledge/)
All foundational knowledge, references, and cross-squad business analysis.

#### Core Knowledge
- **[core-knowledge/glossary.md](business-knowledge/core-knowledge/glossary.md)** - Slotomania terminology and definitions
- **[core-knowledge/methodology.md](business-knowledge/core-knowledge/methodology.md)** - Analysis methodologies and best practices
- **[core-knowledge/business-context.md](business-knowledge/core-knowledge/business-context.md)** - Business context and game overview
- **[core-knowledge/table-schemas.md](business-knowledge/core-knowledge/table-schemas.md)** - Core data tables and schemas
- **[core-knowledge/data-overview.md](business-knowledge/core-knowledge/data-overview.md)** - Comprehensive data context
- **[core-knowledge/onboarding-context.md](business-knowledge/core-knowledge/onboarding-context.md)** - Analytics onboarding guide

#### Business Domains
- **[business-domains/cz-analysis/](business-knowledge/business-domains/cz-analysis/)** - Customer Zone analysis framework
- *Future domains*: Revenue analysis, retention, user lifecycle, etc.

#### References
- **[references/query-patterns.md](business-knowledge/references/query-patterns.md)** - Reusable SQL query examples
- **[references/tableau-mappings.md](business-knowledge/references/tableau-mappings.md)** - Tableau data source mappings
- **[references/table-reference.md](business-knowledge/references/table-reference.md)** - Table reference documentation
- **[references/validation-rules.md](business-knowledge/references/validation-rules.md)** - Data validation rules and checks

## 🧭 Navigation Guide

### For Feature-Specific Work:
1. **Check [squads/](squads/)** first for dedicated feature contexts
2. **Use [business-knowledge/core-knowledge/](business-knowledge/core-knowledge/)** for foundational understanding
3. **Reference [business-knowledge/references/](business-knowledge/references/)** for SQL patterns and technical details

### For Business Analysis:
1. **Check [business-knowledge/business-domains/](business-knowledge/business-domains/)** for cross-feature analysis frameworks
2. **Use [business-knowledge/core-knowledge/](business-knowledge/core-knowledge/)** for business context and methodology
3. **Apply [business-knowledge/references/](business-knowledge/references/)** for query patterns and validation

### For New Analysis:
1. **Start with [business-knowledge/core-knowledge/](business-knowledge/core-knowledge/)** to understand the domain
2. **Find relevant [squads/](squads/)** or [business-knowledge/business-domains/](business-knowledge/business-domains/)** context
3. **Use [business-knowledge/references/](business-knowledge/references/)** for query building and validation

## 📋 Content Standards

### Query Management
- **Only user-provided queries** are stored in context files
- **Separate context from queries** - context explains, queries implement
- **Categorize queries** by business purpose and use case

### File Organization
- **Consistent naming**: Use lowercase with dashes (e.g., `table-schemas.md`)
- **Clear structure**: Context files explain, query files implement
- **Navigation**: Each folder has overview/navigation documentation

### Maintenance
- **Squad-focused**: Feature work organized by product squads
- **Cross-reference**: Business domains span multiple squads
- **Evolving**: Structure grows as new squads and domains are added

---

*This context organization provides systematic access to Slotomania analytics knowledge while maintaining clear separation between different types of information and ensuring only approved content is preserved.*