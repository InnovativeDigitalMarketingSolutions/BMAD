# Development Workflow Guide

## Overview

Dit document beschrijft de verplichte development workflow voor alle nieuwe functionaliteit en uitbreidingen in het BMAD systeem. Het doel is om ervoor te zorgen dat alle code kwalitatief is geïmplementeerd en goed ontwikkeld wordt.

**Voor development strategie en filosofie, zie**: `DEVELOPMENT_STRATEGY.md`

## Development Pyramid Implementatie

Volg de development pyramid strategie zoals beschreven in `DEVELOPMENT_STRATEGY.md`:

```
    🔺 Production Deployment (weinig, volledige validatie)
   🔺🔺 Integration Development (gemiddeld, service integratie)
🔺🔺🔺 Unit Development (veel, component ontwikkeling)
```

### Development Distribution
- **Unit Development**: 70% van alle development (snel, geïsoleerd)
- **Integration Development**: 20% van alle development (service integratie)
- **Production Development**: 10% van alle development (volledige validatie)

## Development Workflow Checklist

### Voor het implementeren van nieuwe functionaliteit:

- [ ] **Agent Inventory Check**: Raadpleeg `bmad/agents/Agent/agents-overview.md` voor complete agent lijst (23 agents)
- [ ] **Project Planning Check**: Raadpleeg project planning files voor context en requirements:
  - `docs/deployment/KANBAN_BOARD.md` - Huidige taken en status
  - `docs/deployment/BMAD_MASTER_PLANNING.md` - Uitgebreide backlog en roadmap
  - `docs/deployment/IMPLEMENTATION_DETAILS.md` - Gedetailleerde implementatie uitleg
- [ ] **Analyse**: Root cause analysis uitvoeren voor bugs
- [ ] **Planning**: Development strategie bepalen (unit, integration, production)
- [ ] **Review**: Bestaande guide files raadplegen voor best practices
- [ ] **Strategy Review**: Bekijk `DEVELOPMENT_STRATEGY.md` voor development type keuze

### Tijdens implementatie:

- [ ] **Unit Development**: Ontwikkel alle core modules
- [ ] **Integration Development**: Ontwikkel service integraties
- [ ] **Quality Checks**: Gebruik linting en code quality tools
- [ ] **Validation**: Test edge cases en error scenarios
- [ ] **Code Quality**: Volg quality standards uit `DEVELOPMENT_STRATEGY.md`

### Na implementatie:

- [ ] **Quality Validation**: Alle quality checks uitvoeren
- [ ] **Coverage Check**: Code coverage controleren
- [ ] **Documentation**: Code documenteren
- [ ] **Review**: Code review inclusief quality checks
- [ ] **Strategy Validation**: Controleer of development strategie correct is toegepast

## Development Structure

### Voor Microservices:

```
microservices/{service-name}/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Main application
│   ├── services/                  # Core services
│   │   ├── __init__.py
│   │   ├── {service_name}.py
│   │   └── ...
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── {model_name}.py
│   │   └── ...
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── {utility_name}.py
│       └── ...
├── tests/                         # Test suite
├── requirements.txt               # Dependencies
├── Dockerfile                     # Containerization
└── README.md                      # Service documentation
```

### Voor Agents:

```
bmad/agents/Agent/{agent_name}/
├── {agent_name}.py               # Agent implementation
├── {agent_name}.yaml             # Agent configuration
├── README.md                     # Agent documentation
└── ...
```

### Voor CLI:

```
cli/
├── {cli_name}_cli.py             # CLI implementation
├── commands/                      # Command modules
│   ├── __init__.py
│   ├── {command_name}.py
│   └── ...
└── ...
```

## 📋 **Project Planning & Agent Inventory Management**

### **Mandatory Project Planning Check**
**VOOR ELKE NIEUWE IMPLEMENTATIE** moet je eerst de project planning files raadplegen:

```bash
# Check project planning files
cat docs/deployment/KANBAN_BOARD.md
cat docs/deployment/BMAD_MASTER_PLANNING.md
cat docs/deployment/IMPLEMENTATION_DETAILS.md
cat bmad/agents/Agent/agents-overview.md
```

### **Project Planning Files Overview**
- **KANBAN_BOARD.md**: Huidige taken, status, en sprint planning
- **BMAD_MASTER_PLANNING.md**: Uitgebreide backlog, roadmap, en implementatie strategie
- **IMPLEMENTATION_DETAILS.md**: Gedetailleerde technische implementatie uitleg
- **agents-overview.md**: Complete agent inventory en status

