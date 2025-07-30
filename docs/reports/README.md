# BMAD Reports Documentation

## 📁 Directory Structure

```
docs/reports/
├── agent-improvements/     # Permanent improvement reports
│   ├── MOBILE_DEVELOPER_AGENT_IMPROVEMENT_REPORT.md
│   ├── RND_AGENT_IMPROVEMENT_REPORT.md
│   ├── RELEASE_MANAGER_AGENT_IMPROVEMENT_REPORT.md
│   └── RETROSPECTIVE_AGENT_IMPROVEMENT_REPORT.md
├── temporary/             # Auto-generated temporary reports
│   ├── *_report_*.json   # JSON export files
│   ├── *_report_*.csv    # CSV export files
│   ├── *_report_*.md     # Markdown reports
│   ├── TestApp_config_*.json
│   └── component_export_*.json
└── README.md             # This file
```

## 📋 File Categories

### 🔒 Permanent Files (agent-improvements/)
- **Purpose:** Long-term documentation of agent improvements
- **Content:** Detailed analysis, test results, quality improvements
- **Retention:** Keep indefinitely, version controlled
- **Examples:** `*IMPROVEMENT_REPORT.md`

### 🗑️ Temporary Files (temporary/)
- **Purpose:** Auto-generated during testing and development
- **Content:** Test outputs, exports, temporary data
- **Retention:** Clean up regularly, not version controlled
- **Examples:** `*_report_*.json`, `component_export_*.json`

## 🧹 Cleanup Guidelines

### Automatic Cleanup
- Temporary files are automatically ignored by `.gitignore`
- Regular cleanup scripts should target `docs/reports/temporary/`

### Manual Cleanup
```bash
# Clean temporary reports
rm -rf docs/reports/temporary/*

# Keep only improvement reports
find docs/reports/temporary/ -name "*IMPROVEMENT_REPORT.md" -delete
```

## 📊 Report Types

### Agent Improvement Reports
- **Format:** Markdown
- **Location:** `agent-improvements/`
- **Content:** Test coverage, quality improvements, business value
- **Frequency:** Generated after each agent completion

### Temporary Reports
- **Format:** JSON, CSV, Markdown
- **Location:** `temporary/`
- **Content:** Test outputs, exports, temporary data
- **Frequency:** Generated during testing

## 🔄 Workflow Integration

### During Development
1. Generate temporary reports in `temporary/`
2. Analyze and process data
3. Create improvement reports in `agent-improvements/`
4. Clean up temporary files

### Before Commits
1. Ensure temporary files are in correct location
2. Verify `.gitignore` excludes temporary files
3. Commit only permanent improvement reports

## 📈 Coverage Tracking

### Current Status
- **Total Project Coverage:** 56%
- **Target Coverage:** 70% overall, 90% for essential components
- **Success Rate:** 99-100%

### Agent Coverage Status
- ✅ **MobileDeveloperAgent:** 73% coverage
- ✅ **RnDAgent:** 71% coverage  
- ✅ **ReleaseManagerAgent:** 71% coverage
- ✅ **RetrospectiveAgent:** 70% coverage
- 🔄 **FeedbackAgent:** 25% coverage (next target)
- 🔄 **AccessibilityAgent:** 24% coverage
- 🔄 **SecurityDeveloper:** 27% coverage
- 🔄 **DataEngineer:** 27% coverage

## 🎯 Next Steps

1. **Continue agent improvements** following the established workflow
2. **Maintain documentation organization** as outlined above
3. **Regular cleanup** of temporary files
4. **Monitor coverage progress** towards 70% target 