# DocumentationAgent Project Setup Workflow

## Overview

Dit document beschrijft de workflow voor de DocumentationAgent om automatisch project documentatie op te zetten bij de start van nieuwe projecten. De agent haalt guides, lessons learned, en best practices op en maakt project-specifieke kopieën beschikbaar.

**Versie**: 1.0  
**Status**: Actief  
**Gebruik**: Project initialization workflow

---

## Workflow Overview

### **Trigger**: New Project Initialization
Wanneer een nieuw project wordt gestart, wordt de DocumentationAgent automatisch geactiveerd om:

1. **Core Documentation Files** ophalen
2. **Project-Specific Copies** maken
3. **Project Context** toevoegen
4. **Documentation Structure** opzetten
5. **Accessibility** voor agents en Cursor AI

---

## Step-by-Step Workflow

### **Step 1: Project Detection**
```python
async def detect_new_project(self, project_path: str) -> bool:
    """Detect if this is a new project requiring documentation setup."""
    # Check for project indicators
    indicators = [
        "new_project_flag",
        "project_initialization",
        "first_commit",
        "project_setup_request"
    ]
    
    # Return True if new project detected
    return await self._check_project_indicators(project_path, indicators)
```

### **Step 2: Core Documentation Collection**
```python
async def collect_core_documentation(self) -> Dict[str, Any]:
    """Collect core documentation files from BMAD guides."""
    core_files = {
        "lessons_learned": "docs/guides/LESSONS_LEARNED_GUIDE.md",
        "best_practices": "docs/guides/BEST_PRACTICES_GUIDE.md",
        "mcp_integration": "docs/guides/MCP_INTEGRATION_GUIDE.md",
        "development_workflow": "docs/guides/DEVELOPMENT_WORKFLOW_GUIDE.md",
        "testing_guide": "docs/guides/TESTING_GUIDE.md",
        "quality_guide": "docs/guides/QUALITY_GUIDE.md"
    }
    
    return await self._fetch_core_files(core_files)
```

### **Step 3: Project-Specific Customization**
```python
async def customize_for_project(self, core_docs: Dict[str, Any], project_context: Dict[str, Any]) -> Dict[str, Any]:
    """Customize core documentation for specific project context."""
    customized_docs = {}
    
    for doc_type, content in core_docs.items():
        customized_content = await self._customize_document(
            content=content,
            project_name=project_context.get("project_name"),
            project_type=project_context.get("project_type"),
            team_size=project_context.get("team_size"),
            technology_stack=project_context.get("technology_stack"),
            development_approach=project_context.get("development_approach")
        )
        
        customized_docs[doc_type] = customized_content
    
    return customized_docs
```

### **Step 4: Project Documentation Structure**
```python
async def create_project_documentation_structure(self, project_path: str) -> Dict[str, str]:
    """Create project-specific documentation structure."""
    structure = {
        "project_guides": f"{project_path}/docs/guides/",
        "project_lessons": f"{project_path}/docs/lessons-learned/",
        "project_best_practices": f"{project_path}/docs/best-practices/",
        "project_templates": f"{project_path}/docs/templates/",
        "project_resources": f"{project_path}/docs/resources/"
    }
    
    # Create directories
    for path in structure.values():
        await self._create_directory(path)
    
    return structure
```

### **Step 5: Documentation Deployment**
```python
async def deploy_project_documentation(self, customized_docs: Dict[str, Any], structure: Dict[str, str]) -> bool:
    """Deploy customized documentation to project structure."""
    deployment_map = {
        "lessons_learned": f"{structure['project_lessons']}/LESSONS_LEARNED.md",
        "best_practices": f"{structure['project_best_practices']}/BEST_PRACTICES.md",
        "mcp_integration": f"{structure['project_guides']}/MCP_INTEGRATION.md",
        "development_workflow": f"{structure['project_guides']}/DEVELOPMENT_WORKFLOW.md",
        "testing_guide": f"{structure['project_guides']}/TESTING_GUIDE.md",
        "quality_guide": f"{structure['project_guides']}/QUALITY_GUIDE.md"
    }
    
    success = True
    for doc_type, file_path in deployment_map.items():
        if doc_type in customized_docs:
            success &= await self._write_document(file_path, customized_docs[doc_type])
    
    return success
```

