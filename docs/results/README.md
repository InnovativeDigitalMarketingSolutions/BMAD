# BMAD Results Documentation

## 📁 Directory Structure

```
docs/results/
├── README.md                  # This file
└── (temporary results files)  # Auto-generated during development
```

## 🎯 Purpose

Deze directory is bedoeld voor **tijdelijke resultaten** die gegenereerd worden tijdens development en testing.

## 🧹 Cleanup Policy

### **Temporary Files**
- **Purpose**: Test outputs, planning exports, temporary data
- **Retention**: Clean up regularly, not version controlled
- **Examples**: `*_planning_*.md`, `*_results_*.md`, `*_export_*.json`

### **Recent Cleanup**
De volgende bestanden zijn opgeschoond:
- ❌ `bmad_frontend_planning_20250726_145620.md`
- ❌ `BMAD_CLICKUP_WORKFLOW_RESULTS.md`
- ❌ `TEMPLATE_ADAPTATION_TEST_RESULTS.md`
- ❌ `bmad_planning_bmad-frontend_20250726_145541.json`

### **Consolidated Planning**
Alle planning documenten zijn geconsolideerd in:
- ✅ `docs/deployment/BMAD_MASTER_PLANNING.md`

## 📋 Guidelines

### **Voor Nieuwe Resultaten**
1. **Temporary**: Plaats in `docs/results/` met timestamp
2. **Permanent**: Plaats in `docs/reports/` of `docs/deployment/`
3. **Cleanup**: Verwijder na analyse en documentatie

### **Voor Planning Documenten**
1. **Consolidate**: Voeg toe aan `BMAD_MASTER_PLANNING.md`
2. **Archive**: Verwijder oude planning documenten
3. **Update**: Houd master planning up-to-date

## 🔄 Workflow

### **During Development**
1. Generate temporary results in `docs/results/`
2. Analyze and document findings
3. Update master planning if needed
4. Clean up temporary files

### **Before Commits**
1. Ensure temporary files are properly categorized
2. Verify master planning is up-to-date
3. Clean up old temporary files

---

**BMAD Results** - Tijdelijke resultaten en exports 📊 