# BMad Method Guiding Principles

The BMad Method is a natural language framework for AI-assisted software development. These principles ensure contributions maintain the method's effectiveness.

## Core Principles

### 1. Dev Agents Must Be Lean

- **Minimize dev agent dependencies**: Development agents that work in IDEs must have minimal context overhead
- **Save context for code**: Every line counts - dev agents should focus on coding, not documentation
- **Web agents can be larger**: Planning agents (PRD Writer, Architect) used in web UI can have more complex tasks and dependencies
- **Small files, loaded on demand**: Multiple small, focused files are better than large files with many branches
- **Class-based architecture**: All agents follow modern Python class-based architecture for consistency and maintainability

### 2. Natural Language First

- **Everything is markdown**: Agents, tasks, templates - all written in plain English
- **No code in core**: The framework itself contains no programming code, only natural language instructions
- **Self-contained templates**: Templates are defined as YAML files with structured sections that include metadata, workflow configuration, and detailed instructions for content generation

### 3. Agent and Task Design

- **Agents define roles**: Each agent is a persona with specific expertise (e.g., Frontend Developer, API Developer, Mobile Developer)
- **Tasks are procedures**: Step-by-step instructions an agent follows to complete work
- **Templates are outputs**: Structured documents with embedded instructions for generation
- **Dependencies matter**: Explicitly declare only what's needed
- **Comprehensive CLI**: All agents provide comprehensive command-line interfaces

### 4. Advanced Services Integration

- **Performance Monitoring**: All agents integrate with real-time performance monitoring
- **Policy Engine**: Rule-based decision making and access control
- **Message Bus**: Event-driven inter-agent communication
- **Context Management**: Persistent context storage and sharing
- **Resource Management**: Structured template and data file management

### 5. Cross-Platform Development Support

- **Mobile Development**: Comprehensive mobile development capabilities
- **Web Development**: Modern web development with advanced frameworks
- **AI/ML Development**: AI and machine learning development support
- **DevOps Integration**: Complete CI/CD pipeline automation
- **Accessibility**: Comprehensive accessibility compliance and support

## Practical Guidelines

### When to Add to Core

- Universal software development needs only
- Doesn't bloat dev agent contexts
- Follows existing agent/task/template patterns
- Supports cross-platform development
- Integrates with advanced services

### When to Create Expansion Packs

- Domain-specific needs beyond software development
- Non-technical domains (business, wellness, education, creative)
- Specialized technical domains (games, infrastructure, mobile)
- Heavy documentation or knowledge bases
- Anything that would bloat core agents

See [Expansion Packs Guide](../docs/expansion-packs.md) for detailed examples and ideas.

### Agent Design Rules

1. **Web/Planning Agents**: Can have richer context, multiple tasks, extensive templates
2. **Dev Agents**: Minimal dependencies, focused on code generation, lean task sets
3. **All Agents**: Clear persona, specific expertise, well-defined capabilities
4. **Class-Based Structure**: All agents follow modern Python class-based architecture
5. **Comprehensive CLI**: All agents provide full command-line interfaces
6. **Resource Management**: All agents include structured resource management
7. **Performance Integration**: All agents integrate with performance monitoring
8. **Event Handling**: All agents support event-driven communication

### Task Writing Rules

1. Write clear step-by-step procedures
2. Use markdown formatting for readability
3. Keep dev agent tasks focused and concise
4. Planning tasks can be more elaborate
5. **Prefer multiple small tasks over one large branching task**
   - Instead of one task with many conditional paths
   - Create multiple focused tasks the agent can choose from
   - This keeps context overhead minimal
6. **Reuse common tasks** - Don't create new document creation tasks
   - Use the existing `create-doc` task
   - Pass the appropriate YAML template with structured sections
   - This maintains consistency and reduces duplication
7. **Include mobile development tasks** for relevant agents
8. **Include AI/ML development tasks** for specialized agents
9. **Include accessibility tasks** for frontend and design agents

### Template Rules

Templates follow the [BMad Document Template](common/utils/bmad-doc-template.md) specification using YAML format:

