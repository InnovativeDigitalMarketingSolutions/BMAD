# Versioning and Releases

## Version Strategy

BMad follows semantic versioning (SemVer) with the format `MAJOR.MINOR.PATCH`.

### Version Components

- **MAJOR**: Breaking changes, major architectural changes
- **MINOR**: New features, agent additions, significant enhancements
- **PATCH**: Bug fixes, minor improvements, documentation updates

## Current Version: 4.0.0 - Agent Optimization & Mobile Development

### Major Features in v4.0.0

#### Complete Agent Optimization
- All agents optimized to class-based Python architecture
- Comprehensive CLI interfaces for all agents
- Advanced resource management and history tracking
- Performance monitoring and metrics collection
- Inter-agent collaboration and event-driven communication
- Multi-format export capabilities (Markdown, CSV, JSON)

#### Advanced Services Integration
- Performance Monitor: Real-time performance tracking and optimization
- Policy Engine: Rule-based decision making and access control
- Message Bus: Event-driven inter-agent communication
- Test Sprites: Component testing and quality assurance
- Supabase Context: Persistent context storage and sharing
- LLM Client: Advanced AI integration capabilities
- Confidence Scoring: Quality assessment and optimization

#### Mobile Development Capabilities
- **MobileDeveloper Agent**: New cross-platform mobile development specialist
  - React Native development
  - Flutter development
  - iOS native development (Swift/SwiftUI)
  - Android native development (Kotlin/Jetpack Compose)
  - PWA development
  - Hybrid development (Cordova/PhoneGap)
  - App store deployment
  - Performance optimization
  - Cross-platform testing

#### Enhanced Frontend Development
- **Shadcn/ui Integration**: Modern UI component library integration
- **Enhanced UXUIDesigner**: Mobile UX capabilities and design system management
- **AccessibilityAgent**: WCAG compliance with Shadcn integration
- **Cross-Platform Support**: Comprehensive cross-platform development

#### Advanced Orchestration
- **Enhanced Orchestrator**: Advanced workflow management with HITL capabilities
- **Mobile Development Workflows**: Complete mobile app development workflows
- **Intelligent Task Assignment**: AI-powered task assignment and load balancing
- **Human-in-the-Loop (HITL)**: Approval workflows and decision points
- **Performance Optimization**: Real-time performance monitoring and optimization

#### Specialized Development Agents
- **AiDeveloper**: AI/ML development with Prefect workflows
- **SecurityDeveloper**: Security implementation and compliance
- **DataEngineer**: Data pipeline development and management
- **DevOpsInfra**: CI/CD pipeline and infrastructure management
- **ReleaseManager**: Release planning and deployment coordination
- **Retrospective**: Process improvement and feedback analysis
- **FeedbackAgent**: Feedback collection and sentiment analysis
- **RnD**: Research and development with innovation generation
- **DocumentationAgent**: Technical documentation and Figma integration

## Release Process

### Pre-Release Checklist

#### Agent Optimization
- [ ] All agents follow class-based architecture
- [ ] All agents have comprehensive CLI interfaces
- [ ] All agents include resource management
- [ ] All agents integrate with performance monitoring
- [ ] All agents support event handling
- [ ] All agents include history tracking
- [ ] All agents provide export capabilities
- [ ] All agents include collaboration examples
- [ ] All agents have error handling
- [ ] All agents pass resource completeness testing

#### Mobile Development
- [ ] MobileDeveloper agent fully functional
- [ ] Mobile development workflows implemented
- [ ] Cross-platform development supported
- [ ] App store deployment workflows included
- [ ] Mobile performance optimization features
- [ ] Mobile testing frameworks integrated

#### AI/ML Development
- [ ] AiDeveloper agent fully functional
- [ ] AI/ML development workflows implemented
- [ ] Model development capabilities included
- [ ] Performance monitoring for AI/ML
- [ ] Ethics and bias detection features
- [ ] Model explainability features

#### Documentation
- [ ] Core architecture documentation updated
- [ ] Expansion packs documentation updated
- [ ] Agent optimization guide created
- [ ] Project management documentation updated
- [ ] Guiding principles updated
- [ ] Version history updated
- [ ] Contribution guide updated

#### Testing
- [ ] All agents pass functionality tests
- [ ] All agents pass resource completeness tests
- [ ] CLI interfaces tested
- [ ] Collaboration examples tested
- [ ] Mobile development tested
- [ ] AI/ML development tested
- [ ] Performance monitoring tested
- [ ] Event handling tested

