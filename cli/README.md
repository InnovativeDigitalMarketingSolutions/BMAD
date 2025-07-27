# BMAD CLI Tools

## 📋 Overview

Deze directory bevat alle CLI tools voor het BMAD systeem, georganiseerd voor eenvoudige toegang en onderhoud.

## 🛠️ Available CLI Tools

### **🔐 Advanced Policy CLI**
- **File**: `advanced_policy_cli.py`
- **Purpose**: Beheer van geavanceerde policies met complexe conditions
- **Usage**: `python3 cli/advanced_policy_cli.py --help`

### **🚀 Integrated Workflow CLI**
- **File**: `integrated_workflow_cli.py`
- **Purpose**: Beheer van geïntegreerde workflows
- **Usage**: `python3 cli/integrated_workflow_cli.py --help`

### **📊 Performance Monitor CLI**
- **File**: `performance_monitor_cli.py`
- **Purpose**: Real-time performance monitoring
- **Usage**: `python3 cli/performance_monitor_cli.py --help`

### **🧪 Test Sprites CLI**
- **File**: `test_sprites_cli.py`
- **Purpose**: Component testing en validation
- **Usage**: `python3 cli/test_sprites_cli.py --help`

### **🔗 Repository Integration CLI**
- **File**: `repository_integration_cli.py`
- **Purpose**: Testen van repository integraties
- **Usage**: `python3 cli/repository_integration_cli.py --help`

### **🔄 LangGraph CLI**
- **File**: `langgraph_cli.py`
- **Purpose**: LangGraph workflow beheer
- **Usage**: `python3 cli/langgraph_cli.py --help`

### **🔔 Webhook CLI**
- **File**: `webhook_cli.py`
- **Purpose**: Webhook notification beheer
- **Usage**: `python3 cli/webhook_cli.py --help`

### **🎨 Figma CLI**
- **File**: `figma_cli.py`
- **Purpose**: Figma API integratie en component generatie
- **Usage**: `python3 cli/figma_cli.py help`

### **📁 Project CLI**
- **File**: `project_cli.py`
- **Purpose**: Project management en ClickUp integratie
- **Usage**: `python3 cli/project_cli.py --help`

### **📋 Projects CLI**
- **File**: `projects_cli.py`
- **Purpose**: Project management met interactieve modus
- **Usage**: `python3 cli/projects_cli.py --help`

### **🔗 ClickUp CLI**
- **File**: `bmad_cli_clickup.py`
- **Purpose**: ClickUp workflow management
- **Usage**: `python3 cli/bmad_cli_clickup.py --help`

## 🚀 Quick Start

### **Installation**
```bash
# Zorg dat je in de BMAD root directory bent
cd /path/to/BMAD

# Activeer virtual environment
source .venv/bin/activate

# Test een CLI tool
python3 cli/advanced_policy_cli.py list-policies
```

### **Common Commands**

#### **Policy Management**
```bash
# List alle policies
python3 cli/advanced_policy_cli.py list-policies

# Show policy details
python3 cli/advanced_policy_cli.py show-policy advanced_access_control

# Evaluate policy
python3 cli/advanced_policy_cli.py evaluate-policy advanced_access_control test_request.json
```

#### **Workflow Management**
```bash
# List workflows
python3 cli/integrated_workflow_cli.py list-workflows

# Execute workflow
python3 cli/integrated_workflow_cli.py execute product-development --level full

# Test integrations
python3 cli/integrated_workflow_cli.py test-integrations
```

#### **Performance Monitoring**
```bash
# Start monitoring
python3 cli/performance_monitor_cli.py start-monitoring

# Show system performance
python3 cli/performance_monitor_cli.py system-summary

# Show agent performance
python3 cli/performance_monitor_cli.py agent-summary product-owner
```

#### **Component Testing**
```bash
# List test sprites
python3 cli/test_sprites_cli.py list-sprites

# Test component
python3 cli/test_sprites_cli.py test-component AgentStatus

# Export test report
python3 cli/test_sprites_cli.py export-report
```

## 📁 Directory Structure

```
cli/
├── __init__.py                    # Package initialization
├── README.md                      # This file
├── advanced_policy_cli.py         # Advanced Policy Engine CLI
├── integrated_workflow_cli.py     # Integrated Workflow CLI
├── performance_monitor_cli.py     # Performance Monitor CLI
├── test_sprites_cli.py           # Test Sprites CLI
├── repository_integration_cli.py  # Repository Integration CLI
├── langgraph_cli.py              # LangGraph CLI
├── webhook_cli.py                # Webhook CLI
├── figma_cli.py                  # Figma CLI
├── project_cli.py                # Project CLI
├── projects_cli.py               # Projects CLI
└── bmad_cli_clickup.py           # ClickUp CLI
```

## 🔧 Development

### **Adding New CLI Tools**

1. **Create the CLI file** in the `cli/` directory
2. **Update imports** to use correct path:
   ```python
   # Add BMAD to path
   sys.path.append(str(Path(__file__).parent.parent))
   ```
3. **Update `__init__.py`** to include the new CLI class
4. **Add documentation** to this README
5. **Test the CLI** to ensure it works correctly

### **Testing CLI Tools**

```bash
# Test help command
python3 cli/[tool_name].py --help

# Test basic functionality
python3 cli/[tool_name].py [command]

# Test with verbose logging
python3 -u cli/[tool_name].py [command] 2>&1 | tee test_output.log
```

## 📚 Documentation

Voor gedetailleerde documentatie van elke CLI tool, zie:
- **Advanced Policy Engine**: `../ADVANCED_POLICY_ENGINE_README.md`
- **Integrated Workflows**: `../AGENT_WORKFLOW_INTEGRATION_README.md`
- **Performance Monitor**: `../PERFORMANCE_MONITOR_INTEGRATION_README.md`
- **Test Sprites**: `../TEST_SPRITES_INTEGRATION_README.md`
- **Repository Integrations**: `../REPOSITORY_INTEGRATIONS_README.md`

## 🔍 Troubleshooting

### **Common Issues**

1. **ModuleNotFoundError: No module named 'bmad'**
   - **Solution**: Zorg dat je in de BMAD root directory bent
   - **Check**: `pwd` should show `/path/to/BMAD`

2. **Import errors**
   - **Solution**: Check of de import paths correct zijn
   - **Verify**: `sys.path.append(str(Path(__file__).parent.parent))`

3. **Permission denied**
   - **Solution**: Make CLI tools executable
   - **Command**: `chmod +x cli/*.py`

### **Debug Mode**

```bash
# Enable debug logging
export PYTHONPATH=/path/to/BMAD:$PYTHONPATH
python3 -u cli/[tool_name].py [command] 2>&1 | tee debug.log
```

## 📞 Support

Voor vragen en ondersteuning:
- **Issues**: GitHub issues
- **Documentation**: Zie de README bestanden in de root directory
- **Examples**: Zie de help output van elke CLI tool

---

**BMAD CLI Tools** - Georganiseerde command-line interface tools voor het BMAD systeem 🚀 