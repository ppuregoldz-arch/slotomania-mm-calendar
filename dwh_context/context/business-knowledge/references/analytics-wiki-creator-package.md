# Analytics WIKI Creator - Distribution Package

## 📦 Files Your Coworkers Need

### ✅ **Essential Files** (Must Have):

1. **`analytics-wiki-creator.mdc`** 
   - 📍 Location: `.cursor/rules/analytics-wiki-creator.mdc`
   - 🎯 Purpose: The main Cursor rule file
   - 📝 Instructions: Copy this to your `.cursor/rules/` folder (root level, not in subfolders)

2. **`mcp-config-example.json`**
   - 📍 Location: `.cursor/rules/analytics-wiki-creator/mcp-config-example.json`
   - 🎯 Purpose: MCP server configuration template
   - 📝 Instructions: Use this to update your `.cursor/mcp.json` file

3. **`setup-guide.md`**
   - 📍 Location: `.cursor/rules/analytics-wiki-creator/setup-guide.md`
   - 🎯 Purpose: Complete setup instructions
   - 📝 Instructions: Follow this step-by-step to configure everything

### 📖 **Helpful Files** (Recommended):

4. **`usage-examples.md`**
   - 📍 Location: `.cursor/rules/analytics-wiki-creator/usage-examples.md`
   - 🎯 Purpose: How to trigger the tool and example workflows
   - 📝 Use: Reference when you need to use the tool

5. **`troubleshooting.md`**
   - 📍 Location: `.cursor/rules/analytics-wiki-creator/troubleshooting.md`
   - 🎯 Purpose: Common issues and solutions
   - 📝 Use: When things don't work as expected

6. **`excel-template-structure.md`**
   - 📍 Location: `.cursor/rules/analytics-wiki-creator/excel-template-structure.md`
   - 🎯 Purpose: How to structure your Excel files
   - 📝 Use: Before creating Excel files for data requirements

## 🚀 **Quick Setup Steps for Coworkers**:

### Step 1: Copy Files
```
your-project/
└── .cursor/
    └── rules/
        └── analytics-wiki-creator.mdc    ← Copy this file here
```

### Step 2: Configure MCP
- Open your `.cursor/mcp.json` file
- Add the configuration from `mcp-config-example.json`
- Replace with your email and Confluence token

### Step 3: Test
- Restart Cursor
- Say: *"Create data requirements WIKI for TestFeature"*
- Should activate the tool

## 📁 **How to Share These Files**:

### Option 1: Email Package
Send these files via email:
- `analytics-wiki-creator.mdc`
- `mcp-config-example.json` 
- `setup-guide.md`
- `usage-examples.md`
- `troubleshooting.md`

### Option 2: Shared Drive
Copy this entire folder structure to shared drive:
```
Analytics-WIKI-Creator-Package/
├── analytics-wiki-creator.mdc          ← Essential
├── analytics-wiki-creator/             ← Documentation folder
│   ├── mcp-config-example.json         ← Essential
│   ├── setup-guide.md                  ← Essential
│   ├── usage-examples.md               ← Helpful
│   ├── troubleshooting.md              ← Helpful
│   └── excel-template-structure.md     ← Helpful
```

### Option 3: Individual Files
If sharing one by one:
1. First: `analytics-wiki-creator.mdc` + `setup-guide.md`
2. Then: `mcp-config-example.json`
3. Later: Other documentation files as needed

## ⚠️ **Critical Reminders for Team**:

1. **Rule file location**: Must be in `.cursor/rules/` (root), not in subfolders
2. **Personal tokens**: Each person needs their own Confluence token
3. **MCP setup**: Must be configured correctly or tool won't work
4. **Trigger phrases**: Only works with specific phrases like "Create data requirements WIKI for [feature]"
5. **Excel structure**: Files must have "streaming" and "ETL" sheets exactly

## 📞 **Support**:
- First: Check `troubleshooting.md`
- Questions: Ask May Edri
- Issues: Verify setup with `setup-guide.md`

---

**Package created by**: May Edri  
**Date**: May 2026  
**Version**: 1.0 - Initial release