### Release Steps

1. **Feature Freeze**: Stop adding new features
2. **Testing**: Comprehensive testing of all components
3. **Documentation**: Update all documentation
4. **Version Update**: Update version numbers
5. **Release Notes**: Create comprehensive release notes
6. **Tag Release**: Create git tag for release
7. **Deploy**: Deploy to production
8. **Announce**: Announce release to community

### Version Update Process

#### Update Version Numbers

```bash
# Update version in main files
# bmad/__init__.py
__version__ = "4.0.0"

# bmad/bmad.yaml
version: "4.0.0"

# Update documentation
# bmad/docs/versions.md
## Current Version: V4 - Agent Optimization & Mobile Development
```

#### Create Release Tag

```bash
# Create and push tag
git tag -a v4.0.0 -m "Release v4.0.0: Agent Optimization & Mobile Development"
git push origin v4.0.0
```

#### Update Release Notes

Create comprehensive release notes including:
- Major features and improvements
- New agents and capabilities
- Breaking changes (if any)
- Migration guide (if needed)
- Known issues and limitations
- Future roadmap

## Release History

### v4.0.0 - Agent Optimization & Mobile Development (Current)
- Complete agent optimization to class-based architecture
- Mobile development capabilities with MobileDeveloper agent
- Advanced services integration (Performance Monitor, Policy Engine, Message Bus)
- Enhanced frontend development with Shadcn/ui integration
- Advanced orchestration with HITL capabilities
- Comprehensive documentation updates

### v3.x - Customization & Web Integration
- Full explosion of customizability
- Tasks, Personas, Agent Configurations, Doc Templates
- BMad AGENT with team capabilities
- Web versions for massive context in Gemini
- Single agent with whole team access

### v2.x - Separation of Concerns & Web Building
- Separation of templates for easier customization
- Web versions for extended agent interactions
- 4 hard-coded web variants
- Improved maintainability and flexibility

### v1.x - Foundation
- Simple 7-file system
- Core agents working in harmony
- Agile personas for streamlined development
- Focus on planning phases

## Future Releases

### v4.1.0 - Enhanced Mobile Development
- Additional mobile development frameworks
- Enhanced mobile testing capabilities
- Mobile-specific performance optimization
- Advanced mobile deployment workflows

### v4.2.0 - Advanced AI/ML Integration
- Enhanced AI model development
- Advanced workflow orchestration
- Improved model validation and testing
- Enhanced AI ethics and bias detection

### v4.3.0 - Enterprise Features
- Advanced security features
- Enterprise deployment capabilities
- Enhanced monitoring and analytics
- Advanced collaboration features

### v5.0.0 - Major Architecture Update
- Potential major architectural changes
- New agent types and capabilities
- Advanced orchestration features
- Enhanced cross-platform support

## Migration Guides

### v3.x to v4.0.0

#### Agent Updates
- All agents now use class-based architecture
- CLI interfaces available for all agents
- Resource management integrated
- Performance monitoring included

#### New Capabilities
- Mobile development with MobileDeveloper agent
- Advanced orchestration with HITL
- Enhanced frontend development with Shadcn/ui
- AI/ML development with AiDeveloper agent

#### Breaking Changes
- Agent initialization now requires class instantiation
- CLI commands available for all agents
- Resource paths may have changed
- Event handling now uses message bus

### v2.x to v3.x

#### Major Changes
- BMad AGENT with team capabilities
- Web versions for extended context
- Enhanced customizability
- Improved maintainability

### v1.x to v2.x

#### Major Changes
- Template separation
- Web building capabilities
- Enhanced customization
- Improved structure

## Release Communication

### Release Announcements
- GitHub Releases with detailed notes
- Community announcements
- Documentation updates
- Migration guides

### Support
- GitHub Issues for bug reports
- GitHub Discussions for questions
- Documentation for guides and tutorials
- Community forums for support

## Quality Assurance

### Testing Strategy
- Unit tests for all agents
- Integration tests for workflows
- Performance tests for optimization
- Mobile development tests
- AI/ML development tests
- Accessibility tests

### Code Quality
- Code review process
- Automated testing
- Performance monitoring
- Security scanning
- Documentation validation

### Release Validation
- Feature completeness verification
- Performance validation
- Security validation
- Documentation accuracy
- User experience validation
