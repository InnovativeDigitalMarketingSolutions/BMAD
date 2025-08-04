# QualityGuardian Agent

## Overview
The QualityGuardian agent is responsible for quality assurance, testing oversight, and quality gate management. It works closely with development teams to ensure high-quality software delivery and maintain quality standards across all development phases.

## Enhanced MCP Integration (Phase 2)

### Features
- **Enhanced MCP Tools**: Advanced quality assurance and testing capabilities
- **Tracing Integration**: Comprehensive operation tracing for quality operations
- **Team Collaboration**: Enhanced communication with other agents for quality reviews
- **Performance Monitoring**: Real-time quality metrics and performance tracking

### Enhanced MCP Commands
- `enhanced-collaborate`: Enhanced inter-agent communication for quality reviews
- `enhanced-security`: Enhanced security validation for quality features
- `enhanced-performance`: Enhanced performance optimization for quality tools
- `trace-operation`: Trace quality operations
- `trace-performance`: Get performance metrics
- `trace-error`: Trace error scenarios
- `tracing-summary`: Get tracing summary

### Core Functionality
- **Quality Gates**: Automated quality gate management and validation
- **Test Oversight**: Comprehensive test strategy and execution oversight
- **Code Quality Analysis**: Static code analysis and quality metrics
- **Performance Testing**: Performance testing and optimization guidance
- **Security Validation**: Security testing and compliance validation
- **Quality Reporting**: Quality metrics reporting and trend analysis

### Integration Points
- **TestEngineer**: Test strategy coordination and execution oversight
- **BackendDeveloper**: Code quality validation and performance testing
- **FrontendDeveloper**: Frontend quality assurance and accessibility testing
- **SecurityDeveloper**: Security testing coordination and compliance validation

## Usage

### Basic Commands
```bash
# Run quality gates
python -m bmad.agents.Agent.QualityGuardian.qualityguardian run-quality-gates --stage production

# Analyze code quality
python -m bmad.agents.Agent.QualityGuardian.qualityguardian analyze-code-quality --target backend

# Performance testing
python -m bmad.agents.Agent.QualityGuardian.qualityguardian performance-test --service api-gateway

# Enhanced MCP commands
python -m bmad.agents.Agent.QualityGuardian.qualityguardian enhanced-collaborate
python -m bmad.agents.Agent.QualityGuardian.qualityguardian trace-operation
```

### Enhanced MCP Integration
The agent now supports enhanced MCP Phase 2 capabilities including:
- Advanced quality assurance tools
- Real-time quality metrics monitoring
- Comprehensive operation tracing
- Enhanced team collaboration features

## Dependencies
- Code quality tools (SonarQube, ESLint, Pylint)
- Testing frameworks (Jest, PyTest, Selenium)
- Performance testing tools (JMeter, Artillery, K6)
- Security scanning tools (OWASP ZAP, Snyk, SonarQube Security)

## Resources
- Templates: Quality gate templates, test strategy frameworks, quality metrics dashboards
- Data: Quality metrics history, test results, performance benchmarks
- Integration: MCP framework, tracing system, team collaboration tools 