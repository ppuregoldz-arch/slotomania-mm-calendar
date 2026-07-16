# Holy Moley Tableau Workbooks

This folder contains Tableau workbooks and dashboard configurations for Holy Moley feature analysis.

## Workbook Structure

### Primary Dashboards

1. **Holy Moley Historical Performance** (`holy_moley_historical_dashboard.twbx`)
   - Historical engagement metrics
   - Revenue and monetization trends
   - User behavior patterns
   - Seasonal performance variations

2. **Blast vs Holy Moley Comparison** (`blast_holy_moley_comparison.twbx`)
   - Side-by-side feature metrics
   - User engagement comparison
   - Revenue per user analysis
   - Pick acquisition patterns

3. **Re-launch Monitoring Dashboard** (`holy_moley_relaunch_monitoring.twbx`)
   - Real-time performance tracking
   - Key success metrics
   - User adoption rates
   - Revenue impact monitoring

### Supporting Workbooks

4. **User Segmentation Analysis** (`holy_moley_user_segments.twbx`)
   - CZ bucket performance
   - User tier engagement
   - Behavioral clustering
   - Retention analysis

5. **Configuration Validation** (`holy_moley_config_analysis.twbx`)
   - Prize distribution analysis
   - Pick cost optimization
   - Reward structure validation
   - Balance testing

## Data Source Configuration

### SQL Data Sources
Each workbook connects to validated SQL queries from `/queries/` folder:
- Custom SQL connections for complex analysis
- Parameterized queries for flexible filtering
- Optimized data extracts for performance

### Refresh Schedule
- **Historical data**: Static extracts (no refresh needed)
- **Monitoring dashboards**: Daily refresh during re-launch period
- **Comparison analysis**: Weekly refresh for trend analysis

## Dashboard Design Standards

### Visual Design
- Follow workspace chart-style standards
- Tableau color palette: ["#4e79a7", "#f28e2b", "#59a14f", "#e15759"]
- Consistent formatting and layout
- Clear titles and annotations

### Functionality
- Interactive filters for date ranges and user segments
- Drill-down capabilities for detailed analysis
- Export functionality for executive reporting
- Mobile-responsive design for stakeholder access

## Expected Deliverables

### Phase 1: Historical Analysis
- Historical performance dashboard with 2+ years of data
- Comparative analysis with Blast feature metrics
- User behavior patterns and segmentation insights

### Phase 2: Re-launch Preparation
- Configuration validation dashboard
- Success metrics definition and tracking
- Risk assessment and monitoring alerts

### Phase 3: Post-launch Monitoring
- Real-time performance tracking
- Success metric monitoring
- User adoption and engagement tracking
- Revenue impact assessment

## Data Validation Requirements

All dashboards include:
- Data source documentation
- Query validation status
- Known limitations and assumptions
- Update frequency and methodology

### Quality Assurance
- Manual validation against raw data
- Business logic verification
- Performance testing with expected user load
- Stakeholder review and approval

---

*All workbooks require data validation documentation*  
*Follow Tableau best practices for dashboard design and performance*