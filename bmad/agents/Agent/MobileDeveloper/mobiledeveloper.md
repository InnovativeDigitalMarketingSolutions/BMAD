# MobileDeveloper Agent

## Overview
De MobileDeveloper Agent is gespecialiseerd in cross-platform mobile development, React Native, Flutter, iOS en Android development. Deze agent biedt uitgebreide functionaliteit voor app development, component building, performance optimization, testing en deployment.

## Core Features
- **Cross-Platform Development**: React Native, Flutter, iOS, Android
- **App Creation**: Complete mobile app development workflow
- **Component Building**: Platform-specific UI components
- **Performance Optimization**: Memory, battery, network optimization
- **Testing**: Unit, integration, and end-to-end testing
- **Deployment**: App Store, Google Play, TestFlight deployment
- **Performance Analysis**: Comprehensive performance monitoring

## MCP Integration

### Standard MCP
- **MCP Client**: Basic MCP client integration
- **Framework Integration**: FrameworkMCPIntegration support
- **Tool Usage**: Standard MCP tool utilization

### Mobile-Specific MCP Tools
- **Platform Tools**: React Native, Flutter, iOS, Android specific tools
- **Development Tools**: App creation, component building tools
- **Performance Tools**: Optimization and analysis tools
- **Deployment Tools**: App Store and Play Store deployment tools

### Enhanced MCP Phase 2
- **Enhanced MCP Integration**: Advanced MCP capabilities
- **Inter-Agent Communication**: Communication with other agents
- **External Tool Integration**: Integration with external development tools
- **Security Enhancement**: Advanced security validation
- **Performance Optimization**: Enhanced performance optimization

### Tracing Integration
- **App Development Tracing**: Trace app development process
- **Mobile Performance Tracing**: Trace performance optimization
- **Mobile Deployment Tracing**: Trace deployment process
- **Mobile Error Tracing**: Trace errors and exceptions

## Enhanced CLI Commands

### Enhanced MCP Phase 2 Commands
```bash
# Enhanced inter-agent communication
python mobiledeveloper.py enhanced-collaborate --agents FrontendDeveloper BackendDeveloper --message "Sync mobile requirements"

# Enhanced security validation
python mobiledeveloper.py enhanced-security --platform ios --app-type business

# Enhanced performance optimization
python mobiledeveloper.py enhanced-performance --optimization-type general --platform react-native

# Enhanced external tool integration
python mobiledeveloper.py enhanced-tools --tool-config '{"tool":"firebase","config":{"project":"myapp"}}'

# Enhanced performance & communication summary
python mobiledeveloper.py enhanced-summary
```

### Tracing Commands
```bash
# Trace app development process
python mobiledeveloper.py trace-app --app-data '{"app_name":"MyApp","platform":"react-native"}'

# Trace mobile performance optimization
python mobiledeveloper.py trace-performance --performance-data '{"type":"general","platform":"react-native"}'

# Trace mobile app deployment
python mobiledeveloper.py trace-deployment --deployment-data '{"target":"app-store","platform":"ios"}'

# Trace mobile errors and exceptions
python mobiledeveloper.py trace-error --error-data '{"type":"crash","message":"Test error"}'

# Get tracing summary and analytics
python mobiledeveloper.py tracing-summary
```

## Usage Examples

### Python Code Examples
```python
from bmad.agents.Agent.MobileDeveloper.mobiledeveloper import MobileDeveloperAgent

# Initialize agent
agent = MobileDeveloperAgent()

# Create app with enhanced MCP and tracing
result = await agent.create_app("MyApp", "react-native", "business")

# Use enhanced MCP tools
enhanced_data = await agent.use_enhanced_mcp_tools({
    "app_name": "MyApp",
    "platform": "react-native",
    "capabilities": ["app_development", "performance_optimization"]
})

# Communicate with other agents
communication_result = await agent.communicate_with_agents(
    ["FrontendDeveloper", "BackendDeveloper"],
    {"message": "Sync mobile requirements"}
)

# Trace app development
trace_result = await agent.trace_app_development({
    "app_name": "MyApp",
    "platform": "react-native",
    "app_type": "business"
})

# Get enhanced performance summary
performance_summary = agent.get_enhanced_performance_summary()

# Get tracing summary
tracing_summary = agent.get_tracing_summary()
```

## Integration Points
- **FrontendDeveloper**: UI component collaboration
- **BackendDeveloper**: API integration and backend services
- **TestEngineer**: Testing strategy and quality assurance
- **DevOpsInfra**: CI/CD and deployment automation
- **SecurityDeveloper**: Security validation and compliance

## Performance Metrics
- **App Creation Time**: < 5 seconds
- **Component Building**: < 2 seconds
- **Performance Optimization**: < 10 seconds
- **Testing Execution**: < 30 seconds
- **Deployment Process**: < 60 seconds

## Dependencies
- **Core Dependencies**: MCP client, performance monitor, policy engine
- **Enhanced Dependencies**: Enhanced MCP integration, tracing system
- **External Dependencies**: React Native, Flutter, iOS SDK, Android SDK
- **Testing Dependencies**: Jest, Detox, Espresso, XCTest 