---

## Core Documentation Files

### **1. Lessons Learned Guide**
**Source**: `docs/guides/LESSONS_LEARNED_GUIDE.md`
**Purpose**: Project-specifieke lessons learned en development patterns
**Customization**: 
- Project-specifieke context toevoegen
- Technology stack aanpassingen
- Team-specifieke patterns

### **2. Best Practices Guide**
**Source**: `docs/guides/BEST_PRACTICES_GUIDE.md`
**Purpose**: Development best practices voor het project
**Customization**:
- Project-specifieke best practices
- Technology stack guidelines
- Team workflow patterns

### **3. MCP Integration Guide**
**Source**: `docs/guides/MCP_INTEGRATION_GUIDE.md`
**Purpose**: MCP integration patterns en best practices
**Customization**:
- Project-specifieke MCP tools
- Integration patterns
- Testing strategies

### **4. Development Workflow Guide**
**Source**: `docs/guides/DEVELOPMENT_WORKFLOW_GUIDE.md`
**Purpose**: Development workflow en processen
**Customization**:
- Project-specifieke workflow
- Team processen
- Tool configurations

### **5. Testing Guide**
**Source**: `docs/guides/TESTING_GUIDE.md`
**Purpose**: Testing strategies en best practices
**Customization**:
- Project-specifieke testing approach
- Test coverage requirements
- Testing tools configuration

### **6. Quality Guide**
**Source**: `docs/guides/QUALITY_GUIDE.md`
**Purpose**: Quality assurance en code quality
**Customization**:
- Project-specifieke quality standards
- Code review processen
- Quality metrics

---

## Project Context Customization

### **Project Information**
```python
project_context = {
    "project_name": "Project Name",
    "project_type": "Web Application | API | Mobile App | Library",
    "team_size": "Small | Medium | Large",
    "technology_stack": ["Python", "React", "PostgreSQL"],
    "development_approach": "Agile | Waterfall | Hybrid",
    "project_duration": "Short-term | Medium-term | Long-term",
    "complexity_level": "Simple | Medium | Complex",
    "deployment_target": "Cloud | On-premise | Hybrid"
}
```

### **Customization Examples**

#### **Technology Stack Specific**
```markdown
# Project-Specific Best Practices

## Python Development
- Use virtual environments for dependency management
- Follow PEP 8 coding standards
- Implement proper error handling

## React Development
- Use functional components with hooks
- Implement proper state management
- Follow component composition patterns
```

#### **Team Size Specific**
```markdown
# Small Team Workflow
- Direct communication preferred
- Minimal process overhead
- Quick decision making

# Large Team Workflow
- Structured communication channels
- Formal review processes
- Clear role definitions
```

---

## Agent & Cursor AI Integration

### **Documentation Access**
```python
async def setup_agent_access(self, project_path: str) -> bool:
    """Setup documentation access for agents and Cursor AI."""
    
    # Create agent-readable documentation
    agent_docs = {
        "quick_reference": f"{project_path}/docs/QUICK_REFERENCE.md",
        "development_guide": f"{project_path}/docs/DEVELOPMENT_GUIDE.md",
        "troubleshooting": f"{project_path}/docs/TROUBLESHOOTING.md"
    }
    
    # Create Cursor AI configuration
    cursor_config = {
        "project_context": f"{project_path}/.cursor/project-context.md",
        "development_patterns": f"{project_path}/.cursor/patterns.md",
        "best_practices": f"{project_path}/.cursor/best-practices.md"
    }
    
    return await self._create_agent_documentation(agent_docs, cursor_config)
```

