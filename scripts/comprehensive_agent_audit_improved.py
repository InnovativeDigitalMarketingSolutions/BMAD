#!/usr/bin/env python3
"""
Improved Comprehensive Agent Audit Script

This script performs a comprehensive audit of all BMAD agents with improved scoring:
1. Resource Scoring: More granular assessment (count and quality)
2. Test Scoring: Includes test success rate and coverage
3. Weighted Scoring: Different weights for different categories
4. Quality Assessment: Beyond just quantity
"""

import ast
import importlib
import inspect
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_all_agent_files() -> List[Path]:
    """Get all agent Python files."""
    agent_dir = project_root / "bmad" / "agents" / "Agent"
    agent_files = []
    
    for agent_folder in agent_dir.iterdir():
        if agent_folder.is_dir():
            for file in agent_folder.glob("*.py"):
                if file.name.endswith(".py") and not file.name.startswith("__"):
                    agent_files.append(file)
    
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
    """Check if agent has complete documentation with quality assessment."""
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
        
        # Check for method docstrings with quality assessment
        method_docstrings = 0
        total_methods = 0
        quality_methods = 0
        
        for node in ast.walk(agent_class):
            if isinstance(node, ast.FunctionDef):
                total_methods += 1
                docstring = ast.get_docstring(node)
                if docstring is not None:
                    method_docstrings += 1
                    # Quality assessment: check if docstring has meaningful content
                    if len(docstring.strip()) > 20:  # More than just a brief description
                        quality_methods += 1
        
        docstring_coverage = method_docstrings / total_methods if total_methods > 0 else 0
        quality_coverage = quality_methods / total_methods if total_methods > 0 else 0
        
        # Combined documentation score (coverage + quality)
        documentation_score = (docstring_coverage + quality_coverage) / 2
        
        return {
            'status': 'complete',
            'has_class_docstring': has_docstring,
            'method_docstring_coverage': docstring_coverage,
            'quality_coverage': quality_coverage,
            'documentation_score': documentation_score,
            'total_methods': total_methods,
            'documented_methods': method_docstrings,
            'quality_methods': quality_methods
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def check_resource_availability_improved(agent_file: Path) -> Dict[str, Any]:
    """Improved resource availability check with granularity and quality assessment."""
    agent_name = agent_file.parent.name
    resource_dir = project_root / "bmad" / "resources"
    
    # Check for YAML configuration
    yaml_file = agent_file.parent / f"{agent_name.lower()}.yaml"
    has_yaml = yaml_file.exists()
    
    # Check for markdown documentation
    md_file = agent_file.parent / f"{agent_name.lower()}.md"
    has_md = md_file.exists()
    
    # Enhanced template checking with count and quality
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
    has_templates = template_dir.exists()
    
    # Count templates and assess quality
    template_count = 0
    template_quality_score = 0
    if has_templates:
        template_files = list(template_dir.glob("*.md"))
        template_count = len(template_files)
        
        # Quality assessment: check if templates have meaningful content
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content.strip()) > 100:  # More than just a header
                        template_quality_score += 1
            except:
                pass
        
        template_quality_score = template_quality_score / template_count if template_count > 0 else 0
    
    # Enhanced data file checking
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
    
    # Count data files and assess quality
    data_count = 0
    data_quality_score = 0
    if has_data:
        data_files = list(data_dir.glob("*.md"))
        data_count = len(data_files)
        
        # Quality assessment: check if data files have meaningful content
        for data_file in data_files:
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content.strip()) > 50:  # More than just a brief note
                        data_quality_score += 1
            except:
                pass
        
        data_quality_score = data_quality_score / data_count if data_count > 0 else 0
    
    # Calculate improved resource completeness
    # Base existence score (25% each)
    existence_score = sum([has_yaml, has_md, has_templates, has_data]) / 4
    
    # Quality score (based on template and data quality)
    quality_score = (template_quality_score + data_quality_score) / 2 if has_templates or has_data else 0
    
    # Quantity score (based on number of files)
    expected_templates = 7  # Based on ProductOwner example
    expected_data_files = 3  # Based on ProductOwner example
    template_quantity_score = min(template_count / expected_templates, 1.0) if has_templates else 0
    data_quantity_score = min(data_count / expected_data_files, 1.0) if has_data else 0
    quantity_score = (template_quantity_score + data_quantity_score) / 2
    
    # Combined resource score (existence + quality + quantity)
    resource_completeness = (existence_score + quality_score + quantity_score) / 3
    
    return {
        'has_yaml_config': has_yaml,
        'has_markdown_docs': has_md,
        'has_templates': has_templates,
        'has_data_files': has_data,
        'template_count': template_count,
        'data_count': data_count,
        'template_quality_score': template_quality_score,
        'data_quality_score': data_quality_score,
        'existence_score': existence_score,
        'quality_score': quality_score,
        'quantity_score': quantity_score,
        'resource_completeness': resource_completeness
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

def run_tests_for_agent(agent_name: str) -> Dict[str, Any]:
    """Run tests for a specific agent and return results."""
    try:
        # Run unit tests
        unit_test_patterns = [
            f"test_{agent_name.lower()}.py",
            f"test_{agent_name.lower()}_agent.py",
            f"test_{agent_name.lower().replace('developer', '')}_agent.py",
            f"test_fullstack_developer_agent.py"  # Special case for FullstackDeveloper
        ]
        
        unit_test_file = None
        for pattern in unit_test_patterns:
            test_file = project_root / "tests" / "unit" / "agents" / pattern
            if test_file.exists():
                unit_test_file = test_file
                break
        
        unit_test_results = {'success': False, 'total': 0, 'passed': 0, 'failed': 0}
        if unit_test_file:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(unit_test_file), "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=60
                )
                
                # Parse pytest output
                output_lines = result.stdout.split('\n')
                total_tests = 0
                passed_tests = 0
                failed_tests = 0
                
                for line in output_lines:
                    if "::test_" in line and "PASSED" in line:
                        passed_tests += 1
                        total_tests += 1
                    elif "::test_" in line and "FAILED" in line:
                        failed_tests += 1
                        total_tests += 1
                    elif "::test_" in line and "ERROR" in line:
                        failed_tests += 1
                        total_tests += 1
                
                unit_test_results = {
                    'success': result.returncode == 0,
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': passed_tests / total_tests if total_tests > 0 else 0
                }
            except subprocess.TimeoutExpired:
                unit_test_results = {'success': False, 'timeout': True}
            except Exception as e:
                unit_test_results = {'success': False, 'error': str(e)}
        
        # Run integration tests
        integration_test_file = project_root / "tests" / "integration" / f"test_{agent_name.lower()}_integration.py"
        integration_test_results = {'success': False, 'total': 0, 'passed': 0, 'failed': 0}
        
        if integration_test_file.exists():
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(integration_test_file), "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=60
                )
                
                # Parse pytest output
                output_lines = result.stdout.split('\n')
                total_tests = 0
                passed_tests = 0
                failed_tests = 0
                
                for line in output_lines:
                    if "::test_" in line and "PASSED" in line:
                        passed_tests += 1
                        total_tests += 1
                    elif "::test_" in line and "FAILED" in line:
                        failed_tests += 1
                        total_tests += 1
                    elif "::test_" in line and "ERROR" in line:
                        failed_tests += 1
                        total_tests += 1
                
                integration_test_results = {
                    'success': result.returncode == 0,
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': passed_tests / total_tests if total_tests > 0 else 0
                }
            except subprocess.TimeoutExpired:
                integration_test_results = {'success': False, 'timeout': True}
            except Exception as e:
                integration_test_results = {'success': False, 'error': str(e)}
        
        return {
            'unit_tests': unit_test_results,
            'integration_tests': integration_test_results
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'unit_tests': {'success': False, 'error': str(e)},
            'integration_tests': {'success': False, 'error': str(e)}
        }

