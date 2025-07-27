# BMAD LangGraph Integration

## 🚀 Overview

De BMAD LangGraph integratie biedt een moderne, async-first workflow orchestration voor complexe multi-agent samenwerking. Deze integratie vervangt de problematische async workflow systemen met een betrouwbare, stateful workflow engine gebaseerd op LangGraph.

## ✨ Key Features

### 🔄 **Async-First Workflows**
- **Stateful Execution**: LangGraph zorgt voor betrouwbare state management
- **Dependency Management**: Automatische task dependency resolution
- **Parallel Execution**: Ondersteuning voor parallelle task execution
- **Error Handling**: Robuuste error handling en retry mechanismen

### 🏗️ **Modern Architecture**
- **Graph-Based**: Workflows worden gedefinieerd als directed graphs
- **Checkpointing**: Automatische state checkpointing voor recovery
- **Event-Driven**: Event-driven architecture voor workflow coordination
- **Extensible**: Makkelijk uit te breiden met nieuwe agent types

### 🎯 **BMAD Integration**
- **Agent Compatibility**: Volledig compatibel met bestaande BMAD agents
- **Backward Compatibility**: Behoud van bestaande workflow interfaces
- **Performance**: Betere performance dan de oude async workflows
- **Debugging**: Verbeterde debugging en monitoring capabilities

## 📦 Installation

LangGraph is al geïnstalleerd in het BMAD project:

```bash
# LangGraph is al geïnstalleerd
pip list | grep langgraph
```

## 🛠️ Usage

### Basic Workflow Creation

```python
from bmad.agents.core.langgraph_workflow import (
    LangGraphWorkflowOrchestrator,
    WorkflowDefinition,
    WorkflowTask,
    create_workflow_orchestrator
)

# Create orchestrator
orchestrator = create_workflow_orchestrator()

# Define tasks
tasks = [
    WorkflowTask(
        id="product_owner_task",
        name="Create User Story",
        agent="ProductOwner",
        command="create_user_story"
    ),
    WorkflowTask(
        id="architect_task",
        name="Design System",
        agent="Architect",
        command="design_system",
        dependencies=["product_owner_task"]
    ),
    WorkflowTask(
        id="developer_task",
        name="Implement Feature",
        agent="FullstackDeveloper",
        command="implement_feature",
        dependencies=["architect_task"]
    )
]

# Create workflow definition
workflow_def = WorkflowDefinition(
    name="development_workflow",
    description="Complete development workflow",
    tasks=tasks,
    max_parallel=2,
    timeout=1800
)

# Register and start workflow
orchestrator.register_workflow(workflow_def)
workflow_id = orchestrator.start_workflow("development_workflow", {
    "project": "My Project",
    "feature": "User Authentication"
})
```

### CLI Usage

```bash
# Test LangGraph integration
python langgraph_cli.py test

# Run demo workflow
python langgraph_cli.py demo

# Run simple workflow
python langgraph_cli.py simple

# List available workflows
python langgraph_cli.py list

# Check workflow status
python langgraph_cli.py status <workflow_id>
```

## 🏗️ Architecture

### Core Components

#### 1. **LangGraphWorkflowOrchestrator**
De hoofdklasse voor workflow orchestration:

```python
class LangGraphWorkflowOrchestrator:
    def __init__(self):
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.task_executors: Dict[str, Callable] = {}
        self.active_workflows: Dict[str, Any] = {}
```

#### 2. **WorkflowDefinition**
Definieert een complete workflow:

```python
@dataclass
class WorkflowDefinition:
    name: str
    description: str
    tasks: List[WorkflowTask]
    max_parallel: int = 3
    timeout: int = 3600
    auto_retry: bool = True
    notify_on_completion: bool = True
    notify_on_failure: bool = True
```

#### 3. **WorkflowTask**
Represents een enkele taak in een workflow:

```python
@dataclass
class WorkflowTask:
    id: str
    name: str
    agent: str
    command: str
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300
    retries: int = 3
    parallel: bool = False
    required: bool = True
```

#### 4. **WorkflowState**
State management voor LangGraph:

```python
class WorkflowState(TypedDict):
    workflow_id: str
    workflow_name: str
    current_task: Optional[str]
    completed_tasks: List[str]
    failed_tasks: List[str]
    skipped_tasks: List[str]
    task_results: Dict[str, Dict[str, Any]]
    task_errors: Dict[str, str]
    context: Dict[str, Any]
    status: str
    start_time: float
    end_time: Optional[float]
    metrics: Dict[str, int]
```

### Workflow Execution Flow

1. **Workflow Registration**: Workflow wordt geregistreerd met definities
2. **Graph Creation**: LangGraph creëert een state graph
3. **Task Execution**: Tasks worden uitgevoerd volgens dependencies
4. **State Management**: LangGraph beheert workflow state
5. **Completion**: Workflow wordt gemarkeerd als voltooid

## 🔧 Configuration

### Environment Variables

```bash
# LangGraph configuration (optioneel)
LANGGRAPH_DEBUG=true
LANGGRAPH_CHECKPOINT_DIR=./checkpoints
```

### Workflow Configuration