### **Project Planning Checklist**
- [ ] **Kanban Status**: Controleer huidige taken en sprint planning
- [ ] **Backlog Items**: Verificeer relevante backlog items in master planning
- [ ] **Implementation Context**: Raadpleeg implementatie details voor technische context
- [ ] **Agent Inventory**: Controleer dat alle 23 agents zijn meegenomen
- [ ] **MCP Status**: Verificeer MCP integration status van alle agents
- [ ] **Dependencies**: Identificeer agent dependencies en integratie punten
- [ ] **Categories**: Begrijp agent categorieën (Development, Design, Quality, etc.)
- [ ] **Responsibilities**: Controleer agent verantwoordelijkheden en overlap

### **Agent Categories Overview**
1. **Core Development** (5 agents): Frontend, Backend, Fullstack, Mobile, AI
2. **Architecture & Design** (3 agents): Architect, UX/UI, Accessibility
3. **Quality & Testing** (2 agents): TestEngineer, QualityGuardian
4. **Project Management** (3 agents): ProductOwner, Scrummaster, ReleaseManager
5. **Infrastructure & Operations** (2 agents): DevOpsInfra, DataEngineer
6. **Security & Compliance** (1 agent): SecurityDeveloper
7. **Documentation & Communication** (2 agents): DocumentationAgent, FeedbackAgent
8. **Process & Workflow** (3 agents): Orchestrator, WorkflowAutomator, Retrospective
9. **Strategy & Innovation** (2 agents): StrategiePartner, RnD

### **MCP Integration Tracking**
- **Completed**: 7/23 agents (30.4%)
- **Pending**: 16/23 agents (69.6%)
- **Target**: 100% MCP integration voor alle agents

## Development Best Practices

### 1. Unit Development

```python
"""
Unit development voor {ModuleName}
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class {ClassName}:
    """{ClassName} implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize {ClassName} with configuration."""
        self.config = config or {}
        self.validate_config()
        self.setup_logging()
    
    def validate_config(self) -> None:
        """Validate configuration parameters."""
        required_keys = ["required_key1", "required_key2"]
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
    
    def setup_logging(self) -> None:
        """Setup logging for the service."""
        logger.info(f"Initializing {self.__class__.__name__}")
    
    def method_name(self, param: str) -> Dict[str, Any]:
        """Method description.
        
        Args:
            param: Parameter description
            
        Returns:
            Result description
            
        Raises:
            ValueError: When parameter is invalid
        """
        try:
            # Validate input
            if not param:
                raise ValueError("Parameter cannot be empty")
            
            # Process logic
            result = self._process_param(param)
            
            # Log success
            logger.info(f"Successfully processed parameter: {param}")
            
            return {"status": "success", "result": result}
            
        except Exception as e:
            logger.error(f"Error processing parameter {param}: {e}")
            raise
```

### 2. Integration Development

```python
"""
Integration development voor {ServiceName}
"""

import asyncio
from typing import Optional, Dict, Any
from unittest.mock import AsyncMock, MagicMock

class {ServiceName}Integration:
    """Integration service for {ServiceName}."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize integration with configuration."""
        self.config = config
        self.client = self._setup_client()
        self.fallback_enabled = config.get("fallback_enabled", True)
    
    def _setup_client(self):
        """Setup external service client."""
        try:
            # Setup external client
            client = ExternalClient(self.config)
            client.validate_connection()
            return client
        except Exception as e:
            logger.error(f"Failed to setup external client: {e}")
            if self.fallback_enabled:
                return self._setup_fallback_client()
            raise
    
    def _setup_fallback_client(self):
        """Setup fallback client when external service fails."""
        logger.warning("Using fallback client")
        return FallbackClient(self.config)
    
    async def call_external_service(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call external service with error handling."""
        try:
            result = await self.client.call(data)
            logger.info("External service call successful")
            return result
        except ExternalServiceError as e:
            logger.error(f"External service error: {e}")
            if self.fallback_enabled:
                return await self._handle_fallback(data)
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
```

### 3. Production Development

