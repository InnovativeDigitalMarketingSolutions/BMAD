# ReleaseManager Agent

De ReleaseManager agent is verantwoordelijk voor releaseplanning, changelogs en deployment.

## Status: ✅ **FULLY COMPLIANT**

**Workflow Compliance**: Volledig geïmplementeerd met Quality-First approach
**Test Coverage**: 80/80 tests passing (100% coverage)
**Message Bus Integration**: ✅ Volledig geïmplementeerd
**Enhanced MCP Integration**: ✅ Volledig geïmplementeerd
**Tracing Integration**: ✅ Volledig geïmplementeerd

## Verantwoordelijkheden
- Plannen en coördineren van releases
- Bijhouden van changelogs
- Samenwerken met alle agents voor releasevoorbereiding
- Release lifecycle management (creation, approval, deployment, rollback)
- Performance metrics tracking en monitoring
- Enhanced MCP tool integration voor release management
- OpenTelemetry tracing voor release operations

## Belangrijke resources
- [Changelog](changelog.md)

## Samenwerking & Automatisering

De ReleaseManager werkt nauw samen met:
- **TestEngineer:** Start releaseproces na geslaagde tests.
- **DevOpsInfra:** Automatiseert deployment en monitoring.
- **Product Owner:** Wacht op goedkeuring voor release.
- **Architect:** Checkt of architecturale eisen zijn geborgd.

## Event Handlers & Message Bus Integration

De ReleaseManager kan automatisch events ontvangen en verwerken via de Message Bus:

### Input Events (Subscribed)
- `tests_passed` (TestEngineer): Start release flow.
- `release_approved` (Product Owner): Zet release live.
- `deployment_failed` (DevOpsInfra): Start rollback of notificatie.
- `release_requested`: Handle release creation requests
- `deployment_requested`: Handle deployment requests
- `rollback_requested`: Handle rollback requests
- `version_update_requested`: Handle version update requests

### Output Events (Published)
- `release_created`: Notify release creation
- `release_approved`: Notify release approval
- `release_deployed`: Notify successful deployment
- `release_rolled_back`: Notify rollback completion
- `version_updated`: Notify version updates

## CLI Commands

### Core Release Management
- `create-release`: Create new release plan
- `approve-release`: Approve release for deployment
- `deploy-release`: Deploy release to production
- `rollback-release`: Rollback failed release

### Message Bus Integration
- `message-bus-status`: Show Message Bus status
- `publish-event`: Publish release management events
- `subscribe-event`: Show subscribed events
- `list-events`: List supported events
- `event-history`: Show event history
- `performance-metrics`: Show performance metrics

### Enhanced MCP Phase 2
- `enhanced-collaborate`: Enhanced collaboration with other agents
- `enhanced-security`: Enhanced security validation
- `enhanced-performance`: Enhanced performance optimization
- `trace-operation`: Trace release operations
- `trace-performance`: Trace performance metrics
- `trace-error`: Trace error analysis
- `tracing-summary`: Show tracing status
