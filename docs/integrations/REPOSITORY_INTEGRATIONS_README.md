# BMAD Repository Integrations

## 🚀 Overview

Dit document beschrijft de implementatie van complementaire GitHub repositories in het BMAD systeem volgens het advies. Deze integraties bieden moderne, schaalbare en betrouwbare functionaliteiten voor multi-agent workflows.

## 📦 Geïmplementeerde Repositories

### 🧱 1. Agent Orkestratie / AI Pipeline Structuur

#### ✅ LangGraph Integration
- **Status**: Volledig geïmplementeerd
- **Bestand**: `bmad/agents/core/langgraph_workflow.py`
- **Functionaliteit**: Async-first workflow orchestration met stateful execution
- **Voordelen**: Betrouwbare async workflows, dependency management, error handling

#### ✅ OpenRouter Integration
- **Status**: Volledig geïmplementeerd
- **Bestand**: `bmad/agents/core/openrouter_client.py`
- **Functionaliteit**: Multi-LLM routing en provider integratie
- **Ondersteunde Providers**: OpenAI, Anthropic, Google, Mistral, Cohere, Meta
- **Features**: Load balancing, cost optimization, automatic fallback

### 🧰 2. DevOps Tooling / CI Integratie

#### ✅ Prefect Integration
- **Status**: Volledig geïmplementeerd
- **Bestand**: `bmad/agents/core/prefect_workflow.py`
- **Functionaliteit**: CI/CD workflow orchestration
- **Features**: Deployment management, scheduling, monitoring

### 📊 3. Observability & Telemetrie

#### ✅ OpenTelemetry Integration
- **Status**: Volledig geïmplementeerd
- **Bestand**: `bmad/agents/core/opentelemetry_tracing.py`
- **Functionaliteit**: Distributed tracing en observability
- **Exporters**: Console, Jaeger, OTLP, Prometheus
- **Metrics**: Agent executions, workflow performance, LLM usage

### 🔒 4. Security / Rights Management / Autonomy

#### ✅ OPA Integration
- **Status**: Volledig geïmplementeerd
- **Bestand**: `bmad/agents/core/opa_policy_engine.py`
- **Functionaliteit**: Policy-based access control en behavior rules
- **Policy Types**: Access control, resource limits, security policies, workflow policies

## 🛠️ Installation

### 1. Install Dependencies

```bash
# Update requirements.txt met nieuwe dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# OpenRouter API key (voor multi-LLM routing)
export OPENROUTER_API_KEY="your-api-key-here"

# OPA server URL (voor policy enforcement)
export OPA_URL="http://localhost:8181"

# OpenTelemetry configuratie
export OTEL_SERVICE_NAME="bmad-agents"
export OTEL_ENVIRONMENT="development"
```

### 3. Start External Services (Optional)

```bash
# Start OPA server (voor policy enforcement)
docker run -d --name opa-server -p 8181:8181 openpolicyagent/opa run --server

# Start Jaeger (voor tracing visualisatie)
docker run -d --name jaeger -p 16686:16686 -p 6831:6831 jaegertracing/all-in-one

# Start Prometheus (voor metrics)
docker run -d --name prometheus -p 9090:9090 prom/prometheus
```

## 🧪 Testing

### CLI Tool

Gebruik de repository integration CLI om alle componenten te testen:

```bash
# Test alle integraties
python repository_integration_cli.py --test all

# Test specifieke integratie
python repository_integration_cli.py --test openrouter
python repository_integration_cli.py --test opentelemetry
python repository_integration_cli.py --test opa
python repository_integration_cli.py --test prefect
python repository_integration_cli.py --test langgraph

# Export policies
python repository_integration_cli.py --export-policies policies.json

# Verbose logging
python repository_integration_cli.py --test all --verbose
```

### Unit Tests

```bash
# Run alle tests
python -m pytest tests/ -v

# Run specifieke test modules
python -m pytest tests/backend/test_langgraph_workflow.py -v
python -m pytest tests/backend/test_prefect_workflow.py -v
```

## 📖 Usage Examples

### 1. OpenRouter Multi-LLM Routing

```python
from bmad.agents.core.openrouter_client import OpenRouterClient, LLMConfig, LLMProvider

# Initialize client
client = OpenRouterClient("your-api-key")

# Generate response met routing strategy
response = await client.generate_response(
    prompt="Explain multi-agent systems",
    strategy_name="development",  # development, production, testing
    context={"project": "BMAD"}
)

print(f"Response: {response.content}")
print(f"Provider: {response.provider}")
print(f"Cost: ${response.cost:.4f}")
print(f"Tokens: {response.tokens_used}")
```

### 2. OpenTelemetry Tracing

```python
from bmad.agents.core.opentelemetry_tracing import (
    initialize_tracing, TracingConfig, TraceLevel, ExporterType
)

# Initialize tracing
config = TracingConfig(
    service_name="my-bmad-service",
    trace_level=TraceLevel.DETAILED,
    exporters=[ExporterType.CONSOLE, ExporterType.JAEGER]
)
tracer = initialize_tracing(config)

# Trace agent execution
with tracer.trace_agent_execution("ProductOwner", "create_user_story") as span:
    # Agent work here
    span.set_attribute("user_story_id", "US-123")
    span.add_event("story_created", {"priority": "high"})

# Trace workflow execution
with tracer.trace_workflow_execution("development_workflow", "wf-456") as span:
    # Workflow execution here
    pass
```

