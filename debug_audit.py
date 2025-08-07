#!/usr/bin/env python3
"""
Debug script to get detailed audit information for ProductOwnerAgent
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional
import ast

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

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
            'methods_with_docstrings': method_docstrings
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def check_resource_availability(agent_file: Path) -> Dict[str, Any]:
    """Check if agent has all required resources."""
    agent_name = agent_file.parent.name
    resource_base = project_root / "bmad" / "resources"
    
    # Expected template paths
    template_paths = [
        resource_base / "templates" / agent_name.lower() / "best-practices.md",
        resource_base / "templates" / agent_name.lower() / "user-story-template.md",
        resource_base / "templates" / agent_name.lower() / "vision-template.md",
        resource_base / "templates" / agent_name.lower() / "backlog-template.md",
        resource_base / "templates" / agent_name.lower() / "roadmap-template.md",
        resource_base / "templates" / agent_name.lower() / "acceptance-criteria.md",
        resource_base / "templates" / agent_name.lower() / "stakeholder-analysis.md"
    ]
    
    # Expected data paths
    data_paths = [
        resource_base / "data" / agent_name.lower() / "story-history.md",
        resource_base / "data" / agent_name.lower() / "vision-history.md",
        resource_base / "data" / agent_name.lower() / "backlog.md"
    ]
    
    # Check templates
    existing_templates = sum(1 for path in template_paths if path.exists())
    template_completeness = existing_templates / len(template_paths) if template_paths else 0
    
    # Check data files
    existing_data = sum(1 for path in data_paths if path.exists())
    data_completeness = existing_data / len(data_paths) if data_paths else 0
    
    # Overall resource completeness
    resource_completeness = (template_completeness + data_completeness) / 2
    
    return {
        'template_completeness': template_completeness,
        'data_completeness': data_completeness,
        'resource_completeness': resource_completeness,
        'existing_templates': existing_templates,
        'total_templates': len(template_paths),
        'existing_data': existing_data,
        'total_data': len(data_paths)
    }

def check_dependencies(agent_file: Path) -> Dict[str, Any]:
    """Check if agent has all required dependencies."""
    try:
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file
        tree = ast.parse(content)
        
        # Find imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        # Required imports for ProductOwner
        required_imports = [
            'bmad.core.message_bus',
            'bmad.core.mcp',
            'bmad.core.mcp.enhanced_mcp_integration',
            'integrations.opentelemetry.opentelemetry_tracing'
        ]
        
        existing_imports = sum(1 for imp in required_imports if any(imp in imp_name for imp_name in imports))
        import_completeness = existing_imports / len(required_imports) if required_imports else 0
        
        return {
            'import_completeness': import_completeness,
            'existing_imports': existing_imports,
            'total_required_imports': len(required_imports),
            'found_imports': imports
        }
        
    except Exception as e:
        return {
            'import_completeness': 0,
            'error': str(e)
        }

def check_test_coverage(agent_file: Path) -> Dict[str, Any]:
    """Check if agent has test coverage."""
    agent_name = agent_file.stem
    test_dir = project_root / "tests" / "unit" / "agents"
    
    # Look for test files
    test_files = list(test_dir.glob(f"test_{agent_name}*.py"))
    integration_test_files = list(test_dir.glob(f"test_{agent_name}_integration.py"))
    
    has_unit_tests = len(test_files) > 0
    has_integration_tests = len(integration_test_files) > 0
    
    if has_unit_tests and has_integration_tests:
        test_coverage = 'complete'
    elif has_unit_tests or has_integration_tests:
        test_coverage = 'partial'
    else:
        test_coverage = 'none'
    
    return {
        'test_coverage': test_coverage,
        'has_unit_tests': has_unit_tests,
        'has_integration_tests': has_integration_tests,
        'test_files': [str(f) for f in test_files],
        'integration_test_files': [str(f) for f in integration_test_files]
    }

def main():
    """Main function to audit ProductOwnerAgent in detail."""
    agent_file = project_root / "bmad" / "agents" / "Agent" / "ProductOwner" / "product_owner.py"
    
    print("🔍 Detailed ProductOwnerAgent Audit")
    print("=" * 60)
    
    try:
        # Import the agent module
        module_name = f"bmad.agents.Agent.ProductOwner.product_owner"
        module = importlib.import_module(module_name)
        
        # Find the agent class
        agent_class = None
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and 'Agent' in name and name != 'AgentMessageBusIntegration':
                agent_class = obj
                break
        
        if not agent_class:
            print("❌ No agent class found")
            return
        
        print(f"📁 Agent Class: {agent_class.__name__}")
        
        # Check attributes
        missing_attributes = []
        for attr in get_required_attributes():
            if not hasattr(agent_class, attr):
                missing_attributes.append(attr)
        
        print(f"\n🔧 Attributes:")
        print(f"   Missing: {missing_attributes}")
        print(f"   Implementation Score: {1.0 if not missing_attributes else 0.5}")
        
        # Check methods
        missing_methods = []
        for method in get_required_methods():
            if not hasattr(agent_class, method):
                missing_methods.append(method)
        
        print(f"\n🔧 Methods:")
        print(f"   Missing: {missing_methods}")
        
        # Check documentation
        doc_check = check_documentation_completeness(agent_file)
        print(f"\n📚 Documentation:")
        print(f"   Method Docstring Coverage: {doc_check.get('method_docstring_coverage', 0):.3f}")
        print(f"   Total Methods: {doc_check.get('total_methods', 0)}")
        print(f"   Methods with Docstrings: {doc_check.get('methods_with_docstrings', 0)}")
        
        # Check resources
        resource_check = check_resource_availability(agent_file)
        print(f"\n📁 Resources:")
        print(f"   Template Completeness: {resource_check['template_completeness']:.3f}")
        print(f"   Data Completeness: {resource_check['data_completeness']:.3f}")
        print(f"   Resource Completeness: {resource_check['resource_completeness']:.3f}")
        print(f"   Templates: {resource_check['existing_templates']}/{resource_check['total_templates']}")
        print(f"   Data Files: {resource_check['existing_data']}/{resource_check['total_data']}")
        
        # Check dependencies
        dependency_check = check_dependencies(agent_file)
        print(f"\n📦 Dependencies:")
        print(f"   Import Completeness: {dependency_check['import_completeness']:.3f}")
        print(f"   Found Imports: {dependency_check['existing_imports']}/{dependency_check['total_required_imports']}")
        
        # Check test coverage
        test_check = check_test_coverage(agent_file)
        print(f"\n🧪 Test Coverage:")
        print(f"   Test Coverage: {test_check['test_coverage']}")
        print(f"   Has Unit Tests: {test_check['has_unit_tests']}")
        print(f"   Has Integration Tests: {test_check['has_integration_tests']}")
        
        # Calculate overall completeness
        implementation_score = 1.0 if not missing_attributes and not missing_methods else 0.5
        documentation_score = doc_check.get('method_docstring_coverage', 0) if doc_check['status'] == 'complete' else 0
        resource_score = resource_check['resource_completeness']
        dependency_score = dependency_check['import_completeness']
        test_score = 1.0 if test_check['test_coverage'] == 'complete' else 0.5 if test_check['test_coverage'] == 'partial' else 0.0
        
        overall_score = (implementation_score + documentation_score + resource_score + dependency_score + test_score) / 5
        
        print(f"\n📊 Overall Scores:")
        print(f"   Implementation Score: {implementation_score:.3f}")
        print(f"   Documentation Score: {documentation_score:.3f}")
        print(f"   Resource Score: {resource_score:.3f}")
        print(f"   Dependency Score: {dependency_score:.3f}")
        print(f"   Test Score: {test_score:.3f}")
        print(f"   Overall Score: {overall_score:.3f}")
        
        print(f"\n🎯 To reach 1.0, we need to improve:")
        if implementation_score < 1.0:
            print(f"   - Implementation: Add missing attributes/methods")
        if documentation_score < 1.0:
            print(f"   - Documentation: Add docstrings to {doc_check.get('total_methods', 0) - doc_check.get('methods_with_docstrings', 0)} methods")
        if resource_score < 1.0:
            print(f"   - Resources: Add missing templates/data files")
        if dependency_score < 1.0:
            print(f"   - Dependencies: Add missing imports")
        if test_score < 1.0:
            print(f"   - Tests: Ensure complete test coverage")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 