```python
# Workflow settings
workflow_def = WorkflowDefinition(
    name="my_workflow",
    description="My workflow description",
    tasks=tasks,
    max_parallel=3,        # Maximum parallelle tasks
    timeout=3600,          # Timeout in seconden
    auto_retry=True,       # Automatische retry bij failure
    notify_on_completion=True,  # Notificatie bij voltooiing
    notify_on_failure=True      # Notificatie bij failure
)
```

## 🧪 Testing

### Unit Tests

```bash
# Run LangGraph tests
python -m pytest tests/backend/test_langgraph_workflow.py -v
```

### Integration Tests

```bash
# Test LangGraph integration
python langgraph_cli.py test

# Run demo workflow
python langgraph_cli.py demo
```

### Test Coverage

De LangGraph integratie heeft uitgebreide test coverage:

- ✅ WorkflowTask creation en configuratie
- ✅ WorkflowDefinition creation en settings
- ✅ Orchestrator initialization en registratie
- ✅ Task execution en error handling
- ✅ Dependency management
- ✅ Workflow status monitoring
- ✅ Async task execution

## 🚀 Benefits Over Old System

### ❌ **Old Async Workflow Problems**
- `KeyError: 'completed_tasks'` - State management issues
- `TypeError: 'WorkflowTask' object is not subscriptable` - Incorrect object handling
- `AttributeError: 'dict' object has no attribute 'required'` - Type confusion
- Hanging tests en infinite loops
- Complexe async debugging

### ✅ **LangGraph Solutions**
- **Stateful Execution**: Automatische state management
- **Type Safety**: Proper TypedDict en dataclass usage
- **Graph-Based**: Duidelijke workflow structure
- **Checkpointing**: Automatische state recovery
- **Better Debugging**: Verbeterde error messages en logging

## 📊 Performance Comparison

| Metric | Old System | LangGraph |
|--------|------------|-----------|
| Async Reliability | ❌ Poor | ✅ Excellent |
| State Management | ❌ Manual | ✅ Automatic |
| Error Handling | ❌ Complex | ✅ Robust |
| Debugging | ❌ Difficult | ✅ Easy |
| Performance | ⚠️ Variable | ✅ Consistent |
| Test Coverage | ❌ Low | ✅ High |

## 🔮 Future Enhancements

### Planned Features

1. **Advanced Routing**
   - Conditional task execution
   - Dynamic workflow modification
   - A/B testing workflows

2. **Enhanced Monitoring**
   - Real-time workflow visualization
   - Performance metrics
   - Resource usage tracking

3. **Integration Extensions**
   - Prefect integration voor CI/CD
   - OpenTelemetry voor observability
   - OpenRouter voor multi-LLM support

4. **Security Features**
   - OPA integration voor policy enforcement
   - Access control per workflow
   - Audit trail logging

## 🛠️ Troubleshooting

### Common Issues

#### 1. **"Found edge starting at unknown node"**
**Problem**: LangGraph graph validation error
**Solution**: Zorg dat alle nodes correct zijn gedefinieerd

```python
# Add missing nodes
workflow.add_node("start", lambda state: state)
workflow.add_node("end", lambda state: state)
```

#### 2. **"RuntimeError: no running event loop"**
**Problem**: Async execution buiten event loop
**Solution**: Gebruik proper async context

```python
# Use asyncio.run() for testing
result = asyncio.run(orchestrator._execute_task(task, context))
```

#### 3. **Workflow Status Not Available**
**Problem**: Workflow execution failed
**Solution**: Check logs en error handling

```python
# Check workflow status
status = orchestrator.get_workflow_status(workflow_id)
if status is None:
    print("Workflow failed or not found")
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('bmad.agents.core.langgraph_workflow').setLevel(logging.DEBUG)
```

## 📚 API Reference

### Core Functions

#### `create_workflow_orchestrator()`
Create a new LangGraph workflow orchestrator.

```python
orchestrator = create_workflow_orchestrator()
```

#### `register_workflow_definition(name, description, tasks, **kwargs)`
Create and register a workflow definition.

```python
workflow_def = register_workflow_definition(
    name="my_workflow",
    description="My workflow",
    tasks=tasks,
    max_parallel=3
)
```

### Orchestrator Methods

#### `register_workflow(workflow_def)`
Register a workflow definition.

#### `start_workflow(workflow_name, context=None)`
Start a workflow execution.

#### `get_workflow_status(workflow_id)`
Get the status of a running workflow.

#### `cancel_workflow(workflow_id)`
Cancel a running workflow.

## 🤝 Contributing

### Adding New Agent Types

1. **Register Task Executor**:
```python
def my_agent_executor(task, context):
    # Implement agent logic
    return {"output": "result"}

orchestrator.register_task_executor("MyAgent", my_agent_executor)
```

2. **Create Workflow Task**:
```python
task = WorkflowTask(
    id="my_task",
    name="My Task",
    agent="MyAgent",
    command="my_command"
)
```

### Adding New Features

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## 📄 License

Deze LangGraph integratie is onderdeel van het BMAD project en volgt dezelfde licentie.

## 🆘 Support

Voor vragen of problemen met de LangGraph integratie:

1. Check de troubleshooting sectie
2. Review de test cases
3. Open een issue op GitHub
4. Raadpleeg de LangGraph documentatie

---

**🎉 De LangGraph integratie lost de async workflow problemen op en biedt een moderne, betrouwbare foundation voor BMAD workflows!** 