### 3. OPA Policy Enforcement

```python
from bmad.agents.core.opa_policy_engine import (
    initialize_policy_engine, PolicyRequest
)

# Initialize policy engine
policy_engine = initialize_policy_engine("http://localhost:8181")

# Check agent permission
request = PolicyRequest(
    subject="ProductOwner",
    action="create_user_story",
    resource="backlog",
    context={"project": "BMAD"}
)

response = await policy_engine.evaluate_policy(request)

if response.allowed:
    print("✅ Action allowed")
else:
    print(f"❌ Action denied: {response.reason}")

# Check workflow permission
workflow_response = await policy_engine.check_workflow_permission(
    agent_name="Architect",
    workflow_id="workflow-123",
    action="workflow_modify"
)
```

### 4. Prefect CI/CD Workflows

```python
from bmad.agents.core.prefect_workflow import (
    create_prefect_orchestrator, PrefectWorkflowConfig, WorkflowType
)

# Initialize orchestrator
orchestrator = create_prefect_orchestrator()

# Create workflow config
config = PrefectWorkflowConfig(
    name="development_pipeline",
    description="Complete development workflow",
    workflow_type=WorkflowType.DEVELOPMENT,
    timeout_minutes=60
)

# Register and create deployment
orchestrator.register_workflow_config(config)
deployment_id = orchestrator.create_deployment("development_pipeline", [])
```

### 5. LangGraph Workflows

```python
from bmad.agents.core.langgraph_workflow import (
    create_workflow_orchestrator, WorkflowTask, WorkflowDefinition
)

# Initialize orchestrator
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
    )
]

# Create and start workflow
workflow_def = WorkflowDefinition(
    name="development_workflow",
    description="Complete development workflow",
    tasks=tasks
)

orchestrator.register_workflow(workflow_def)
workflow_id = orchestrator.start_workflow("development_workflow", {
    "project": "My Project"
})
```

## 🔧 Configuration

### OpenRouter Configuration

```python
# Custom routing strategy
from bmad.agents.core.openrouter_client import RoutingStrategy, LLMConfig, LLMProvider

strategy = RoutingStrategy(
    primary_config=LLMConfig(LLMProvider.OPENAI, "gpt-4o", max_tokens=8000),
    fallback_configs=[
        LLMConfig(LLMProvider.ANTHROPIC, "claude-3-5-haiku-20241022"),
        LLMConfig(LLMProvider.GOOGLE, "gemini-1.5-flash")
    ],
    load_balancing=True,
    cost_optimization=True
)

client.add_routing_strategy("custom_strategy", strategy)
```

### OpenTelemetry Configuration

```python
# Advanced tracing config
config = TracingConfig(
    service_name="bmad-production",
    service_version="2.0.0",
    environment="production",
    trace_level=TraceLevel.DEBUG,
    exporters=[
        ExporterType.JAEGER,
        ExporterType.OTLP,
        ExporterType.PROMETHEUS
    ],
    jaeger_host="jaeger.example.com",
    jaeger_port=6831,
    otlp_endpoint="http://collector.example.com:4317",
    prometheus_port=9090,
    sample_rate=0.1  # 10% sampling in production
)
```

### OPA Policy Configuration

```python
# Custom policy rule
from bmad.agents.core.opa_policy_engine import PolicyRule, PolicyType

custom_policy = PolicyRule(
    name="custom_resource_limits",
    policy_type=PolicyType.RESOURCE_LIMITS,
    description="Custom resource limits for specific agents",
    rego_code="""
package bmad.custom_limits

default allow = true

allow = false {
    input.subject = "FullstackDeveloper"
    input.context.tokens_used > 20000
}
""",
    priority=50  # Higher priority (lower number)
)

policy_engine.add_policy(custom_policy)
```

## 📊 Monitoring & Metrics

### Prometheus Metrics

De OpenTelemetry integratie exporteert de volgende metrics:

- `bmad_agent_executions_total`: Total agent executions
- `bmad_agent_duration_seconds`: Agent execution duration
- `bmad_workflow_executions_total`: Total workflow executions
- `bmad_workflow_duration_seconds`: Workflow execution duration
- `bmad_active_agents`: Currently active agents
- `bmad_llm_calls_total`: Total LLM API calls
- `bmad_llm_tokens_total`: Total tokens used

### Jaeger Tracing

OpenTelemetry exporteert traces naar Jaeger voor visualisatie:

1. Start Jaeger: `docker run -d -p 16686:16686 jaegertracing/all-in-one`
2. Open browser: `http://localhost:16686`
3. Zoek naar service: `bmad-agents`

### Cost Analysis