1. **Structure**: Templates are defined in YAML with clear metadata, workflow configuration, and section hierarchy
2. **Separation of Concerns**: Instructions for LLMs are in `instruction` fields, separate from content
3. **Reusability**: Templates are agent-agnostic and can be used across different agents
4. **Key Components**:
   - `template` block for metadata (id, name, version, output settings)
   - `workflow` block for interaction mode configuration
   - `sections` array defining document structure with nested subsections
   - Each section has `id`, `title`, and `instruction` fields
5. **Advanced Features**:
   - Variable substitution using `{{variable_name}}` syntax
   - Conditional sections with `condition` field
   - Repeatable sections with `repeatable: true`
   - Agent permissions with `owner` and `editors` fields
   - Examples arrays for guidance (never included in output)
6. **Clean Output**: YAML structure ensures all processing logic stays separate from generated content
7. **Mobile Development Templates**: Include mobile-specific templates for relevant agents
8. **AI/ML Templates**: Include AI/ML-specific templates for specialized agents
9. **Accessibility Templates**: Include accessibility templates for frontend and design agents

### Optimization Standards

1. **Preserve Original Functionality**: Never remove existing functionality, only enhance
2. **Class-Based Architecture**: Implement modern Python class structure
3. **Comprehensive CLI**: Provide full command-line interface with help system
4. **Resource Management**: Implement structured template and data file management
5. **Performance Monitoring**: Integrate with advanced performance monitoring
6. **Event Handling**: Implement message bus integration for inter-agent communication
7. **History Tracking**: Implement persistent history management for all activities
8. **Export Capabilities**: Provide multi-format report export (Markdown, CSV, JSON)
9. **Collaboration Features**: Include inter-agent collaboration examples and workflows
10. **Error Handling**: Implement comprehensive error handling and logging

### Mobile Development Guidelines

1. **Cross-Platform Support**: Support React Native, Flutter, and native development
2. **Performance Optimization**: Focus on mobile performance and battery optimization
3. **User Experience**: Design for mobile-first user experience
4. **App Store Compliance**: Ensure app store compliance and guidelines
5. **Testing**: Include comprehensive mobile testing strategies
6. **Deployment**: Support app store deployment and distribution

### AI/ML Development Guidelines

1. **Data Quality**: Ensure high data quality and proper data pipeline
2. **Model Validation**: Implement comprehensive model validation and testing
3. **Ethics & Bias**: Consider AI ethics and bias detection
4. **Explainability**: Implement model explainability and interpretability
5. **Workflow Orchestration**: Use Prefect or similar for workflow orchestration
6. **Performance Monitoring**: Monitor model performance and drift

### Accessibility Guidelines

1. **WCAG Compliance**: Ensure WCAG 2.1 AA compliance
2. **Inclusive Design**: Design for all users, including those with disabilities
3. **Testing**: Include comprehensive accessibility testing
4. **Documentation**: Document accessibility features and compliance
5. **Integration**: Integrate with Shadcn/ui accessibility features

## Advanced Features

### Human-in-the-Loop (HITL) Integration

1. **Approval Gates**: Implement automated approval workflows with human oversight
2. **Decision Points**: Create critical decision points requiring human input
3. **Escalation Handling**: Implement automatic escalation to appropriate stakeholders
4. **Audit Trails**: Maintain complete audit trails for all HITL decisions

### Performance Monitoring

1. **Real-time Metrics**: Implement real-time performance tracking
2. **Historical Analysis**: Provide performance trend analysis and optimization
3. **Resource Optimization**: Implement intelligent resource allocation and load balancing
4. **Quality Assurance**: Provide continuous quality monitoring and improvement

### Inter-Agent Collaboration

1. **Event-Driven Communication**: Use event-driven communication between agents
2. **Context Sharing**: Implement seamless context sharing and synchronization
3. **Workflow Orchestration**: Provide intelligent workflow orchestration and task assignment
4. **Resource Coordination**: Implement coordinated resource management and allocation

## Remember

- The power is in natural language orchestration, not code
- Dev agents code, planning agents plan
- Keep dev agents lean for maximum coding efficiency
- Expansion packs handle specialized domains
- All agents must preserve original functionality while adding enhancements
- Mobile development is now a core capability
- AI/ML development is supported through specialized agents
- Accessibility is a fundamental requirement, not an afterthought
- Performance monitoring and optimization are essential
- Inter-agent collaboration enables complex workflows