```python
"""
Production development voor {ServiceName}
"""

import os
import logging
from typing import Dict, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class {ServiceName}Production:
    """Production service for {ServiceName}."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize production service."""
        self.config = config
        self.setup_monitoring()
        self.setup_logging()
        self.setup_error_tracking()
    
    def setup_monitoring(self) -> None:
        """Setup monitoring and metrics."""
        try:
            # Setup monitoring
            self.monitor = MonitoringService(self.config)
            logger.info("Monitoring setup successful")
        except Exception as e:
            logger.error(f"Failed to setup monitoring: {e}")
    
    def setup_logging(self) -> None:
        """Setup structured logging."""
        try:
            # Setup structured logging
            self.logger = StructuredLogger(self.config)
            logger.info("Logging setup successful")
        except Exception as e:
            logger.error(f"Failed to setup logging: {e}")
    
    def setup_error_tracking(self) -> None:
        """Setup error tracking and alerting."""
        try:
            # Setup error tracking
            self.error_tracker = ErrorTrackingService(self.config)
            logger.info("Error tracking setup successful")
        except Exception as e:
            logger.error(f"Failed to setup error tracking: {e}")
    
    @asynccontextmanager
    async def production_context(self):
        """Production context manager."""
        try:
            # Setup production context
            await self.setup_production_context()
            yield self
        except Exception as e:
            # Handle production errors
            await self.handle_production_error(e)
            raise
        finally:
            # Cleanup production context
            await self.cleanup_production_context()
```

## Code Quality Standards

### 1. Linting Configuration

```ini
# .flake8
[flake8]
max-line-length = 120
ignore = E501,W503,E402,F401,F541,F821,F811,F841,E265,E303,E226,W291,W293,W292,E128,E129,E305,E302,E306,E261,E504,F824,W504,E122,E116
exclude = .git,__pycache__,.venv,venv,path/to/venv,htmlcov,.pytest_cache,allure-results,test_data
per-file-ignores = 
    bmad/resources/templates/**/*.py:F821
    bmad/agents/Agent/**/*.py:E402
    bmad/agents/core/**/*.py:F401
```

### 2. Code Quality Requirements
- **Linting**: Geen flake8 errors
- **Documentation**: Complete docstrings voor alle functies
- **Error Handling**: Comprehensive error handling
- **Logging**: Structured logging voor alle operaties
- **Type Hints**: Type hints voor alle functies

### 3. Development Quality Requirements
- **No Code Removal**: Alleen uitbreiden, niet verwijderen
- **Root Cause Analysis**: Voor bugs, niet symptomen
- **Guide Updates**: Update guide files na oplossingen
- **Backward Compatibility**: Behoud van bestaande functionaliteit

## Development Execution Workflow

### 1. Voor elke nieuwe feature:

```bash
# 1. Setup development environment
export DEV_MODE=true
source venv/bin/activate

# 2. Run quality checks
flake8 bmad/ --count
pytest tests/unit/ -v

# 3. Implement feature
# ... development work ...

# 4. Run comprehensive checks
flake8 bmad/ --count
pytest tests/ -v
pytest --cov=bmad --cov-report=html
```

### 2. Voor microservices:

```bash
# 1. Setup service environment
cd microservices/{service-name}
export SERVICE_ENV=development

# 2. Run service quality checks
flake8 src/ --count
pytest tests/unit/ -v

# 3. Run integration checks
pytest tests/integration/ -v --run-integration

# 4. Run full test suite
pytest tests/ -v --cov=src
```

### 3. Development Environment Setup

```bash
# 1. Enable development mode
export DEV_MODE=true

# 2. Setup database connection (optional)
python setup_database_connection.py

# 3. Verify setup
python verify_database_tables.py

# 4. Start development server
python bmad/api.py
```

## Quality Gates

### 1. Code Quality Requirements
- **Linting**: Geen flake8 errors
- **Documentation**: Complete docstrings
- **Error Handling**: Comprehensive error handling
- **Logging**: Structured logging

### 2. Development Quality Requirements
- **No Code Removal**: Alleen uitbreiden, niet verwijderen
- **Root Cause Analysis**: Voor bugs, niet symptomen
- **Guide Updates**: Update guide files na oplossingen

### 3. Production Quality Requirements
- **Monitoring**: Complete monitoring setup
- **Logging**: Structured logging
- **Error Tracking**: Error tracking en alerting
- **Performance**: Performance monitoring

## Development Maintenance

### 1. Regular Updates
- Update code bij requirements wijzigingen
- Verwijder obsolete code (met analyse)
- Voeg code toe voor nieuwe edge cases

### 2. Code Review
- Code review inclusief quality checks
- Quality monitoring
- Performance monitoring

### 3. Documentation
- Update development documentation
- Document development patterns
- Share best practices

