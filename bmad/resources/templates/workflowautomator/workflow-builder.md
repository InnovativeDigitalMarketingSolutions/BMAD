# Workflow Builder Template

## Overview
This template provides guidelines and best practices for creating automated workflows with the WorkflowAutomator agent.

## Workflow Creation Guidelines

### 1. Workflow Structure
```yaml
workflow:
  name: "Feature Development Workflow"
  description: "Complete workflow for developing new features"
  priority: "normal"
  steps:
    - id: "step-1"
      agent: "ProductOwner"
      command: "create-epic"
      parameters:
        title: "New Feature Epic"
        description: "Epic description"
      dependencies: []
      timeout: 300
      retry_count: 3
```

### 2. Agent Coordination
- **Sequential Execution**: Steps that depend on each other
- **Parallel Execution**: Independent steps that can run simultaneously
- **Conditional Execution**: Steps that run based on conditions
- **Error Handling**: Steps that handle failures gracefully

### 3. Best Practices

#### Workflow Design
- Keep workflows modular and focused
- Use descriptive names and descriptions
- Set appropriate timeouts and retry counts
- Include error handling steps

#### Performance Optimization
- Identify parallel execution opportunities
- Minimize dependencies between steps
- Use appropriate agent selection
- Monitor execution times

#### Error Handling
- Include recovery steps
- Set appropriate retry counts
- Handle partial failures
- Provide fallback mechanisms

## Template Examples

### Basic Feature Development Workflow
```yaml
workflow:
  name: "Basic Feature Development"
  steps:
    - agent: "ProductOwner"
      command: "create-epic"
      dependencies: []
    - agent: "Scrummaster"
      command: "create-sprint"
      dependencies: ["step-1"]
    - agent: "FrontendDeveloper"
      command: "develop-feature"
      dependencies: ["step-2"]
    - agent: "BackendDeveloper"
      command: "develop-api"
      dependencies: ["step-2"]
    - agent: "TestEngineer"
      command: "test-feature"
      dependencies: ["step-3", "step-4"]
    - agent: "QualityGuardian"
      command: "quality-gate-check"
      dependencies: ["step-5"]
```

### Advanced Workflow with Parallel Execution
```yaml
workflow:
  name: "Advanced Feature Development"
  steps:
    - agent: "StrategiePartner"
      command: "validate-idea"
      dependencies: []
    - agent: "ProductOwner"
      command: "create-epic"
      dependencies: ["step-1"]
    - agent: "Architect"
      command: "design-architecture"
      dependencies: ["step-2"]
    - agent: "Scrummaster"
      command: "create-sprint"
      dependencies: ["step-2"]
    - agent: "FrontendDeveloper"
      command: "develop-ui"
      dependencies: ["step-3", "step-4"]
    - agent: "BackendDeveloper"
      command: "develop-api"
      dependencies: ["step-3", "step-4"]
    - agent: "DataEngineer"
      command: "setup-database"
      dependencies: ["step-3"]
    - agent: "TestEngineer"
      command: "test-integration"
      dependencies: ["step-5", "step-6", "step-7"]
    - agent: "QualityGuardian"
      command: "quality-gate-check"
      dependencies: ["step-8"]
    - agent: "DevOpsInfra"
      command: "deploy-production"
      dependencies: ["step-9"]
```

### Conditional Workflow
```yaml
workflow:
  name: "Conditional Feature Development"
  steps:
    - agent: "StrategiePartner"
      command: "validate-idea"
      dependencies: []
    - agent: "ProductOwner"
      command: "create-epic"
      dependencies: ["step-1"]
      condition: "idea_validation_score > 70"
    - agent: "Architect"
      command: "design-architecture"
      dependencies: ["step-2"]
      condition: "epic_created = true"
    - agent: "Scrummaster"
      command: "create-sprint"
      dependencies: ["step-3"]
      condition: "architecture_designed = true"
```

## Configuration Options

### Timeout Settings
- **Short tasks**: 60-300 seconds
- **Medium tasks**: 300-1800 seconds
- **Long tasks**: 1800+ seconds

### Retry Settings
- **Critical tasks**: 5 retries
- **Important tasks**: 3 retries
- **Optional tasks**: 1 retry

### Priority Levels
- **Critical**: Immediate execution
- **High**: High priority execution
- **Normal**: Standard execution
- **Low**: Low priority execution

## Validation Rules

### Required Fields
- Workflow name
- At least one step
- Agent and command for each step

### Validation Checks
- Agent exists and is available
- Command is valid for the agent
- Dependencies are valid
- Timeout values are reasonable
- Retry counts are appropriate

## Error Handling

### Common Errors
1. **Agent not available**: Use fallback agent or retry
2. **Command failed**: Retry with different parameters
3. **Timeout exceeded**: Increase timeout or optimize step
4. **Dependency failed**: Skip dependent steps or use alternative

### Recovery Strategies
1. **Automatic retry**: Retry failed steps
2. **Fallback agents**: Use alternative agents
3. **Skip steps**: Skip non-critical steps
4. **Manual intervention**: Require human intervention

## Monitoring and Metrics

### Key Metrics
- Execution time per step
- Success rate per step
- Overall workflow success rate
- Resource utilization
- Error frequency

### Alerting
- Workflow failures
- Performance degradation
- Resource exhaustion
- Error rate increases

## Best Practices Summary

1. **Design for reliability**: Include error handling and recovery
2. **Optimize for performance**: Use parallel execution where possible
3. **Monitor execution**: Track metrics and performance
4. **Document workflows**: Keep documentation up to date
5. **Test thoroughly**: Test workflows before production use
6. **Iterate and improve**: Continuously optimize workflows 