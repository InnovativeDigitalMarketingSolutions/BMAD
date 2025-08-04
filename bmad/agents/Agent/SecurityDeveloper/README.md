# SecurityDeveloper Agent

## Overview
The SecurityDeveloper agent is responsible for security analysis, vulnerability assessment, and compliance monitoring. It works closely with development teams to ensure secure coding practices, perform security scans, and maintain compliance with security standards.

## Enhanced MCP Integration (Phase 2)

### Features
- **Enhanced MCP Tools**: Advanced security analysis and vulnerability assessment capabilities
- **Tracing Integration**: Comprehensive operation tracing for security operations
- **Team Collaboration**: Enhanced communication with other agents for security reviews
- **Performance Monitoring**: Real-time security performance metrics

### Enhanced MCP Commands
- `enhanced-collaborate`: Enhanced inter-agent communication for security reviews
- `enhanced-security`: Enhanced security validation for security features
- `enhanced-performance`: Enhanced performance optimization for security tools
- `trace-operation`: Trace security operations
- `trace-performance`: Get performance metrics
- `trace-error`: Trace error scenarios
- `tracing-summary`: Get tracing summary

### Core Functionality
- **Security Scanning**: Comprehensive security vulnerability scanning and assessment
- **Vulnerability Assessment**: Advanced vulnerability analysis and CVSS scoring
- **Compliance Monitoring**: OWASP, NIST, ISO27001, GDPR, SOC2 compliance checking
- **Threat Assessment**: Real-time threat intelligence and assessment
- **Incident Response**: Automated incident detection and response workflows
- **Penetration Testing**: Automated and manual penetration testing capabilities

### Integration Points
- **DevOpsInfra**: Security infrastructure and deployment coordination
- **BackendDeveloper**: Secure coding practices and API security
- **FrontendDeveloper**: Frontend security and input validation
- **QualityGuardian**: Security quality gates and validation

## Usage

### Basic Commands
```bash
# Run security scan
python -m bmad.agents.Agent.SecurityDeveloper.securitydeveloper run-security-scan --target application

# Vulnerability assessment
python -m bmad.agents.Agent.SecurityDeveloper.securitydeveloper vulnerability-assessment --component API

# Compliance check
python -m bmad.agents.Agent.SecurityDeveloper.securitydeveloper compliance-check --framework OWASP

# Enhanced MCP commands
python -m bmad.agents.Agent.SecurityDeveloper.securitydeveloper enhanced-collaborate
python -m bmad.agents.Agent.SecurityDeveloper.securitydeveloper trace-operation
```

### Enhanced MCP Integration
The agent now supports enhanced MCP Phase 2 capabilities including:
- Advanced security analysis tools
- Real-time security metrics monitoring
- Comprehensive operation tracing
- Enhanced team collaboration features

## Dependencies
- Security scanning tools (OWASP ZAP, Snyk, SonarQube Security)
- Vulnerability databases (NVD, CVE, CWE)
- Compliance frameworks (OWASP, NIST, ISO27001, GDPR, SOC2)
- Threat intelligence feeds (OSINT, DarkWeb, Vendor)

## Resources
- Templates: Security scan templates, compliance reports, incident response playbooks
- Data: Scan history, incident logs, vulnerability databases
- Integration: MCP framework, tracing system, team collaboration tools 