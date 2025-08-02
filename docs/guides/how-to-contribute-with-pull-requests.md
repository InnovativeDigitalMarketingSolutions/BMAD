# How to Contribute with Pull Requests

## Overview

This guide explains how to contribute to the BMad Method project using pull requests. The project has been optimized with class-based agent architecture, comprehensive CLI interfaces, and advanced services integration.

## Prerequisites

- Git installed and configured
- Python 3.8+ installed
- Understanding of the BMad Method architecture
- Familiarity with the agent optimization standards

## Development Environment Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/your-username/BMAD.git
cd BMAD

# Add upstream remote
git remote add upstream https://github.com/InnovativeDigitalMarketingSolutions/BMAD.git
```

### 2. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Verify Setup

```bash
# Test agent functionality
python3 bmad/agents/Agent/FrontendDeveloper/frontenddeveloper.py test
python3 bmad/agents/Agent/Orchestrator/orchestrator.py test

# Test project management
python3 bmad/projects/cli.py list
```

## Understanding the Codebase

### Agent Architecture

All agents follow a consistent class-based architecture:

```python
class AgentName:
    def __init__(self):
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()
        
        # Resource paths
        self.resource_base = Path("/path/to/resources")
        self.template_paths = {...}
        self.data_paths = {...}
        
        # Initialize history
        self.history = []
        self._load_history()

    def show_help(self):
        """Show available commands"""
        pass

    def test_resource_completeness(self):
        """Test if all required resources are available"""
        pass

    def collaborate_example(self):
        """Demonstrate collaboration with other agents"""
        pass
```

### Key Components

1. **Core Services Integration**: All agents integrate with performance monitoring, policy engine, message bus, etc.
2. **Resource Management**: Structured template and data file management
3. **CLI Interface**: Comprehensive command-line interface for all agents
4. **Event Handling**: Message bus integration for inter-agent communication
5. **History Tracking**: Persistent history management
6. **Export Capabilities**: Multi-format report export

### Project Structure

```
bmad/
├── agents/
│   └── Agent/
│       ├── FrontendDeveloper/
│       ├── BackendDeveloper/
│       ├── MobileDeveloper/
│       ├── Orchestrator/
│       └── ...
├── core/
│   ├── communication/
│   ├── agent/
│   ├── policy/
│   ├── data/
│   └── ai/
├── projects/
│   ├── project_manager.py
│   ├── cli.py
│   └── configs/
├── resources/
│   ├── templates/
│   └── data/
└── docs/
```

## Making Changes

### 1. Create a Feature Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Follow Agent Optimization Standards

When modifying agents, ensure they follow the optimization standards:

#### Required Components
- [ ] Class-based architecture
- [ ] Comprehensive CLI interface
- [ ] Resource management
- [ ] Performance monitoring integration
- [ ] Event handling
- [ ] History tracking
- [ ] Export capabilities
- [ ] Collaboration examples
- [ ] Error handling
- [ ] Resource completeness testing

#### Code Quality
- [ ] Preserve all original functionality
- [ ] Add enhancements without removing features
- [ ] Follow Python best practices
- [ ] Include comprehensive error handling
- [ ] Add proper logging
- [ ] Include type hints where appropriate

### 3. Testing Your Changes

```bash
# Test agent functionality
python3 bmad/agents/Agent/YourAgent/youragent.py test

# Test resource completeness
python3 bmad/agents/Agent/YourAgent/youragent.py test-resource-completeness

# Test CLI interface
python3 bmad/agents/Agent/YourAgent/youragent.py help

# Test collaboration
python3 bmad/agents/Agent/YourAgent/youragent.py collaborate
```

### 4. Mobile Development Contributions

When contributing mobile development features:

```bash
# Test mobile development workflows
python3 bmad/agents/Agent/MobileDeveloper/mobiledeveloper.py test

# Test mobile-specific features
python3 bmad/agents/Agent/MobileDeveloper/mobiledeveloper.py create-app --platform react-native
python3 bmad/agents/Agent/MobileDeveloper/mobiledeveloper.py build-component --type button
```

### 5. AI/ML Development Contributions

When contributing AI/ML features:

```bash
# Test AI development workflows
python3 bmad/agents/Agent/AiDeveloper/aidev.py test

# Test AI-specific features
python3 bmad/agents/Agent/AiDeveloper/aidev.py create-model --type classification
python3 bmad/agents/Agent/AiDeveloper/aidev.py optimize-performance
```

## Documentation Updates

### Required Documentation Updates

When making changes, update relevant documentation:

1. **Agent-Specific Documentation**: Update agent markdown files
2. **Core Architecture**: Update `bmad/docs/core-architecture.md`
3. **Expansion Packs**: Update `bmad/docs/expansion-packs.md`
4. **Agent Optimization Guide**: Update `bmad/docs/agent-optimization-guide.md`
5. **Project Management**: Update `bmad/docs/project-management.md`
6. **Guiding Principles**: Update `bmad/docs/GUIDING-PRINCIPLES.md`

### Documentation Standards

- Use clear, concise language
- Include code examples where appropriate
- Update diagrams and workflows
- Include mobile development examples
- Include AI/ML development examples
- Include accessibility considerations

## Commit Guidelines

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build process or auxiliary tool changes

### Examples

```bash
# Agent optimization
feat(FrontendDeveloper): add Shadcn/ui integration and mobile UX capabilities