def check_test_coverage_improved(agent_file: Path) -> Dict[str, Any]:
    """Improved test coverage check with success rate and quality assessment.
    
    Requirements:
    - Tests must exist (unit + integration)
    - Tests must have 100% success rate for perfect score
    - Tests must have sufficient quantity
    """
    agent_name = agent_file.parent.name
    
    # Check for unit tests with multiple possible naming patterns
    unit_test_patterns = [
        f"test_{agent_name.lower()}.py",
        f"test_{agent_name.lower()}_agent.py",
        f"test_{agent_name.lower().replace('developer', '')}_agent.py",
        f"test_fullstack_developer_agent.py"  # Special case for FullstackDeveloper
    ]
    
    has_unit_tests = False
    unit_test_file = None
    for pattern in unit_test_patterns:
        test_file = project_root / "tests" / "unit" / "agents" / pattern
        if test_file.exists():
            has_unit_tests = True
            unit_test_file = test_file
            break
    
    # Check for integration tests
    integration_test_file = project_root / "tests" / "integration" / f"test_{agent_name.lower()}_integration.py"
    has_integration_tests = integration_test_file.exists()
    
    # Run tests to get success rate
    test_results = run_tests_for_agent(agent_name)
    
    # Calculate improved test score
    # Base existence score
    existence_score = 1.0 if has_unit_tests and has_integration_tests else 0.5 if has_unit_tests or has_integration_tests else 0.0
    
    # Success rate score
    unit_success_rate = test_results['unit_tests'].get('success_rate', 0)
    integration_success_rate = test_results['integration_tests'].get('success_rate', 0)
    success_rate_score = (unit_success_rate + integration_success_rate) / 2 if (has_unit_tests or has_integration_tests) else 0
    
    # Quantity score (based on number of tests)
    unit_test_count = test_results['unit_tests'].get('total', 0)
    integration_test_count = test_results['integration_tests'].get('total', 0)
    total_test_count = unit_test_count + integration_test_count
    
    expected_tests = 50  # Baseline expectation
    quantity_score = min(total_test_count / expected_tests, 1.0)
    
    # Combined test score (existence + success rate + quantity)
    # Success rate must be 100% for perfect score
    if success_rate_score < 1.0:
        # Penalize for less than 100% success rate
        test_score = (existence_score + success_rate_score * 0.5 + quantity_score) / 3
    else:
        # Perfect score only if 100% success rate
        test_score = (existence_score + success_rate_score + quantity_score) / 3
    
    # Validate test success rate requirements
    meets_success_rate_requirement = success_rate_score >= 1.0
    test_quality_status = 'perfect' if meets_success_rate_requirement else 'needs_improvement'
    
    return {
        'has_unit_tests': has_unit_tests,
        'has_integration_tests': has_integration_tests,
        'unit_test_count': unit_test_count,
        'integration_test_count': integration_test_count,
        'total_test_count': total_test_count,
        'unit_success_rate': unit_success_rate,
        'integration_success_rate': integration_success_rate,
        'overall_success_rate': success_rate_score,
        'meets_success_rate_requirement': meets_success_rate_requirement,
        'test_quality_status': test_quality_status,
        'existence_score': existence_score,
        'success_rate_score': success_rate_score,
        'quantity_score': quantity_score,
        'test_score': test_score,
        'test_results': test_results
    }

