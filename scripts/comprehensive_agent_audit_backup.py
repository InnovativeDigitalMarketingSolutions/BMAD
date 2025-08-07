#!/usr/bin/env python3
"""
Comprehensive Agent Audit Script

This script performs a complete audit of all agents including:
- Required attributes and methods
- Documentation completeness
- Resource availability
- Dependencies
- Test coverage
- Enhanced MCP integration
- Tracing integration
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional
import ast

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_all_agent_files() -> List[Path]:
    """Get all agent Python files."""
    agent_dir = project_root / "bmad" / "agents" / "Agent"
    agent_files = []
    
    for agent_folder in agent_dir.iterdir():
        if agent_folder.is_dir():
            # Look for main agent file (usually agentname.py or agentnameagent.py)
            for py_file in agent_folder.glob("*.py"):
                if not py_file.name.startswith("__"):
                    agent_files.append(py_file)
                    break
    
    return agent_files

def get_required_attributes() -> List[str]:
    """Get list of required attributes for all agents."""
    return [
        'mcp_client',
        'enhanced_mcp', 
        'enhanced_mcp_enabled',
        'tracing_enabled',
        'agent_name',
        'message_bus_integration'
    ]

def get_required_methods() -> List[str]:
    """Get list of required methods for all agents."""
    return [
        'initialize_enhanced_mcp',
        'get_enhanced_mcp_tools',
        'register_enhanced_mcp_tools', 
        'trace_operation'
    ]

def check_documentation_completeness(agent_file: Path) -> Dict[str, Any]:
    """Check if agent has complete documentation."""
    try:
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file
        tree = ast.parse(content)
        
        # Find the main agent class
        agent_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and 'Agent' in node.name and node.name != 'AgentMessageBusIntegration':
                agent_class = node
                break
        
        if not agent_class:
            return {
                'status': 'error',
                'message': 'No agent class found'
            }
        
        # Check for docstring
        has_docstring = ast.get_docstring(agent_class) is not None
        
        # Check for method docstrings
        method_docstrings = 0
        total_methods = 0
        
        for node in ast.walk(agent_class):
            if isinstance(node, ast.FunctionDef):
                total_methods += 1
                if ast.get_docstring(node) is not None:
                    method_docstrings += 1
        
        docstring_coverage = method_docstrings / total_methods if total_methods > 0 else 0
        
        return {
            'status': 'complete',
            'has_class_docstring': has_docstring,
            'method_docstring_coverage': docstring_coverage,
            'total_methods': total_methods,
            'documented_methods': method_docstrings
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def check_resource_availability(agent_file: Path) -> Dict[str, Any]:
    """Check if agent has required resources."""
    agent_name = agent_file.parent.name
    resource_dir = project_root / "bmad" / "resources"
    
    # Check for YAML configuration
    yaml_file = agent_file.parent / f"{agent_name.lower()}.yaml"
    has_yaml = yaml_file.exists()
    
    # Check for markdown documentation
    md_file = agent_file.parent / f"{agent_name.lower()}.md"
    has_md = md_file.exists()
    
    # Check for templates - handle special cases for agent names
    template_name = agent_name.lower()
    if template_name == "aideveloper":
        template_name = "ai"
    elif template_name == "backenddeveloper":
        template_name = "backenddeveloper"
    elif template_name == "frontenddeveloper":
        template_name = "frontenddeveloper"
    elif template_name == "fullstackdeveloper":
        template_name = "fullstackdeveloper"
    elif template_name == "mobiledeveloper":
        template_name = "mobiledeveloper"
    elif template_name == "dataengineer":
        template_name = "dataengineer"
    elif template_name == "testengineer":
        template_name = "testengineer"
    elif template_name == "securitydeveloper":
        template_name = "securitydeveloper"
    elif template_name == "uxuidesigner":
        template_name = "uxuidesigner"
    elif template_name == "accessibilityagent":
        template_name = "accessibilityagent"
    elif template_name == "documentationagent":
        template_name = "documentationagent"
    elif template_name == "feedbackagent":
        template_name = "feedbackagent"
    elif template_name == "qualityguardian":
        template_name = "qualityguardian"
    elif template_name == "workflowautomator":
        template_name = "workflowautomator"
    elif template_name == "orchestrator":
        template_name = "orchestrator"
    elif template_name == "rnd":
        template_name = "rnd"
    elif template_name == "retrospective":
        template_name = "retrospective"
    elif template_name == "releasemanager":
        template_name = "releasemanager"
    elif template_name == "devopsinfra":
        template_name = "devopsinfra"
    elif template_name == "scrummaster":
        template_name = "scrummaster"
    elif template_name == "strategiepartner":
        template_name = "strategiepartner"
    elif template_name == "architect":
        template_name = "architect"
    elif template_name == "productowner":
        template_name = "productowner"
    
    template_dir = resource_dir / "templates" / template_name
    has_templates = template_dir.exists() and any(template_dir.iterdir())
    
    # Check for data files - handle special cases for agent names
    data_name = agent_name.lower()
    if data_name == "aideveloper":
        data_name = "ai"
    elif data_name == "backenddeveloper":
        data_name = "backenddeveloper"
    elif data_name == "frontenddeveloper":
        data_name = "frontenddeveloper"
    elif data_name == "fullstackdeveloper":
        data_name = "fullstackdeveloper"
    elif data_name == "mobiledeveloper":
        data_name = "mobiledeveloper"
    elif data_name == "dataengineer":
        data_name = "dataengineer"
    elif data_name == "testengineer":
        data_name = "testengineer"
    elif data_name == "securitydeveloper":
        data_name = "securitydeveloper"
    elif data_name == "uxuidesigner":
        data_name = "uxuidesigner"
    elif data_name == "accessibilityagent":
        data_name = "accessibilityagent"
    elif data_name == "documentationagent":
        data_name = "documentationagent"
    elif data_name == "feedbackagent":
        data_name = "feedbackagent"
    elif data_name == "qualityguardian":
        data_name = "qualityguardian"
    elif data_name == "workflowautomator":
        data_name = "workflowautomator"
    elif data_name == "orchestrator":
        data_name = "orchestrator"
    elif data_name == "rnd":
        data_name = "rnd"
    elif data_name == "retrospective":
        data_name = "retrospective"
    elif data_name == "releasemanager":
        data_name = "releasemanager"
    elif data_name == "devopsinfra":
        data_name = "devopsinfra"
    elif data_name == "scrummaster":
        data_name = "scrummaster"
    elif data_name == "strategiepartner":
        data_name = "strategiepartner"
    elif data_name == "architect":
        data_name = "architect"
    elif data_name == "productowner":
        data_name = "productowner"
    
    data_dir = resource_dir / "data" / data_name
    has_data = data_dir.exists() and any(data_dir.iterdir())
    
    return {
        'has_yaml_config': has_yaml,
        'has_markdown_docs': has_md,
        'has_templates': has_templates,
        'has_data_files': has_data,
        'resource_completeness': sum([has_yaml, has_md, has_templates, has_data]) / 4
    }

def check_dependencies(agent_file: Path) -> Dict[str, Any]:
    """Check if agent has all required dependencies."""
    try:
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse imports
        tree = ast.parse(content)
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        # Check for required imports
        required_imports = [
            'bmad.core.mcp',
            'bmad.core.tracing',
            'bmad.core.message_bus',
            'integrations.opentelemetry.opentelemetry_tracing',
            'bmad.agents.core.communication.agent_message_bus_integration'
        ]
        
        missing_imports = []
        for required in required_imports:
            if not any(required in imp for imp in imports):
                missing_imports.append(required)
        
        return {
            'total_imports': len(imports),
            'missing_imports': missing_imports,
            'import_completeness': (len(required_imports) - len(missing_imports)) / len(required_imports)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def check_test_coverage(agent_file: Path) -> Dict[str, Any]:
    """Check if agent has test coverage."""
    agent_name = agent_file.parent.name
    
    # Check for unit tests with multiple possible naming patterns
    unit_test_patterns = [
        f"test_{agent_name.lower()}.py",
        f"test_{agent_name.lower()}_agent.py",
        f"test_{agent_name.lower().replace('developer', '')}_agent.py",
        f"test_fullstack_developer_agent.py"  # Special case for FullstackDeveloper
    ]
    
    has_unit_tests = False
    for pattern in unit_test_patterns:
        test_file = project_root / "tests" / "unit" / "agents" / pattern
        if test_file.exists():
            has_unit_tests = True
            break
    
    # Check for integration tests
    integration_test_file = project_root / "tests" / "integration" / f"test_{agent_name.lower()}_integration.py"
    has_integration_tests = integration_test_file.exists()
    
    return {
        'has_unit_tests': has_unit_tests,
        'has_integration_tests': has_integration_tests,
        'test_coverage': 'complete' if has_unit_tests and has_integration_tests else 'partial' if has_unit_tests or has_integration_tests else 'none'
    }

def comprehensive_agent_audit(agent_file: Path) -> Dict[str, Any]:
    """Perform comprehensive audit of an agent."""
    print(f"\n🔍 Auditing {agent_file.name}...")
    
    try:
        # Import the agent module
        module_name = f"bmad.agents.Agent.{agent_file.parent.name}.{agent_file.stem}"
        module = importlib.import_module(module_name)
        
        # Find the agent class
        agent_class = None
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and 'Agent' in name and name != 'AgentMessageBusIntegration':
                agent_class = obj
                break
        
        if not agent_class:
            return {
                'file': str(agent_file),
                'status': 'error',
                'message': 'No agent class found'
            }
        
        # Check attributes
        missing_attributes = []
        for attr in get_required_attributes():
            if not hasattr(agent_class, attr):
                missing_attributes.append(attr)
        
        # Check methods
        missing_methods = []
        for method in get_required_methods():
            if not hasattr(agent_class, method):
                missing_methods.append(method)
        
        # Check documentation
        doc_check = check_documentation_completeness(agent_file)
        
        # Check resources
        resource_check = check_resource_availability(agent_file)
        
        # Check dependencies
        dependency_check = check_dependencies(agent_file)
        
        # Check test coverage
        test_check = check_test_coverage(agent_file)
        
        # Calculate overall completeness
        implementation_score = 1.0 if not missing_attributes and not missing_methods else 0.5
        documentation_score = doc_check.get('method_docstring_coverage', 0) if doc_check['status'] == 'complete' else 0
        resource_score = resource_check['resource_completeness']
        dependency_score = dependency_check['import_completeness']
        test_score = 1.0 if test_check['test_coverage'] == 'complete' else 0.5 if test_check['test_coverage'] == 'partial' else 0.0
        
        overall_score = (implementation_score + documentation_score + resource_score + dependency_score + test_score) / 5
        
        return {
            'file': str(agent_file),
            'agent_class': agent_class.__name__,
            'status': 'complete' if overall_score >= 0.8 else 'incomplete',
            'overall_score': overall_score,
            'missing_attributes': missing_attributes,
            'missing_methods': missing_methods,
            'documentation': doc_check,
            'resources': resource_check,
            'dependencies': dependency_check,
            'test_coverage': test_check
        }
        
    except Exception as e:
        return {
            'file': str(agent_file),
            'status': 'error',
            'message': str(e)
        }

def main():
    """Main function to perform comprehensive agent audit."""
    print("🔍 Comprehensive Agent Audit")
    print("=" * 60)
    
    agent_files = get_all_agent_files()
    results = []
    
    for agent_file in agent_files:
        result = comprehensive_agent_audit(agent_file)
        results.append(result)
        
        if result['status'] == 'complete':
            print(f"✅ {result['agent_class']} is complete (Score: {result['overall_score']:.2f})")
        elif result['status'] == 'incomplete':
            print(f"❌ {result['agent_class']} is incomplete (Score: {result['overall_score']:.2f})")
        else:
            print(f"⚠️  Error auditing {agent_file.name}: {result['message']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE AUDIT SUMMARY")
    print("=" * 60)
    
    complete_count = sum(1 for r in results if r['status'] == 'complete')
    incomplete_count = sum(1 for r in results if r['status'] == 'incomplete')
    error_count = sum(1 for r in results if r['status'] == 'error')
    
    print(f"✅ Complete agents: {complete_count}")
    print(f"❌ Incomplete agents: {incomplete_count}")
    print(f"⚠️  Errors: {error_count}")
    print(f"📈 Total agents: {len(results)}")
    
    # Calculate average scores
    valid_results = [r for r in results if r['status'] != 'error']
    if valid_results:
        avg_score = sum(r['overall_score'] for r in valid_results) / len(valid_results)
        print(f"📊 Average completeness score: {avg_score:.2f}")
    
    # Show incomplete agents with details
    if incomplete_count > 0:
        print(f"\n🔧 INCOMPLETE AGENTS DETAILS:")
        for result in results:
            if result['status'] == 'incomplete':
                print(f"\n📁 {result['file']}")
                print(f"   Class: {result['agent_class']}")
                print(f"   Overall Score: {result['overall_score']:.2f}")
                
                if result['missing_attributes']:
                    print(f"   Missing attributes: {result['missing_attributes']}")
                if result['missing_methods']:
                    print(f"   Missing methods: {result['missing_methods']}")
                
                if result['documentation']['status'] == 'complete':
                    print(f"   Documentation: {result['documentation']['method_docstring_coverage']:.1%} coverage")
                else:
                    print(f"   Documentation: {result['documentation']['message']}")
                
                print(f"   Resources: {result['resources']['resource_completeness']:.1%} complete")
                print(f"   Dependencies: {result['dependencies']['import_completeness']:.1%} complete")
                print(f"   Test Coverage: {result['test_coverage']['test_coverage']}")
    
    return results

if __name__ == "__main__":
    main() 