# New agent
feat(MobileDeveloper): create new cross-platform mobile development agent

# Bug fix
fix(Orchestrator): resolve HITL workflow issue in mobile development

# Documentation
docs(core-architecture): update architecture diagram with advanced services

# Performance improvement
perf(PerformanceMonitor): optimize real-time metrics collection
```

## Pull Request Process

### 1. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill in the PR template

### 2. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Agent Changes
- [ ] FrontendDeveloper
- [ ] BackendDeveloper
- [ ] MobileDeveloper
- [ ] Orchestrator
- [ ] Other: ________

## Testing
- [ ] All tests pass
- [ ] Resource completeness verified
- [ ] CLI interface tested
- [ ] Collaboration examples tested
- [ ] Mobile development tested (if applicable)
- [ ] AI/ML development tested (if applicable)

## Documentation
- [ ] Agent documentation updated
- [ ] Core architecture updated
- [ ] Expansion packs updated
- [ ] Agent optimization guide updated
- [ ] Project management updated
- [ ] Guiding principles updated

## Checklist
- [ ] Code follows optimization standards
- [ ] Original functionality preserved
- [ ] Error handling implemented
- [ ] Logging added
- [ ] Type hints included where appropriate
- [ ] Mobile development considerations included
- [ ] AI/ML development considerations included
- [ ] Accessibility considerations included
```

### 3. Review Process

1. **Automated Checks**: Ensure all automated checks pass
2. **Code Review**: Address reviewer feedback
3. **Testing**: Verify all functionality works as expected
4. **Documentation**: Ensure documentation is complete and accurate
5. **Mobile Testing**: Test mobile development features (if applicable)
6. **AI/ML Testing**: Test AI/ML development features (if applicable)

### 4. Merge Requirements

- All automated checks must pass
- At least one maintainer approval
- All review comments addressed
- Documentation updated
- Tests passing
- Mobile development tested (if applicable)
- AI/ML development tested (if applicable)

## Common Contribution Areas

### Agent Optimizations

1. **Performance Improvements**: Optimize agent performance and resource usage
2. **CLI Enhancements**: Improve command-line interfaces
3. **Resource Management**: Enhance template and data file management
4. **Error Handling**: Improve error handling and recovery
5. **Logging**: Enhance logging and debugging capabilities

### Mobile Development

1. **Cross-Platform Support**: Enhance React Native and Flutter support
2. **Native Development**: Improve iOS and Android native development
3. **Performance Optimization**: Mobile-specific performance improvements
4. **Testing**: Mobile testing frameworks and strategies
5. **Deployment**: App store deployment and distribution

### AI/ML Development

1. **Model Development**: Enhance AI model development capabilities
2. **Workflow Orchestration**: Improve Prefect workflow integration
3. **Performance Monitoring**: AI/ML performance monitoring
4. **Ethics & Bias**: AI ethics and bias detection
5. **Explainability**: Model explainability and interpretability

### Documentation

1. **Architecture Documentation**: Update system architecture documentation
2. **API Documentation**: Improve API documentation
3. **User Guides**: Create and update user guides
4. **Best Practices**: Document best practices and guidelines
5. **Examples**: Provide comprehensive examples and tutorials

## Getting Help

### Resources

- [Core Architecture Guide](core-architecture.md)
- [Agent Optimization Guide](agent-optimization-guide.md)
- [Expansion Packs Guide](expansion-packs.md)
- [Project Management Guide](project-management.md)
- [Guiding Principles](GUIDING-PRINCIPLES.md)

### Community

- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and share ideas
- Pull Requests: Contribute code and improvements

### Support

- Check existing issues and discussions
- Search documentation for answers
- Ask specific questions with code examples
- Provide detailed bug reports with reproduction steps

## Best Practices

### Code Quality

1. **Follow Standards**: Adhere to agent optimization standards
2. **Preserve Functionality**: Never remove existing functionality
3. **Add Tests**: Include comprehensive tests for new features
4. **Document Changes**: Update documentation for all changes
5. **Consider Impact**: Consider impact on other agents and systems

### Mobile Development

1. **Cross-Platform**: Consider cross-platform compatibility
2. **Performance**: Focus on mobile performance and battery optimization
3. **User Experience**: Design for mobile-first user experience
4. **Testing**: Include comprehensive mobile testing
5. **Deployment**: Consider app store deployment requirements

### AI/ML Development

1. **Data Quality**: Ensure high data quality and proper pipelines
2. **Model Validation**: Implement comprehensive model validation
3. **Ethics**: Consider AI ethics and bias detection
4. **Explainability**: Implement model explainability
5. **Performance**: Monitor model performance and drift

### Accessibility

1. **WCAG Compliance**: Ensure WCAG 2.1 AA compliance
2. **Inclusive Design**: Design for all users
3. **Testing**: Include accessibility testing
4. **Documentation**: Document accessibility features
5. **Integration**: Integrate with accessibility frameworks

## Conclusion

Contributing to BMad is a great way to help improve the framework and learn about AI-assisted development. Follow the guidelines, test thoroughly, and maintain high code quality. Your contributions help make BMad better for everyone!