```python
# Get cost analysis
cost_analysis = client.get_cost_analysis(days=7)
print(f"Total cost: ${cost_analysis['total_cost']:.4f}")
print(f"Total tokens: {cost_analysis['total_tokens']}")

# Provider breakdown
for provider, breakdown in cost_analysis['provider_breakdown'].items():
    print(f"{provider}: ${breakdown['cost']:.4f}")
```

## 🔒 Security Features

### Policy-Based Access Control

De OPA integratie biedt granular access control:

- **Agent Permissions**: Welke acties elke agent mag uitvoeren
- **Resource Limits**: Maximum tokens, execution time, memory usage
- **Security Policies**: File access, network access, system commands
- **Workflow Policies**: Workflow modification, deletion, production access

### Audit Trail

Alle policy evaluations worden gelogd met:

- Timestamp
- Subject (agent/user)
- Action
- Resource
- Decision (allow/deny)
- Reason
- Trace ID

## 🚀 Performance Benefits

### LangGraph vs Old Async System

| Metric | Old System | LangGraph |
|--------|------------|-----------|
| Async Reliability | ❌ Poor | ✅ Excellent |
| State Management | ❌ Manual | ✅ Automatic |
| Error Handling | ❌ Complex | ✅ Robust |
| Debugging | ❌ Difficult | ✅ Easy |
| Performance | ⚠️ Variable | ✅ Consistent |

### Multi-LLM Routing Benefits

- **Cost Optimization**: Automatische selectie van goedkoopste provider
- **Load Balancing**: Verdeling van requests over providers
- **Automatic Fallback**: Fallback bij provider failures
- **Quality Control**: Confidence scoring voor response kwaliteit

## 🔮 Future Enhancements

### Planned Features

1. **Advanced Routing**
   - Conditional task execution
   - Dynamic workflow modification
   - A/B testing workflows

2. **Enhanced Monitoring**
   - Real-time workflow visualization
   - Performance metrics dashboard
   - Resource usage tracking

3. **Integration Extensions**
   - Meilisearch voor search functionality
   - Kedro voor ML pipeline consistency
   - Zinc voor lightweight logging

4. **Security Features**
   - Advanced OPA policies
   - Role-based access control
   - Audit trail visualization

## 🛠️ Troubleshooting

### Common Issues

#### OpenRouter Connection Issues
```bash
# Check API key
echo $OPENROUTER_API_KEY

# Test connection
python repository_integration_cli.py --test openrouter --verbose
```

#### OPA Policy Evaluation Failures
```bash
# Check OPA server
curl http://localhost:8181/health

# Test policy evaluation
python repository_integration_cli.py --test opa --verbose
```

#### OpenTelemetry Export Issues
```bash
# Check Jaeger
curl http://localhost:16686/api/services

# Check Prometheus
curl http://localhost:9090/api/v1/targets
```

### Debug Mode

Enable debug logging voor alle componenten:

```bash
python repository_integration_cli.py --test all --verbose
```

## 📚 API Reference

### Core Functions

#### OpenRouter
- `OpenRouterClient(api_key)`: Create client
- `generate_response(prompt, strategy_name)`: Generate LLM response
- `get_cost_analysis(days)`: Get cost analysis
- `add_routing_strategy(name, strategy)`: Add custom strategy

#### OpenTelemetry
- `initialize_tracing(config)`: Initialize tracing
- `trace_agent_execution(agent, task)`: Trace agent execution
- `trace_workflow_execution(workflow, workflow_id)`: Trace workflow
- `trace_llm_call(provider, model, tokens)`: Trace LLM call

#### OPA
- `initialize_policy_engine(opa_url)`: Initialize policy engine
- `evaluate_policy(request)`: Evaluate policy
- `validate_agent_action(agent, action, resource)`: Validate action
- `check_workflow_permission(agent, workflow_id, action)`: Check permission

#### Prefect
- `create_prefect_orchestrator()`: Create orchestrator
- `register_workflow_config(config)`: Register workflow
- `create_deployment(workflow_name, tasks)`: Create deployment

#### LangGraph
- `create_workflow_orchestrator()`: Create orchestrator
- `register_workflow(workflow_def)`: Register workflow
- `start_workflow(workflow_name, context)`: Start workflow

## 🤝 Contributing

### Adding New Integrations

1. **Create Module**: Add new module in `bmad/agents/core/`
2. **Add Tests**: Create tests in `tests/backend/`
3. **Update CLI**: Add test method in `repository_integration_cli.py`
4. **Update README**: Document new integration
5. **Update Requirements**: Add dependencies to `requirements.txt`

### Testing New Features

```bash
# Run specific test
python -m pytest tests/backend/test_new_integration.py -v

# Run integration test
python repository_integration_cli.py --test new_integration --verbose
```

## 📄 License

Deze repository integraties zijn onderdeel van het BMAD project en volgen dezelfde licentie.

## 🆘 Support

Voor vragen of problemen met de repository integraties:

1. Check de troubleshooting sectie
2. Review de test cases
3. Open een issue op GitHub
4. Raadpleeg de individuele repository documentatie

---

**🎉 De repository integraties bieden een moderne, schaalbare en betrouwbare foundation voor BMAD workflows!** 