## Troubleshooting

### Common Issues

1. **Linting Errors**
   - Run `flake8 bmad/ --count` to identify issues
   - Fix linting errors before committing
   - Use per-file-ignores for template files

2. **Import Errors**
   - Check sys.path voor imports
   - Gebruik relative imports waar mogelijk
   - Validate dependencies

3. **Development Environment**
   - Ensure DEV_MODE is set
   - Check environment variables
   - Validate database connections

### Debug Tips

```bash
# Debug development environment
python -c "import os; print('DEV_MODE:', os.getenv('DEV_MODE'))"

# Debug specific module
python -c "import bmad.core.agent; print('Module loaded successfully')"

# Check linting issues
flake8 bmad/ --count --show-source

# Run with coverage
pytest --cov=bmad --cov-report=term-missing tests/
```

## Examples

### Voor Context Service:

```python
# bmad/core/context/context_manager.py
class ContextManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validate_config()
        self.setup_logging()
    
    def create_context(self, name: str, context_type: str) -> Dict[str, Any]:
        """Create a new context."""
        try:
            context = {
                "name": name,
                "type": context_type,
                "created_at": datetime.utcnow()
            }
            logger.info(f"Created context: {name}")
            return context
        except Exception as e:
            logger.error(f"Failed to create context {name}: {e}")
            raise
```

### Voor Integration Service:

```python
# integrations/{service_name}/{service_name}_client.py
class {ServiceName}Client:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = self._setup_client()
    
    def _setup_client(self):
        """Setup external service client."""
        try:
            client = ExternalClient(self.config)
            client.validate_connection()
            return client
        except Exception as e:
            logger.error(f"Failed to setup client: {e}")
            raise
```

### Voor Workflow Service:

```python
# bmad/core/workflow/workflow_manager.py
class WorkflowManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validate_config()
        self.setup_logging()
    
    def create_workflow(self, name: str, workflow_type: str) -> Dict[str, Any]:
        """Create a new workflow."""
        try:
            workflow = {
                "name": name,
                "type": workflow_type,
                "created_at": datetime.utcnow()
            }
            logger.info(f"Created workflow: {name}")
            return workflow
        except Exception as e:
            logger.error(f"Failed to create workflow {name}: {e}")
            raise
```

## 🚀 Nieuwe Lessons Learned (Januari 2025)

### **MCP Integration Development Lessons**

#### **1. Async Development Patterns**
**Lesson**: MCP integration vereist async-first development patterns.

**Best Practice**:
```python
# Voor MCP client development
class MCPClient:
    async def __aenter__(self):
        """Async context manager voor MCP client."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Graceful cleanup bij context exit."""
        await self.disconnect()
    
    async def execute_tool(self, tool_name: str, **kwargs):
        """Async tool execution met proper error handling."""
        try:
            return await self._execute_tool_internal(tool_name, **kwargs)
        except MCPConnectionError:
            logger.warning("MCP connection failed, using fallback")
            return await self._fallback_execution(tool_name, **kwargs)
```

**Voordelen**:
- ✅ Proper resource management
- ✅ Graceful error handling
- ✅ Async performance benefits

#### **2. Tool Registry Development**
**Lesson**: Tool registry moet extensible en maintainable zijn.

**Best Practice**:
```python
# Voor tool registry development
class MCPToolRegistry:
    def __init__(self):
        self._tools = {}
        self._statistics = {}
        self._lock = asyncio.Lock()
    
    async def register_tool(self, tool: MCPTool):
        """Thread-safe tool registration."""
        async with self._lock:
            self._tools[tool.name] = tool
            self._statistics[tool.name] = ToolStatistics()
    
    async def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Thread-safe tool retrieval."""
        async with self._lock:
            return self._tools.get(tool_name)
```

**Voordelen**:
- ✅ Thread-safe operations
- ✅ Extensible architecture
- ✅ Performance monitoring

#### **3. Agent MCP Integration**
**Lesson**: Agent MCP integration moet backward compatible zijn.

**Best Practice**:
```python
# Voor agent MCP integration
class MCPEnhancedAgent:
    def __init__(self):
        self.mcp_client = None
        self.mcp_enabled = False
    
    async def initialize_mcp(self):
        """Initialize MCP client als beschikbaar."""
        try:
            self.mcp_client = await MCPClient.create()
            await self.mcp_client.connect()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully")
        except Exception as e:
            logger.warning(f"MCP initialization failed: {e}")
            self.mcp_enabled = False
    
    async def execute_task(self, task_name: str, **kwargs):
        """Execute task met MCP fallback."""
        if self.mcp_enabled and self.mcp_client:
            try:
                return await self.mcp_client.execute_tool(task_name, **kwargs)
            except Exception:
                logger.warning("MCP execution failed, using local execution")
        
        # Fallback naar lokale execution
        return await self._local_execution(task_name, **kwargs)
```

