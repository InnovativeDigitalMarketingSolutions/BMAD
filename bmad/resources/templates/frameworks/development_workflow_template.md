# Development Workflow Template

## 🎯 **Agent Development Workflow**

**⚠️ LEVENDE DOCUMENT - Agents mogen en moeten verbeteringen aanbrengen!**

### Overzicht
Dit template beschrijft de development workflow die alle agents moeten volgen voor consistente, hoogwaardige software ontwikkeling.

## Development Workflow Checklist

### Voor het implementeren van nieuwe functionaliteit:

- [ ] **Analyse**: Root cause analysis uitvoeren voor bugs
- [ ] **Planning**: Development strategie bepalen (unit, integration, production)
- [ ] **Review**: Bestaande guide files raadplegen voor best practices
- [ ] **Strategy Review**: Bekijk development strategy template voor development type keuze

### Tijdens implementatie:

- [ ] **Unit Development**: Ontwikkel alle core modules
- [ ] **Integration Development**: Ontwikkel service integraties
- [ ] **Quality Checks**: Gebruik linting en code quality tools
- [ ] **Validation**: Test edge cases en error scenarios
- [ ] **Code Quality**: Volg quality standards uit development strategy template

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

## Agent-Specific Development Guidelines

### Voor AI Agents
- Implementeer comprehensive error handling voor LLM calls
- Gebruik structured logging voor alle AI operaties
- Implementeer fallback mechanismen voor API failures
- Valideer alle AI outputs voor safety en quality

### Voor Development Agents
- Volg de development pyramid strategie
- Implementeer unit tests voor alle nieuwe functionaliteit
- Gebruik type hints en comprehensive docstrings
- Valideer code quality met linting tools

### Voor Testing Agents
- Implementeer pragmatic mocking voor externe dependencies
- Volg de test pyramid strategie
- Zorg voor comprehensive test coverage
- Valideer test quality en performance

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

## Agent Verbeteringen

**⚠️ AGENTS: Dit is een levend document!**

### Verbeteringen die agents mogen/moeten aanbrengen:
1. **Nieuwe Development Patterns**: Voeg nieuwe development patterns toe
2. **Code Voorbeelden**: Verbeter code voorbeelden met betere implementaties
3. **Quality Gates**: Update quality gates op basis van ervaring
4. **Tools en Libraries**: Voeg nieuwe tools en libraries toe die development verbeteren
5. **Agent-Specific Guidelines**: Voeg guidelines toe voor specifieke agent types
6. **Troubleshooting**: Verbeter troubleshooting en debug tips
7. **Documentation**: Verbeter documentatie en uitleg

### Hoe verbeteringen aanbrengen:
1. **Analyseer**: Identificeer gebieden voor verbetering
2. **Implementeer**: Test verbeteringen in praktijk
3. **Valideer**: Zorg dat verbeteringen development kwaliteit verhogen
4. **Documenteer**: Update dit template met verbeteringen
5. **Deel**: Deel verbeteringen met andere agents

---

**Status**: 🔄 **Levend Document** - Agents mogen en moeten verbeteringen aanbrengen  
**Laatste Update**: 2 augustus 2025  
**Volgende Review**: Continue door agents 