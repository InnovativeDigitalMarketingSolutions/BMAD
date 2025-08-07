# SecurityDeveloper Agent

## Overview
De SecurityDeveloper Agent bewaakt de security van het platform, voert scans uit en monitort incidenten. Deze agent is gespecialiseerd in security analysis, vulnerability assessment en compliance monitoring.

**✅ Status: FULLY COMPLIANT** - 95/95 tests passing (100% coverage)

## Core Features
- **Security Scanning**: Comprehensive security scans en vulnerability assessment
- **Compliance Monitoring**: OWASP, NIST, ISO27001 compliance checks
- **Incident Response**: Security incident detection en response procedures
- **Threat Assessment**: Real-time threat level assessment en monitoring
- **Penetration Testing**: Automated penetration testing capabilities
- **Message Bus Integration**: Event-driven security coordination

## Quality-First Implementation

### Test Coverage
- **95/95 tests passing** (100% coverage)
- **4 event handlers** met echte functionaliteit
- **6 Message Bus CLI commands** geïmplementeerd
- **12 performance metrics** voor security tracking

### Event Handlers
1. **`handle_security_scan_requested`** - Scan history tracking en performance metrics
2. **`handle_security_scan_completed`** - Scan completion tracking en metrics
3. **`handle_vulnerability_detected`** - Vulnerability analysis met CVSS scoring en recommendations
4. **`handle_security_incident_reported`** - Incident history tracking en severity metrics

### Message Bus CLI Extension
- **`message-bus-status`** - Status van Message Bus integratie
- **`publish-event`** - Event publishing met JSON data support
- **`subscribe-event`** - Event subscription en listening
- **`list-events`** - Overzicht van ondersteunde events
- **`event-history`** - Event history en scan/incident history
- **`performance-metrics`** - Performance metrics display

### Performance Metrics
- Total security scans, scans completed, vulnerabilities found
- Total vulnerabilities detected, high severity vulnerabilities
- Total security incidents, high severity incidents
- Average CVSS score, security scan success rate
- Incident response time, compliance check success rate
- Threat assessment accuracy

## Resource Management
- **Template Paths**: 6 template paths voor security strategie en templates
- **Data Paths**: 3 data paths voor history en changelog
- **Resource Validation**: Complete resource completeness testing

## Enhanced MCP Integration
- **Phase 2 Capabilities**: Advanced tracing en collaboration
- **Security-Specific Tools**: MCP tools voor security scanning en analysis
- **Performance Optimization**: Enhanced performance monitoring
- **Security Validation**: Enterprise security compliance

## CLI Commands
```bash
# Core Commands
python securitydeveloper.py run-security-scan --target application
python securitydeveloper.py vulnerability-assessment --component API
python securitydeveloper.py compliance-check --framework OWASP
python securitydeveloper.py threat-assessment

# Message Bus Commands
python securitydeveloper.py message-bus-status
python securitydeveloper.py publish-event --event-type security_scan_requested --event-data '{"target": "application"}'
python securitydeveloper.py event-history
python securitydeveloper.py performance-metrics

# Enhanced MCP Commands
python securitydeveloper.py enhanced-collaborate
python securitydeveloper.py enhanced-security
python securitydeveloper.py enhanced-performance
```

## Event System
### Input Events
- `security_scan_requested` - Request security scan
- `security_scan_completed` - Notify scan completion
- `vulnerability_detected` - Report vulnerability detection
- `security_incident_reported` - Report security incident

### Output Events
- `security_scan_processing_started` - Security scan processing started
- `security_scan_completion_reported` - Security scan completion reported
- `vulnerability_analysis_completed` - Vulnerability analysis completed
- `vulnerability_analysis_error` - Vulnerability analysis error
- `security_incident_processing` - Security incident processing

## Collaboration
Deze agent werkt samen met andere agents via Message Bus en gedeelde context:
- **BackendDeveloper**: Backend security coordination
- **FrontendDeveloper**: Frontend security coordination
- **TestEngineer**: Security testing coordination
- **DevOpsInfra**: Infrastructure security coordination
- **QualityGuardian**: Security quality metrics sharing

## Resources
- [Security checklist](../../resources/templates/securitydeveloper/security-checklist.md)
- [Incidenten](../../resources/data/securitydeveloper/incidents.md)
- [Agent changelog](changelog.md)
- [Best practices](../../resources/templates/securitydeveloper/best-practices.md)
- [Compliance report template](../../resources/templates/securitydeveloper/compliance-report-template.md)