**Voordelen**:
- ✅ Backward compatibility
- ✅ Graceful degradation
- ✅ Progressive enhancement

### **Kanban Board Development Lessons**

#### **1. Cursor AI Integration**
**Lesson**: Kanban board moet Cursor AI-vriendelijk zijn voor development workflow.

**Best Practice**:
```markdown
# Voor Cursor AI optimale Kanban structuur
## 📋 Backlog (Toekomstige Taken)

### **Priority 1 - High Priority**
- [ ] **Feature Name** (Week X-Y)
  - [ ] Subtask 1
  - [ ] Subtask 2
  - [ ] Subtask 3

### **Priority 2 - Medium Priority**
- [ ] **Feature Name** (Week X-Y)
  - [ ] Subtask 1
  - [ ] Subtask 2
```

**Voordelen**:
- ✅ Cursor AI kan taken herkennen
- ✅ Duidelijke task structuur
- ✅ Progress tracking

#### **2. Implementation Details Integration**
**Lesson**: Technische details moeten gescheiden blijven van project management.

**Best Practice**:
```python
# Voor implementation details management
class ImplementationTracker:
    def __init__(self):
        self.kanban_board = "docs/deployment/KANBAN_BOARD.md"
        self.implementation_details = "docs/deployment/IMPLEMENTATION_DETAILS.md"
    
    def update_task_status(self, task_name: str, status: str):
        """Update task status in Kanban board."""
        # Update Kanban board
        self._update_kanban_status(task_name, status)
        
        # Update implementation details
        self._update_implementation_details(task_name, status)
    
    def _update_kanban_status(self, task_name: str, status: str):
        """Update status in Kanban board."""
        # Implementation voor Kanban board update
        pass
    
    def _update_implementation_details(self, task_name: str, status: str):
        """Update technical details."""
        # Implementation voor technical details update
        pass
```

**Voordelen**:
- ✅ Separation of concerns
- ✅ Maintainable documentation
- ✅ Clear information hierarchy

### **Guide Files Development Lessons**

#### **1. Regular Updates Workflow**
**Lesson**: Guide files moeten regelmatig geüpdatet worden met development insights.

**Best Practice**:
```python
# Voor guide files management
class GuideManager:
    def __init__(self):
        self.guides_path = "docs/guides/"
        self.required_sections = ['Doel', 'Checklist', 'Lessons Learned']
    
    def update_guide_with_lessons(self, guide_name: str, lessons: List[str]):
        """Update guide met nieuwe lessons learned."""
        guide_path = f"{self.guides_path}{guide_name}"
        
        # Read current guide
        with open(guide_path, 'r') as f:
            content = f.read()
        
        # Add new lessons learned
        lessons_section = self._format_lessons_section(lessons)
        updated_content = self._add_lessons_to_guide(content, lessons_section)
        
        # Write updated guide
        with open(guide_path, 'w') as f:
            f.write(updated_content)
    
    def _format_lessons_section(self, lessons: List[str]) -> str:
        """Format lessons learned section."""
        section = "\n## 🚀 Nieuwe Lessons Learned\n\n"
        for lesson in lessons:
            section += f"- {lesson}\n"
        return section
```

**Voordelen**:
- ✅ Automated guide updates
- ✅ Consistent formatting
- ✅ Knowledge preservation

#### **2. Cross-Reference Management**
**Lesson**: Guide files moeten elkaar refereren voor complete coverage.

**Best Practice**:
```python
# Voor cross-reference management
class GuideCrossReference:
    def __init__(self):
        self.guide_references = {
            'DEVELOPMENT_WORKFLOW_GUIDE.md': [
                'DEVELOPMENT_STRATEGY.md',
                'TESTING_STRATEGY.md',
                'DEVELOPMENT_QUALITY_GUIDE.md'
            ],
            'TEST_WORKFLOW_GUIDE.md': [
                'TESTING_STRATEGY.md',
                'TEST_QUALITY_GUIDE.md'
            ]
        }
    
    def validate_cross_references(self):
        """Validate of alle cross-references correct zijn."""
        for guide, references in self.guide_references.items():
            for reference in references:
                if not self._reference_exists(reference):
                    logger.warning(f"Missing reference in {guide}: {reference}")
    
    def _reference_exists(self, reference: str) -> bool:
        """Check of reference file bestaat."""
        return os.path.exists(f"docs/guides/{reference}")
```

