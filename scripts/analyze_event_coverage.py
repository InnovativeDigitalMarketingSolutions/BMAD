#!/usr/bin/env python3
"""
Analyze event coverage and compare with agent functionalities
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def analyze_event_coverage():
    """Analyze event coverage from backup and compare with agent functionalities."""
    
    backup_path = Path("bmad/agents/core/shared_context.json.backup")
    
    print("🔍 Analyzing event coverage from backup...")
    
    if not backup_path.exists():
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    # Read the backup file and extract valid events
    with open(backup_path, 'r') as f:
        content = f.read()
    
    print(f"📊 Backup file has {len(content)} characters")
    
    # Find the corruption point
    lines = content.split('\n')
    corruption_line = -1
    
    for i, line in enumerate(lines):
        if '"data":' in line and '%' in line:
            corruption_line = i
            break
    
    if corruption_line == -1:
        print("✅ No corruption found, analyzing full backup")
        valid_lines = lines
    else:
        print(f"🚨 Found corruption at line {corruption_line + 1}")
        valid_lines = lines[:corruption_line]
    
    # Extract events from valid lines
    events = []
    event_types = defaultdict(int)
    agent_activities = defaultdict(int)
    
    i = 0
    while i < len(valid_lines):
        line = valid_lines[i].strip()
        
        # Look for event start
        if line.startswith('"timestamp"'):
            # Try to extract complete event
            event_lines = []
            brace_count = 0
            event_started = False
            
            # Go back to find the opening brace
            j = i - 1
            while j >= 0:
                if valid_lines[j].strip() == '{':
                    event_started = True
                    event_lines.insert(0, valid_lines[j])
                    brace_count = 1
                    break
                j -= 1
            
            if not event_started:
                i += 1
                continue
            
            # Collect event lines
            j = i
            while j < len(valid_lines) and brace_count > 0:
                line_content = valid_lines[j]
                event_lines.append(line_content)
                
                # Count braces
                brace_count += line_content.count('{') - line_content.count('}')
                
                if brace_count == 0:
                    # Complete event found
                    event_text = '\n'.join(event_lines)
                    
                    # Remove trailing comma if present
                    if event_text.rstrip().endswith(','):
                        event_text = event_text.rstrip().rstrip(',')
                    
                    # Try to parse as JSON
                    try:
                        event_obj = json.loads(event_text)
                        events.append(event_obj)
                        
                        # Count event types
                        event_type = event_obj.get('event', 'unknown')
                        event_types[event_type] += 1
                        
                        # Count agent activities
                        data = event_obj.get('data', {})
                        agent = data.get('agent', 'unknown')
                        agent_activities[agent] += 1
                        
                    except json.JSONDecodeError:
                        pass
                    
                    break
                
                j += 1
            
            i = j + 1
        else:
            i += 1
    
    print(f"📊 Extracted {len(events)} valid events")
    
    # Analyze event coverage
    print("\n📈 Event Type Coverage:")
    print("=" * 50)
    for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {event_type}: {count} events")
    
    print(f"\n📊 Agent Activity Coverage:")
    print("=" * 50)
    for agent, count in sorted(agent_activities.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {agent}: {count} activities")
    
    # Define agent functionalities based on code analysis
    agent_functionalities = {
        "OrchestratorAgent": [
            "workflow_orchestration", "agent_coordination", "escalation_management",
            "metrics_analysis", "report_generation", "workflow_monitoring"
        ],
        "FrontendDeveloperAgent": [
            "component_build", "shadcn_integration", "accessibility_check",
            "figma_parsing", "component_export", "code_review"
        ],
        "BackendDeveloperAgent": [
            "api_development", "database_design", "backend_architecture",
            "api_testing", "performance_optimization"
        ],
        "TestEngineerAgent": [
            "test_execution", "test_planning", "test_automation",
            "quality_assurance", "test_reporting"
        ],
        "QualityGuardianAgent": [
            "quality_gate_check", "code_quality_analysis", "quality_metrics",
            "quality_trends", "quality_improvement"
        ],
        "DevOpsInfraAgent": [
            "deployment", "infrastructure_management", "ci_cd_pipeline",
            "monitoring_setup", "security_scanning"
        ],
        "ProductOwnerAgent": [
            "feature_management", "requirement_analysis", "product_planning",
            "stakeholder_communication", "priority_management"
        ],
        "ScrummasterAgent": [
            "sprint_management", "team_coordination", "agile_practices",
            "retrospective_facilitation", "impediment_removal"
        ],
        "ArchitectAgent": [
            "system_design", "architecture_planning", "technology_selection",
            "design_patterns", "system_integration"
        ],
        "DataEngineerAgent": [
            "data_pipeline", "data_modeling", "etl_processes",
            "data_quality", "data_analytics"
        ],
        "SecurityDeveloperAgent": [
            "security_audit", "vulnerability_assessment", "security_testing",
            "compliance_check", "security_implementation"
        ],
        "MobileDeveloperAgent": [
            "mobile_development", "app_build", "mobile_testing",
            "platform_integration", "mobile_optimization"
        ],
        "FullstackDeveloperAgent": [
            "fullstack_development", "end_to_end_implementation",
            "technology_integration", "cross_platform_development"
        ],
        "UXUIDesignerAgent": [
            "design_system", "user_experience", "interface_design",
            "design_validation", "prototype_creation"
        ],
        "AccessibilityAgent": [
            "accessibility_check", "wcag_compliance", "accessibility_testing",
            "accessibility_improvement", "inclusive_design"
        ],
        "DocumentationAgent": [
            "documentation_creation", "api_documentation", "user_guides",
            "technical_writing", "documentation_maintenance"
        ],
        "FeedbackAgent": [
            "feedback_collection", "user_feedback_analysis", "feedback_processing",
            "improvement_suggestions", "user_satisfaction"
        ],
        "RetrospectiveAgent": [
            "process_analysis", "improvement_identification", "retrospective_facilitation",
            "lessons_learned", "process_optimization"
        ],
        "RnDAgent": [
            "research_analysis", "technology_evaluation", "innovation_research",
            "proof_of_concept", "trend_analysis"
        ],
        "StrategiePartnerAgent": [
            "strategy_planning", "business_analysis", "market_research",
            "strategic_decision", "business_alignment"
        ],
        "ReleaseManagerAgent": [
            "release_planning", "version_management", "deployment_coordination",
            "release_notes", "rollback_planning"
        ],
        "AiDeveloperAgent": [
            "ai_development", "ml_model_development", "ai_integration",
            "ai_testing", "ai_optimization"
        ],
        "WorkflowAutomatorAgent": [
            "workflow_automation", "process_automation", "workflow_optimization",
            "automation_testing", "workflow_monitoring"
        ]
    }
    
    # Analyze coverage vs capabilities
    print(f"\n🔍 Coverage Analysis:")
    print("=" * 50)
    
    total_events = len(events)
    total_functionalities = sum(len(funcs) for funcs in agent_functionalities.values())
    
    print(f"Total Events: {total_events}")
    print(f"Total Agent Functionalities: {total_functionalities}")
    
    # Calculate coverage per agent
    coverage_analysis = {}
    for agent, functionalities in agent_functionalities.items():
        agent_events = agent_activities.get(agent, 0)
        coverage_percentage = (agent_events / total_events * 100) if total_events > 0 else 0
        functionality_coverage = min(agent_events / len(functionalities), 1.0) if functionalities else 0
        
        coverage_analysis[agent] = {
            "events": agent_events,
            "functionalities": len(functionalities),
            "coverage_percentage": coverage_percentage,
            "functionality_coverage": functionality_coverage
        }
    
    print(f"\n📊 Agent Coverage Analysis:")
    print("=" * 50)
    for agent, analysis in sorted(coverage_analysis.items(), key=lambda x: x[1]['events'], reverse=True):
        print(f"  {agent}:")
        print(f"    - Events: {analysis['events']} ({analysis['coverage_percentage']:.1f}%)")
        print(f"    - Functionalities: {analysis['functionalities']}")
        print(f"    - Functionality Coverage: {analysis['functionality_coverage']:.1f}")
    
    # Identify gaps
    print(f"\n🚨 Coverage Gaps:")
    print("=" * 50)
    for agent, analysis in coverage_analysis.items():
        if analysis['events'] == 0:
            print(f"  ❌ {agent}: No events recorded")
        elif analysis['functionality_coverage'] < 0.5:
            print(f"  ⚠️ {agent}: Low functionality coverage ({analysis['functionality_coverage']:.1f})")
    
    return True

if __name__ == "__main__":
    success = analyze_event_coverage()
    sys.exit(0 if success else 1) 