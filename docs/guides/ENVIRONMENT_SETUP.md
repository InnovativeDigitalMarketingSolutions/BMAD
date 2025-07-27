# BMAD Repository Integrations - Environment Setup

## 🚀 Complete .env Configuration

Maak een `.env` bestand aan in de root van het project met de volgende configuratie:

```bash
# BMAD Repository Integrations Environment Configuration
# ===================================================

# 🔑 API Keys & Authentication
# ============================

# OpenRouter API Key (voor multi-LLM routing)
# Haal je API key op: https://openrouter.ai/keys
OPENROUTER_API_KEY=your_openrouter_api_key_here

# OpenAI API Key (backup voor directe OpenAI calls)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (voor Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google AI API Key (voor Gemini models)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Mistral AI API Key (voor Mistral models)
MISTRAL_API_KEY=your_mistral_api_key_here

# Cohere API Key (voor Cohere models)
COHERE_API_KEY=your_cohere_api_key_here

# 🔒 Security & Policy Management
# ===============================

# OPA Server URL (voor policy enforcement)
# Standaard: localhost:8181 (docker run -d -p 8181:8181 openpolicyagent/opa run --server)
OPA_URL=http://localhost:8181

# OPA Policy Bundle URL (optioneel, voor remote policies)
OPA_POLICY_BUNDLE_URL=

# 🔍 Observability & Telemetry
# =============================

# OpenTelemetry Service Configuration
OTEL_SERVICE_NAME=bmad-agents
OTEL_SERVICE_VERSION=1.0.0
OTEL_ENVIRONMENT=development

# OpenTelemetry Exporters
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14268/api/traces
OTEL_EXPORTER_PROMETHEUS_PORT=8000

# Jaeger Tracing (voor distributed tracing visualisatie)
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831

# Prometheus Metrics (voor metrics collection)
PROMETHEUS_PORT=9090

# 📊 Monitoring & Logging
# =======================

# Log Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Log Format
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Log File
LOG_FILE=bmad.log

# 🔄 Workflow & Orchestration
# ============================

# Prefect Configuration
PREFECT_API_URL=http://localhost:4200/api
PREFECT_UI_URL=http://localhost:4200

# LangGraph Configuration
LANGGRAPH_PERSIST_DIR=./langgraph_persist
LANGGRAPH_CHECKPOINT_DIR=./langgraph_checkpoints

# 🚀 Development & Testing
# ========================

# Test Mode (true/false)
TEST_MODE=false

# Mock API Responses (voor testing zonder echte API calls)
MOCK_API_RESPONSES=false

# Development Environment
ENVIRONMENT=development

# Debug Mode
DEBUG=false

# 🔧 Performance & Optimization
# =============================

# Max Concurrent Requests
MAX_CONCURRENT_REQUESTS=10

# Request Timeout (seconds)
REQUEST_TIMEOUT=30

# Retry Attempts
MAX_RETRY_ATTEMPTS=3

# Retry Delay (seconds)
RETRY_DELAY=1

# 💰 Cost Management
# ==================

# Cost Tracking Enabled
ENABLE_COST_TRACKING=true

# Cost Alert Threshold (USD)
COST_ALERT_THRESHOLD=10.0

# Daily Cost Limit (USD)
DAILY_COST_LIMIT=50.0

# 📈 Analytics & Metrics
# ======================

# Metrics Collection Enabled
ENABLE_METRICS_COLLECTION=true

# Metrics Export Interval (seconds)
METRICS_EXPORT_INTERVAL=60

# Performance Monitoring
ENABLE_PERFORMANCE_MONITORING=true

# Performance Monitor Configuration
PERFORMANCE_MONITOR_INTERVAL=5.0
PERFORMANCE_MONITOR_HISTORY_SIZE=1000
PERFORMANCE_MONITOR_BASELINE_SMOOTHING=0.1
PERFORMANCE_MONITOR_ALERT_COOLDOWN=300
PERFORMANCE_MONITOR_MAX_ALERTS=1000

# Test Sprites Configuration
TEST_SPRITES_DIR=test_sprites
TEST_SPRITES_ENABLED=true
TEST_SPRITES_AUTO_CREATE=true

# 🔐 Security Settings
# ====================

# Enable Policy Enforcement
ENABLE_POLICY_ENFORCEMENT=true

# Policy Evaluation Mode (strict/lenient)
POLICY_EVALUATION_MODE=strict

# Security Level (low/medium/high)
SECURITY_LEVEL=medium

# 🔄 Integration Settings
# =======================

# Enable OpenRouter Integration
ENABLE_OPENROUTER=true

# Enable OpenTelemetry Integration
ENABLE_OPENTELEMETRY=true

# Enable OPA Integration
ENABLE_OPA=true

# Enable Prefect Integration
ENABLE_PREFECT=true

# Enable LangGraph Integration
ENABLE_LANGGRAPH=true

# Enable Performance Monitor Integration
ENABLE_PERFORMANCE_MONITOR=true

# Enable Test Sprites Integration
ENABLE_TEST_SPRITES=true

# 🌐 External Services
# ====================

# ClickUp Integration (bestaande)
CLICKUP_API_TOKEN=your_clickup_token_here
CLICKUP_TEAM_ID=your_clickup_team_id_here

# Figma Integration (bestaande)
FIGMA_ACCESS_TOKEN=your_figma_token_here

# Slack Integration (optioneel)
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_SIGNING_SECRET=your_slack_signing_secret_here

# GitHub Integration (optioneel)
GITHUB_TOKEN=your_github_token_here

# 🎯 Agent Configuration
# ======================

# Default Agent Timeout (seconds)
DEFAULT_AGENT_TIMEOUT=300

# Agent Retry Policy
AGENT_RETRY_POLICY=exponential_backoff

# Agent Confidence Threshold
AGENT_CONFIDENCE_THRESHOLD=0.7

# 🔧 Advanced Configuration
# =========================

# Custom Model Configurations (JSON)
CUSTOM_MODEL_CONFIG={}

# Policy Rules (JSON)
CUSTOM_POLICY_RULES={}

# Workflow Templates (JSON)
WORKFLOW_TEMPLATES={}
```