**Voordelen**:
- ✅ Consistent documentation
- ✅ No broken links
- ✅ Complete coverage

### **Quality Assurance Development Lessons**

#### **1. Automated Quality Checks**
**Lesson**: Automated quality checks zijn essentieel voor development consistency.

**Best Practice**:
```python
# Voor automated quality checks
class DevelopmentQualityChecker:
    def __init__(self):
        self.quality_checks = [
            self._check_guide_completeness,
            self._check_cross_references,
            self._check_implementation_details,
            self._check_kanban_board
        ]
    
    async def run_quality_checks(self):
        """Run alle quality checks."""
        results = []
        for check in self.quality_checks:
            try:
                result = await check()
                results.append(result)
            except Exception as e:
                logger.error(f"Quality check failed: {e}")
                results.append(False)
        
        return all(results)
    
    async def _check_guide_completeness(self) -> bool:
        """Check of alle guides complete zijn."""
        # Implementation voor guide completeness check
        return True
    
    async def _check_cross_references(self) -> bool:
        """Check of alle cross-references correct zijn."""
        # Implementation voor cross-reference check
        return True
```

**Voordelen**:
- ✅ Consistent quality
- ✅ Automated validation
- ✅ Early error detection

### **Development Workflow Integration**

#### **1. MCP-Enhanced Development**
**Lesson**: MCP integration verbetert development workflow significant.

**Best Practice**:
```python
# Voor MCP-enhanced development
class MCPDevelopmentWorkflow:
    def __init__(self):
        self.mcp_client = None
        self.workflow_tools = [
            'code_analysis',
            'test_generation',
            'documentation_generation',
            'quality_check'
        ]
    
    async def initialize_workflow(self):
        """Initialize MCP-enhanced development workflow."""
        self.mcp_client = await MCPClient.create()
        await self.mcp_client.connect()
        
        # Register workflow tools
        for tool in self.workflow_tools:
            await self.mcp_client.register_tool(tool)
    
    async def execute_development_task(self, task_name: str, **kwargs):
        """Execute development task met MCP enhancement."""
        if self.mcp_client:
            try:
                return await self.mcp_client.execute_tool(task_name, **kwargs)
            except Exception:
                logger.warning("MCP execution failed, using local execution")
        
        # Fallback naar lokale execution
        return await self._local_development_execution(task_name, **kwargs)
```

**Voordelen**:
- ✅ Enhanced development capabilities
- ✅ Automated tool execution
- ✅ Quality improvement

### **Implementation Recommendations**

#### **Voor Nieuwe Development**:
1. **Check Kanban Board**: Bekijk huidige development planning
2. **Update Guides**: Voeg development lessons learned toe
3. **Follow MCP Patterns**: Gebruik MCP integration waar mogelijk
4. **Quality Checks**: Run automated quality checks

#### **Voor Guide Maintenance**:
1. **Regular Updates**: Maandelijkse guide updates
2. **Lessons Learned**: Capture development lessons learned
3. **Cross-References**: Maintain cross-reference integrity
4. **Quality Validation**: Validate guide completeness

#### **Voor Workflow Integration**:
1. **MCP Integration**: Integreer MCP tools in development workflow
2. **Quality Assurance**: Automated quality checks
3. **Documentation**: Complete en up-to-date documentation
4. **Best Practices**: Consistent best practices application

## Conclusion

Deze development workflow zorgt ervoor dat:
- Alle nieuwe functionaliteit kwalitatief wordt geïmplementeerd
- Code kwaliteit hoog blijft
- Bugs vroeg gedetecteerd worden
- Documentatie up-to-date blijft
- Best practices consistent worden toegepast

**Belangrijk**: Development kwaliteit is geen optie, maar een verplicht onderdeel van elke implementatie!

## Referenties

- [DEVELOPMENT_STRATEGY.md](./DEVELOPMENT_STRATEGY.md) - Development strategie en filosofie
- [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) - Test strategie en filosofie
- [DEVELOPMENT_QUALITY_GUIDE.md](./DEVELOPMENT_QUALITY_GUIDE.md) - Development quality best practices
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contributing guidelines 