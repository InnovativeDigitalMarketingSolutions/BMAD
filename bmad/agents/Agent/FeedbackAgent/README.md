# FeedbackAgent

## Overview
The FeedbackAgent is responsible for feedback collection, sentiment analysis, and template quality tracking. It works closely with development teams to gather, analyze, and report on user feedback and stakeholder input to drive continuous improvement.

## Enhanced MCP Integration (Phase 2)

### Features
- **Enhanced MCP Tools**: Advanced feedback collection and sentiment analysis capabilities
- **Tracing Integration**: Comprehensive operation tracing for feedback operations
- **Team Collaboration**: Enhanced communication with other agents for feedback reviews
- **Performance Monitoring**: Real-time feedback analysis performance metrics

### Enhanced MCP Commands
- `enhanced-collaborate`: Enhanced inter-agent communication for feedback reviews
- `enhanced-security`: Enhanced security validation for feedback features
- `enhanced-performance`: Enhanced performance optimization for feedback tools
- `trace-operation`: Trace feedback operations
- `trace-performance`: Get performance metrics
- `trace-error`: Trace error scenarios
- `tracing-summary`: Get tracing summary

### Core Functionality
- **Feedback Collection**: Comprehensive feedback gathering from multiple sources
- **Sentiment Analysis**: Advanced sentiment analysis and emotion detection
- **Feedback Summarization**: Automated feedback summarization and trend analysis
- **Template Quality Tracking**: Template quality assessment and improvement suggestions
- **Trend Analysis**: Real-time feedback trend monitoring and prediction
- **Insight Generation**: Automated insight generation from feedback data

### Integration Points
- **ProductOwner**: Product feedback and stakeholder input coordination
- **UXUIDesigner**: User experience feedback and design improvement suggestions
- **QualityGuardian**: Quality feedback and improvement recommendations
- **Retrospective**: Retrospective feedback and process improvement coordination

## Usage

### Basic Commands
```bash
# Collect feedback
python -m bmad.agents.Agent.FeedbackAgent.feedbackagent collect-feedback --feedback-text "The new dashboard is much more user-friendly"

# Analyze sentiment
python -m bmad.agents.Agent.FeedbackAgent.feedbackagent analyze-sentiment --feedback-text "The new dashboard is much more user-friendly"

# Track trends
python -m bmad.agents.Agent.FeedbackAgent.feedbackagent track-trends --timeframe "30 days"

# Enhanced MCP commands
python -m bmad.agents.Agent.FeedbackAgent.feedbackagent enhanced-collaborate
python -m bmad.agents.Agent.FeedbackAgent.feedbackagent trace-operation
```

### Enhanced MCP Integration
The agent now supports enhanced MCP Phase 2 capabilities including:
- Advanced feedback analysis tools
- Real-time sentiment analysis monitoring
- Comprehensive operation tracing
- Enhanced team collaboration features

## Dependencies
- Sentiment analysis libraries (NLTK, TextBlob, VADER)
- Feedback collection tools (Survey platforms, API integrations)
- Data analysis frameworks (Pandas, NumPy, Matplotlib)
- Natural language processing (spaCy, Transformers)

## Resources
- Templates: Feedback templates, sentiment analysis templates, trend analysis templates
- Data: Feedback history, sentiment history, template quality data
- Integration: MCP framework, tracing system, team collaboration tools 