def calculate_weighted_score(scores: Dict[str, float]) -> float:
    """Calculate weighted overall score."""
    weights = {
        'implementation': 0.3,    # Most important
        'documentation': 0.2,     # Important
        'resources': 0.15,        # Medium
        'dependencies': 0.15,     # Medium
        'tests': 0.2             # Important
    }
    
    weighted_sum = sum(scores[category] * weights[category] for category in weights)
    return weighted_sum

def comprehensive_agent_audit_improved(agent_file: Path) -> Dict[str, Any]:
    """Perform improved comprehensive audit of an agent."""
    print(f"\n🔍 Auditing {agent_file.name} with improved scoring...")
    
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
        
        # Check documentation with improved scoring
        doc_check = check_documentation_completeness(agent_file)
        
        # Check resources with improved scoring
        resource_check = check_resource_availability_improved(agent_file)
        
        # Check dependencies
        dependency_check = check_dependencies(agent_file)
        
        # Check test coverage with improved scoring
        test_check = check_test_coverage_improved(agent_file)
        
        # Calculate scores
        implementation_score = 1.0 if not missing_attributes and not missing_methods else 0.5
        documentation_score = doc_check.get('documentation_score', 0) if doc_check['status'] == 'complete' else 0
        resource_score = resource_check['resource_completeness']
        dependency_score = dependency_check['import_completeness']
        test_score = test_check['test_score']
        
        # Calculate both unweighted and weighted scores
        unweighted_score = (implementation_score + documentation_score + resource_score + dependency_score + test_score) / 5
        weighted_score = calculate_weighted_score({
            'implementation': implementation_score,
            'documentation': documentation_score,
            'resources': resource_score,
            'dependencies': dependency_score,
            'tests': test_score
        })
        
        return {
            'file': str(agent_file),
            'agent_class': agent_class.__name__,
            'status': 'complete' if weighted_score >= 0.8 else 'incomplete',
            'unweighted_score': unweighted_score,
            'weighted_score': weighted_score,
            'missing_attributes': missing_attributes,
            'missing_methods': missing_methods,
            'documentation': doc_check,
            'resources': resource_check,
            'dependencies': dependency_check,
            'test_coverage': test_check,
            'detailed_scores': {
                'implementation': implementation_score,
                'documentation': documentation_score,
                'resources': resource_score,
                'dependencies': dependency_score,
                'tests': test_score
            }
        }
        
    except Exception as e:
        return {
            'file': str(agent_file),
            'status': 'error',
            'message': str(e)
        }