## 🔑 Vereiste API Keys

### 1. **OpenRouter API Key** (VERPLICHT)
- **Waarom**: Voor multi-LLM routing en provider integratie
- **Hoe te krijgen**: https://openrouter.ai/keys
- **Kosten**: Gratis tier beschikbaar

### 2. **OpenAI API Key** (AANBEVOLEN)
- **Waarom**: Backup voor directe OpenAI calls
- **Hoe te krijgen**: https://platform.openai.com/api-keys
- **Kosten**: Pay-per-use

### 3. **Anthropic API Key** (OPTIONEEL)
- **Waarom**: Voor Claude models via OpenRouter
- **Hoe te krijgen**: https://console.anthropic.com/
- **Kosten**: Pay-per-use

### 4. **Google AI API Key** (OPTIONEEL)
- **Waarom**: Voor Gemini models via OpenRouter
- **Hoe te krijgen**: https://makersuite.google.com/app/apikey
- **Kosten**: Pay-per-use

### 5. **Mistral API Key** (OPTIONEEL)
- **Waarom**: Voor Mistral models via OpenRouter
- **Hoe te krijgen**: https://console.mistral.ai/
- **Kosten**: Pay-per-use

### 6. **Cohere API Key** (OPTIONEEL)
- **Waarom**: Voor Cohere models via OpenRouter
- **Hoe te krijgen**: https://dashboard.cohere.ai/
- **Kosten**: Pay-per-use

## 🐳 External Services Setup

### 1. **OPA Server** (OPTIONEEL - voor policy enforcement)
```bash
# Start OPA server
docker run -d --name opa-server -p 8181:8181 openpolicyagent/opa run --server

# Test OPA server
curl http://localhost:8181/health
```

### 2. **Jaeger** (OPTIONEEL - voor tracing visualisatie)
```bash
# Start Jaeger
docker run -d --name jaeger -p 16686:16686 -p 6831:6831 jaegertracing/all-in-one

# Open Jaeger UI: http://localhost:16686
```

### 3. **Prometheus** (OPTIONEEL - voor metrics)
```bash
# Start Prometheus
docker run -d --name prometheus -p 9090:9090 prom/prometheus

# Open Prometheus UI: http://localhost:9090
```

## 🚀 Quick Start

### 1. **Minimale Setup** (alleen OpenRouter)
```bash
# Maak .env bestand
cp .env.example .env

# Vul alleen OpenRouter API key in
echo "OPENROUTER_API_KEY=your_actual_key_here" >> .env

# Test integraties
python repository_integration_cli.py --test all
```

### 2. **Complete Setup** (alle services)
```bash
# Maak .env bestand met alle keys
cp .env.example .env

# Vul alle API keys in

# Start external services
docker run -d --name opa-server -p 8181:8181 openpolicyagent/opa run --server
docker run -d --name jaeger -p 16686:16686 -p 6831:6831 jaegertracing/all-in-one
docker run -d --name prometheus -p 9090:9090 prom/prometheus

# Test alle integraties
python repository_integration_cli.py --test all
```

## 📊 Monitoring Dashboards

### 1. **Jaeger Tracing**
- URL: http://localhost:16686
- Functionaliteit: Distributed tracing visualisatie
- Zoek op service name: `bmad-agents`

### 2. **Prometheus Metrics**
- URL: http://localhost:9090
- Functionaliteit: Metrics collection en querying
- Metrics: `bmad_agent_executions_total`, `bmad_workflow_duration_seconds`

### 3. **Prefect UI**
- URL: http://localhost:4200
- Functionaliteit: Workflow monitoring en management
- Start met: `prefect server start`

## 🔧 Troubleshooting

### 1. **OpenRouter 401 Errors**
- Controleer of API key correct is ingesteld
- Controleer of je credits hebt op OpenRouter
- Test met: `curl -H "Authorization: Bearer YOUR_KEY" https://openrouter.ai/api/v1/models`

### 2. **OPA Connection Errors**
- Controleer of OPA server draait: `curl http://localhost:8181/health`
- Start OPA server: `docker run -d -p 8181:8181 openpolicyagent/opa run --server`

### 3. **OpenTelemetry Export Errors**
- Controleer of Jaeger draait: `curl http://localhost:16686`
- Controleer firewall instellingen
- Gebruik console exporter voor development

### 4. **Prefect Connection Errors**
- Start Prefect server: `prefect server start`
- Controleer of port 4200 beschikbaar is
- Test met: `prefect server status`

## 💡 Tips

1. **Start klein**: Begin met alleen OpenRouter API key
2. **Test incrementally**: Test elke integratie apart
3. **Use fallbacks**: De systemen werken ook zonder external services
4. **Monitor costs**: Zet cost limits in je .env
5. **Development mode**: Gebruik `TEST_MODE=true` voor development
6. **Production**: Zet `ENVIRONMENT=production` en `DEBUG=false`

## 🎯 Volgende Stappen

1. **Vul je OpenRouter API key in** in .env
2. **Test de integraties**: `python repository_integration_cli.py --test all`
3. **Start external services** (optioneel)
4. **Integreer in je workflows** via de BMAD agents
5. **Monitor en optimize** via de dashboards 