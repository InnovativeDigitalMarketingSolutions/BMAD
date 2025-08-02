# BMAD Workflow Service

## Overview

The Workflow Service is a microservice responsible for workflow orchestration and management in the BMAD system. It provides comprehensive workflow lifecycle management, execution, monitoring, and state management capabilities.

## Features

### Core Functionality
- **Workflow Management**: Create, read, update, and delete workflows
- **Workflow Execution**: Execute workflows with different execution patterns
- **State Management**: Persistent state management with recovery capabilities
- **Validation**: Comprehensive data validation and sanitization
- **Monitoring**: Real-time workflow monitoring and analytics

### Workflow Types
- **Sequential**: Execute steps in order
- **Parallel**: Execute steps concurrently
- **Conditional**: Execute steps based on conditions
- **Event-driven**: Execute steps based on events
- **Loop**: Execute steps in loops

### Execution Features
- **Step Dependencies**: Define dependencies between workflow steps
- **Timeout Management**: Configurable timeouts for steps
- **Retry Logic**: Automatic retry with configurable retry counts
- **Error Handling**: Comprehensive error handling and recovery
- **Checkpointing**: State checkpointing for recovery

## Architecture

```
Workflow Service Architecture:
├── FastAPI Application (15+ endpoints)
├── Workflow Manager (lifecycle management)
├── Workflow Store (PostgreSQL + Redis)
├── Workflow Validator (data validation)
├── State Manager (state persistence & recovery)
├── Workflow Execution Engine
├── Database Schema (workflows + steps + executions)
├── Caching Layer (Redis)
└── Comprehensive Test Suite (35+ tests)
```

## API Endpoints

### Health & Monitoring
- `GET /health` - Basic health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

### Workflow Management
- `GET /workflows` - List all workflows
- `POST /workflows` - Create new workflow
- `GET /workflows/{id}` - Get workflow details
- `PUT /workflows/{id}` - Update workflow
- `DELETE /workflows/{id}` - Delete workflow

### Workflow Execution
- `POST /workflows/{id}/execute` - Execute workflow
- `GET /executions` - List executions
- `GET /executions/{id}` - Get execution details
- `POST /executions/{id}/cancel` - Cancel execution

### Analytics & Monitoring
- `GET /workflows/{id}/stats` - Get workflow statistics
- `GET /stats` - Get system-wide statistics

### Service Information
- `GET /info` - Service information

## Database Schema

### Workflows Table
```sql
CREATE TABLE workflows (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    workflow_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    config JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    average_duration_seconds DECIMAL(10,2) DEFAULT 0.0
);
```

### Workflow Steps Table
```sql
CREATE TABLE workflow_steps (
    id VARCHAR(255) PRIMARY KEY,
    workflow_id VARCHAR(255) REFERENCES workflows(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    step_type VARCHAR(100) NOT NULL,
    agent_id VARCHAR(255),
    config JSONB DEFAULT '{}',
    dependencies TEXT[] DEFAULT '{}',
    timeout_seconds INTEGER DEFAULT 300,
    retry_count INTEGER DEFAULT 3,
    status VARCHAR(50) DEFAULT 'pending',
    result JSONB,
    error TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Workflow Executions Table
```sql
CREATE TABLE workflow_executions (
    id VARCHAR(255) PRIMARY KEY,
    workflow_id VARCHAR(255) REFERENCES workflows(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    input_data JSONB DEFAULT '{}',
    output_data JSONB,
    step_results JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error TEXT,
    duration_seconds DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/workflow_db"
   export REDIS_URL="redis://localhost:6379/0"
   ```

4. Run the service:
   ```bash
   python -m src.api.main
   ```

## Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_workflow_manager.py

# Run with coverage
pytest --cov=src tests/
```

### Test Coverage
- **Unit Tests**: Core functionality testing
- **Integration Tests**: API endpoint testing
- **Performance Tests**: Load and stress testing

## Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `SERVICE_PORT`: Service port (default: 8000)

### Workflow Configuration
- **Max Steps**: 100 steps per workflow
- **Max Step Name Length**: 255 characters
- **Max Workflow Name Length**: 255 characters
- **Max Description Length**: 1000 characters
- **Max Config Size**: 1MB
- **Max Metadata Size**: 1MB
- **Max Tag Count**: 20 tags

## Usage Examples

### Create a Sequential Workflow
```python
import requests

workflow_data = {
    "name": "Data Processing Workflow",
    "workflow_type": "sequential",
    "description": "Process data through multiple steps",
    "steps": [
        {
            "name": "Data Validation",
            "step_type": "validation",
            "config": {"schema": "data_schema.json"}
        },
        {
            "name": "Data Transformation",
            "step_type": "transformation",
            "config": {"rules": "transform_rules.json"}
        },
        {
            "name": "Data Storage",
            "step_type": "storage",
            "config": {"destination": "database"}
        }
    ]
}

response = requests.post("http://localhost:8000/workflows", json=workflow_data)
workflow_id = response.json()["id"]
```

### Execute a Workflow
```python
execution_data = {
    "input_data": {
        "source_file": "data.csv",
        "processing_rules": "rules.json"
    }
}

response = requests.post(
    f"http://localhost:8000/workflows/{workflow_id}/execute",
    json=execution_data
)
execution_id = response.json()["id"]
```

### Monitor Execution
```python
# Get execution status
response = requests.get(f"http://localhost:8000/executions/{execution_id}")
execution = response.json()

# Get workflow statistics
response = requests.get(f"http://localhost:8000/workflows/{workflow_id}/stats")
stats = response.json()
```

## Development

### Project Structure
```
workflow-service/
├── src/
│   ├── api/
│   │   └── main.py              # FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   ├── workflow_manager.py  # Workflow lifecycle management
│   │   ├── workflow_store.py    # Data persistence
│   │   ├── workflow_validator.py # Data validation
│   │   └── state_manager.py     # State management
│   ├── workflows/               # Workflow templates
│   ├── orchestration/           # Execution orchestration
│   ├── templates/               # Workflow templates
│   └── monitoring/              # Monitoring and analytics
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── performance/             # Performance tests
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

### Contributing
1. Follow the existing code style
2. Add tests for new functionality
3. Update documentation
4. Ensure all tests pass

## Monitoring

### Health Checks
- **Basic Health**: `GET /health`
- **Readiness**: `GET /health/ready`
- **Liveness**: `GET /health/live`

### Metrics
- Workflow execution count
- Success/failure rates
- Average execution time
- Active workflows
- Queue depth

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- Error tracking

## Security

### Authentication
- JWT token validation
- API key authentication
- Role-based access control

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting

## Performance

### Optimization
- Database connection pooling
- Redis caching
- Async execution
- Batch processing

### Scalability
- Horizontal scaling support
- Load balancing
- Database sharding
- Microservice architecture

## Troubleshooting

### Common Issues
1. **Database Connection**: Check DATABASE_URL
2. **Redis Connection**: Check REDIS_URL
3. **Workflow Execution**: Check step dependencies
4. **Performance**: Monitor database and Redis usage

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
python -m src.api.main
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 