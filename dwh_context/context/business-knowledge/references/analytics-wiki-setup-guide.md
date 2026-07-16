# Analytics WIKI Creator - Setup Guide for Team

## 🎯 What This Does

This tool helps you create standardized analytical data requirements documentation using our official Playtika template. It automates the entire process from template duplication to data population from Excel files.

## 📋 Quick Start

### 1. Copy the Rule File
Copy `analytics-wiki-creator.mdc` to your workspace's `.cursor/rules/` folder:
```
your-project/
└── .cursor/
    └── rules/
        └── analytics-wiki-creator.mdc
```

### 2. Configure MCP Servers
Add this to your `.cursor/mcp.json` file:

```json
{
  "mcpServers": {
    "user-mcp-atlassian-wiki": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "CONFLUENCE_URL": "https://wiki.playtika.com",
        "CONFLUENCE_USERNAME": "your-email@playtika.com",
        "CONFLUENCE_PERSONAL_TOKEN": "YOUR_CONFLUENCE_TOKEN"
      }
    },
    "excel": {
      "command": "uvx",
      "args": ["excel-mcp-server", "stdio"]
    }
  }
}
```

**Replace**:
- `your-email@playtika.com` → Your actual Playtika email
- `YOUR_CONFLUENCE_TOKEN` → Your Confluence personal access token

### 3. Get Your Confluence Token
1. Go to https://wiki.playtika.com
2. Profile → Personal Access Tokens
3. Create new token with read/write permissions
4. Copy token to your MCP config

## 🚀 How to Use

### Activation Commands
The agent activates ONLY when you use these specific phrases:

✅ **Correct triggers**:
- *"Create data requirements WIKI for the new XYZ feature"*
- *"I need to document analytics data requirements for ABC"*
- *"Use the WIKI data requirements template for the Login feature"*

❌ **Won't activate**:
- "Create a WIKI page" (too general)
- "Help with documentation" (not specific)
- "Make a new page" (not data requirements)

### Required Input
You'll need to provide:
1. **Feature name** (e.g., "Aviator", "Daily Dash", "Login System")
2. **Excel file** with your data requirements (must have "streaming" and "ETL" sheets)
3. **Feature details** for the General Info tab (owners, goals, KPIs, etc.)

### Example Usage Session
```
You: "Create data requirements WIKI for the Daily Rewards feature"

Agent: "I'll help you create analytical data requirements documentation for Daily Rewards. 
First, let me duplicate the official template..."

[Agent guides you through the entire process step by step]
```

## 📁 Excel File Requirements

Your Excel file should have exactly these sheets:

### "streaming" Sheet Structure
| Vertica Field Name | Vertica Data Type | JSON Field Name | Value Example | BA Comments | R&D Comments |
|-------------------|------------------|-----------------|---------------|-------------|--------------|
| event_date        | date             |                 |               |             |              |
| user_id           | integer          |                 |               |             |              |
| ...               | ...              |                 |               |             |              |

### "ETL" Sheet Structure  
| Field Name | Vertica Data Type | Source Table | Comments |
|-----------|------------------|--------------|----------|
| user_id   | integer          | users        | Primary key |
| ...       | ...              |              |         |

## 🔧 Troubleshooting

### Common Issues

**"MCP server not found"**
- Check `.cursor/mcp.json` syntax
- Restart Cursor after config changes
- Verify MCP servers are installed: `uvx mcp-atlassian`, `uvx excel-mcp-server`

**"Can't read Excel file"**
- Move Excel file to local drive (not OneDrive)
- Check file permissions
- Ensure sheets are named "streaming" and "ETL"

**"HTML parsing error in Confluence"**
- Agent will automatically retry with simplified content
- Usually resolves automatically

**"Permission denied on Confluence"**
- Verify your token has write permissions
- Check you're in the SLOT space
- Confirm email in MCP config is correct

### Getting Help
1. First: Check this troubleshooting section
2. Try: Restart Cursor and retry the command
3. Ask: May Edri (created this system) for advanced issues

## 📋 What the Agent Will Do

1. **Duplicate Template**: Creates new page from official template with proper tab structure
2. **General Info**: Helps you fill feature details (asks for approval before changes)
3. **Streaming Data**: Extracts data from your Excel "streaming" sheet
4. **ETL Data**: Extracts data from your Excel "ETL" sheet  
5. **Quality Check**: Verifies everything matches your requirements
6. **Final URL**: Provides link to completed WIKI page

## ✅ Success Checklist

After completion, your WIKI page should have:
- [ ] Proper location under "BI-BA Data Requirements"
- [ ] Three working tabs (General Info, Streaming, ETL)
- [ ] All data from your Excel file
- [ ] Proper table formatting
- [ ] JSON examples for streaming events
- [ ] Your approval on all content

## 🎯 Best Practices

1. **Prepare your Excel file first** - having structured data ready speeds up the process
2. **Be specific in your request** - mention "data requirements WIKI" clearly
3. **Review each step** - the agent asks for approval before making changes
4. **Keep Excel sheets named correctly** - "streaming" and "ETL" exactly
5. **Test with a small feature first** - get familiar with the workflow

---

**Created by**: May Edri  
**Last updated**: May 2026  
**Template source**: https://wiki.playtika.com/spaces/SLOT/pages/899952455/DATA+REQ+TEMP