def main():
    """Main function to perform improved comprehensive agent audit."""
    print("🔍 Improved Comprehensive Agent Audit")
    print("=" * 60)
    print("Features:")
    print("- Resource scoring with count and quality assessment")
    print("- Test scoring with success rate and coverage (100% success rate required for perfect score)")
    print("- Weighted scoring (implementation: 30%, docs: 20%, tests: 20%, resources: 15%, deps: 15%)")
    print("- Quality assessment beyond just quantity")
    print("=" * 60)
    
    agent_files = get_all_agent_files()
    results = []
    
    for agent_file in agent_files:
        result = comprehensive_agent_audit_improved(agent_file)
        results.append(result)
        
        if result['status'] == 'complete':
            print(f"✅ {result['agent_class']} is complete")
            print(f"   Unweighted Score: {result['unweighted_score']:.3f}")
            print(f"   Weighted Score: {result['weighted_score']:.3f}")
        elif result['status'] == 'incomplete':
            print(f"❌ {result['agent_class']} is incomplete")
            print(f"   Unweighted Score: {result['unweighted_score']:.3f}")
            print(f"   Weighted Score: {result['weighted_score']:.3f}")
        else:
            print(f"⚠️  Error auditing {agent_file.name}: {result['message']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 IMPROVED COMPREHENSIVE AUDIT SUMMARY")
    print("=" * 60)
    
    complete_agents = [r for r in results if r['status'] == 'complete']
    incomplete_agents = [r for r in results if r['status'] == 'incomplete']
    error_agents = [r for r in results if r['status'] == 'error']
    
    print(f"✅ Complete Agents: {len(complete_agents)}")
    print(f"❌ Incomplete Agents: {len(incomplete_agents)}")
    print(f"⚠️  Error Agents: {len(error_agents)}")
    
    if complete_agents:
        print(f"\n🏆 Best Performing Agents:")
        sorted_complete = sorted(complete_agents, key=lambda x: x['weighted_score'], reverse=True)
        for agent in sorted_complete[:3]:
            print(f"   {agent['agent_class']}: {agent['weighted_score']:.3f}")
    
    if incomplete_agents:
        print(f"\n🔧 Agents Needing Improvement:")
        sorted_incomplete = sorted(incomplete_agents, key=lambda x: x['weighted_score'])
        for agent in sorted_incomplete[:3]:
            print(f"   {agent['agent_class']}: {agent['weighted_score']:.3f}")
    
    # Detailed analysis
    print(f"\n📈 Detailed Analysis:")
    for result in results:
        if result['status'] != 'error':
            print(f"\n{result['agent_class']}:")
            scores = result['detailed_scores']
            print(f"   Implementation: {scores['implementation']:.3f}")
            print(f"   Documentation: {scores['documentation']:.3f}")
            print(f"   Resources: {scores['resources']:.3f}")
            print(f"   Dependencies: {scores['dependencies']:.3f}")
            print(f"   Tests: {scores['tests']:.3f}")
            
            # Show test details if available
            if 'test_coverage' in result and 'test_results' in result['test_coverage']:
                test_results = result['test_coverage']['test_results']
                unit_tests = test_results.get('unit_tests', {})
                integration_tests = test_results.get('integration_tests', {})
                
                if unit_tests.get('total', 0) > 0:
                    success_rate = unit_tests.get('success_rate', 0)
                    status = "✅" if success_rate >= 1.0 else "⚠️"
                    print(f"   {status} Unit Tests: {unit_tests['passed']}/{unit_tests['total']} passed ({success_rate:.1%})")
                if integration_tests.get('total', 0) > 0:
                    success_rate = integration_tests.get('success_rate', 0)
                    status = "✅" if success_rate >= 1.0 else "⚠️"
                    print(f"   {status} Integration Tests: {integration_tests['passed']}/{integration_tests['total']} passed ({success_rate:.1%})")
                
                # Show overall test quality status
                test_coverage = result['test_coverage']
                if 'test_quality_status' in test_coverage:
                    quality_status = test_coverage['test_quality_status']
                    if quality_status == 'perfect':
                        print(f"   🎯 Test Quality: {quality_status.upper()} (100% success rate achieved)")
                    else:
                        print(f"   ⚠️  Test Quality: {quality_status.replace('_', ' ').title()} (100% success rate required)")

if __name__ == "__main__":
    main() 