### **Cursor AI Configuration**
```markdown
# .cursor/project-context.md
This project follows the BMAD development methodology with the following key principles:

## Development Approach
- Async-first development
- MCP integration for enhanced capabilities
- Comprehensive testing strategy
- Quality-driven development

## Key Patterns
- Agent-based architecture
- Event-driven communication
- Graceful error handling
- Performance monitoring

## Best Practices
- Follow established coding standards
- Implement proper error handling
- Write comprehensive tests
- Document all changes
```

---

## Automation Workflow

### **Automatic Trigger**
```python
async def auto_setup_project_documentation(self, project_path: str) -> bool:
    """Automatically setup project documentation when new project detected."""
    
    try:
        # Step 1: Detect new project
        if not await self.detect_new_project(project_path):
            logger.info("Not a new project, skipping documentation setup")
            return True
        
        # Step 2: Collect core documentation
        core_docs = await self.collect_core_documentation()
        
        # Step 3: Get project context
        project_context = await self._analyze_project_context(project_path)
        
        # Step 4: Customize documentation
        customized_docs = await self.customize_for_project(core_docs, project_context)
        
        # Step 5: Create structure
        structure = await self.create_project_documentation_structure(project_path)
        
        # Step 6: Deploy documentation
        success = await self.deploy_project_documentation(customized_docs, structure)
        
        # Step 7: Setup agent access
        agent_success = await self.setup_agent_access(project_path)
        
        return success and agent_success
        
    except Exception as e:
        logger.error(f"Error in auto setup: {e}")
        return False
```

### **Manual Trigger**
```python
async def setup_project_documentation(self, project_path: str, project_context: Dict[str, Any]) -> bool:
    """Manually setup project documentation with specific context."""
    
    try:
        # Collect and customize documentation
        core_docs = await self.collect_core_documentation()
        customized_docs = await self.customize_for_project(core_docs, project_context)
        
        # Create structure and deploy
        structure = await self.create_project_documentation_structure(project_path)
        success = await self.deploy_project_documentation(customized_docs, structure)
        
        # Setup agent access
        agent_success = await self.setup_agent_access(project_path)
        
        return success and agent_success
        
    except Exception as e:
        logger.error(f"Error in manual setup: {e}")
        return False
```

---

## Integration with Development Workflow

### **Pre-Development Setup**
1. **Project Initialization**: Detect new project
2. **Documentation Setup**: Run DocumentationAgent workflow
3. **Context Analysis**: Analyze project requirements
4. **Customization**: Adapt documentation to project needs
5. **Deployment**: Deploy to project structure

### **During Development**
1. **Documentation Updates**: Update project-specific documentation
2. **Lessons Learned**: Capture new lessons learned
3. **Best Practices**: Refine best practices
4. **Pattern Updates**: Update development patterns

### **Post-Development**
1. **Documentation Review**: Review and finalize documentation
2. **Knowledge Transfer**: Transfer lessons learned back to core guides
3. **Template Updates**: Update templates based on project experience

---

## Quality Assurance

### **Documentation Quality Checks**
- [ ] All core files present and accessible
- [ ] Project-specific customization applied
- [ ] Agent access properly configured
- [ ] Cursor AI integration working
- [ ] Documentation structure logical
- [ ] Links and references working

### **Validation Process**
```python
async def validate_documentation_setup(self, project_path: str) -> Dict[str, bool]:
    """Validate that documentation setup was successful."""
    
    validation_results = {
        "structure_created": await self._validate_structure(project_path),
        "core_docs_present": await self._validate_core_docs(project_path),
        "customization_applied": await self._validate_customization(project_path),
        "agent_access": await self._validate_agent_access(project_path),
        "cursor_integration": await self._validate_cursor_integration(project_path)
    }
    
    return validation_results
```

---

## Version History

- **v1.0 (2025-08-02)**: Initial workflow creation
- **v1.1 (Planned)**: Enhanced customization options
- **v1.2 (Planned)**: Advanced agent integration

---

**Note**: Deze workflow wordt automatisch uitgevoerd bij nieuwe projecten en kan ook handmatig worden getriggerd voor bestaande projecten. 