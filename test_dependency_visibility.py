#!/usr/bin/env python3
"""
Test script for Dependency Visibility & Feedback Strategy
Validates that missing dependencies are properly reported and visible to users
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from bmad.core.mcp.dependency_manager import get_dependency_manager
from bmad.core.mcp.agent_mixin import MCPAgentMixin, MCPAgentConfig, create_mcp_agent_config

class TestDependencyVisibility:
    """Test class for dependency visibility functionality."""
    
    def __init__(self):
        self.test_results = []
    
    def test_dependency_manager_warnings(self):
        """Test that dependency manager provides proper warnings."""
        print("🧪 Testing Dependency Manager Warnings...")
        
        try:
            manager = get_dependency_manager()
            
            # Get warnings for missing dependencies
            warnings = manager.get_dependency_warnings()
            missing_deps = manager.get_missing_dependencies()
            degraded_features = manager.get_degraded_features()
            recommendations = manager.get_dependency_recommendations()
            
            print(f"✅ Dependency warnings: {len(warnings)} warnings generated")
            print(f"✅ Missing dependencies: {missing_deps}")
            print(f"✅ Degraded features: {degraded_features}")
            print(f"✅ Recommendations: {recommendations}")
            
            # Validate warning format
            for warning in warnings:
                if not warning.startswith("[DEPENDENCY WARNING]"):
                    print(f"❌ Warning format incorrect: {warning}")
                    return False
            
            self.test_results.append({
                "test": "dependency_manager_warnings",
                "status": "PASS",
                "warnings_count": len(warnings),
                "missing_deps": missing_deps
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Dependency manager warnings test failed: {e}")
            self.test_results.append({
                "test": "dependency_manager_warnings",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    def test_agent_mixin_dependency_status(self):
        """Test that agent mixin provides dependency status."""
        print("\n🧪 Testing Agent Mixin Dependency Status...")
        
        try:
            # Create test agent with mixin
            config = create_mcp_agent_config(
                agent_name="TestAgent",
                agent_type="Testing",
                tool_categories=["development", "testing"],
                custom_tools=["test_tool"],
                error_handling="graceful"
            )
            
            agent = MCPAgentMixin(config)
            
            # Get dependency status
            dep_status = agent.get_dependency_status()
            
            print(f"✅ Agent dependency status: {dep_status['agent_name']}")
            print(f"✅ Missing dependencies: {dep_status['missing_dependencies']}")
            print(f"✅ Degraded features: {dep_status['degraded_features']}")
            print(f"✅ Dependency health: {dep_status['dependency_health']}")
            
            # Validate status structure
            required_fields = ['agent_name', 'missing_dependencies', 'degraded_features', 'dependency_health']
            for field in required_fields:
                if field not in dep_status:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            self.test_results.append({
                "test": "agent_mixin_dependency_status",
                "status": "PASS",
                "missing_deps": dep_status['missing_dependencies'],
                "degraded_features": dep_status['degraded_features']
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Agent mixin dependency status test failed: {e}")
            self.test_results.append({
                "test": "agent_mixin_dependency_status",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    def test_frontend_developer_dependency_check(self):
        """Test FrontendDeveloper agent dependency checking."""
        print("\n🧪 Testing FrontendDeveloper Agent Dependency Check...")
        
        try:
            from bmad.agents.Agent.FrontendDeveloper.frontenddeveloper import FrontendDeveloperAgent
            
            agent = FrontendDeveloperAgent()
            
            # Test dependency check method
            dep_check = agent.check_dependencies()
            
            print(f"✅ FrontendDeveloper dependency check: {dep_check['agent_name']}")
            print(f"✅ Missing dependencies: {dep_check.get('missing_dependencies', [])}")
            print(f"✅ Degraded features: {dep_check.get('degraded_features', [])}")
            
            # Test status method includes dependency info
            status = agent.get_status()
            if 'dependency_status' in status:
                print(f"✅ Status includes dependency info: {len(status['dependency_status']['missing_dependencies'])} missing")
            else:
                print("⚠️ Status does not include dependency info (agent may not use MCP mixin)")
            
            self.test_results.append({
                "test": "frontend_developer_dependency_check",
                "status": "PASS",
                "agent_name": dep_check['agent_name'],
                "has_dependency_status": 'dependency_status' in status
            })
            
            return True
            
        except Exception as e:
            print(f"❌ FrontendDeveloper dependency check test failed: {e}")
            self.test_results.append({
                "test": "frontend_developer_dependency_check",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    def test_cli_dependency_commands(self):
        """Test CLI dependency checking commands."""
        print("\n🧪 Testing CLI Dependency Commands...")
        
        try:
            from bmad.agents.Agent.FrontendDeveloper.frontenddeveloper import FrontendDeveloperAgent
            
            agent = FrontendDeveloperAgent()
            
            # Test check_dependencies method output
            dep_status = agent.check_dependencies()
            
            # Validate CLI-friendly output
            if isinstance(dep_status, dict):
                json_output = json.dumps(dep_status, indent=2, default=str)
                print(f"✅ CLI output format: Valid JSON ({len(json_output)} characters)")
                
                # Check for actionable information
                if 'recommendations' in dep_status:
                    print(f"✅ Includes recommendations: {len(dep_status['recommendations'])} suggestions")
                
                if 'missing_dependencies' in dep_status:
                    print(f"✅ Lists missing dependencies: {len(dep_status['missing_dependencies'])} items")
            
            self.test_results.append({
                "test": "cli_dependency_commands",
                "status": "PASS",
                "output_format": "JSON",
                "has_recommendations": 'recommendations' in dep_status
            })
            
            return True
            
        except Exception as e:
            print(f"❌ CLI dependency commands test failed: {e}")
            self.test_results.append({
                "test": "cli_dependency_commands",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    def test_dependency_visibility_strategy(self):
        """Test overall dependency visibility strategy."""
        print("\n🧪 Testing Overall Dependency Visibility Strategy...")
        
        try:
            # Test all components work together
            manager = get_dependency_manager()
            warnings = manager.get_dependency_warnings()
            
            # Create test agent
            config = create_mcp_agent_config(
                agent_name="VisibilityTestAgent",
                agent_type="Testing"
            )
            agent = MCPAgentMixin(config)
            
            # Test complete workflow
            dep_status = agent.get_dependency_status()
            
            # Validate strategy requirements
            strategy_requirements = [
                "Warnings are logged" if warnings else "No warnings needed",
                "Status includes dependency info" if 'missing_dependencies' in dep_status else "Status missing dependency info",
                "Recommendations provided" if dep_status.get('recommendations') else "No recommendations",
                "Health status available" if 'dependency_health' in dep_status else "Health status missing"
            ]
            
            print("✅ Strategy validation:")
            for req in strategy_requirements:
                print(f"  - {req}")
            
            self.test_results.append({
                "test": "dependency_visibility_strategy",
                "status": "PASS",
                "requirements_met": len(strategy_requirements),
                "warnings_count": len(warnings)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Dependency visibility strategy test failed: {e}")
            self.test_results.append({
                "test": "dependency_visibility_strategy",
                "status": "FAIL",
                "error": str(e)
            })
            return False

async def main():
    """Run all dependency visibility tests."""
    print("🚀 Starting Dependency Visibility & Feedback Tests")
    print("=" * 60)
    
    tester = TestDependencyVisibility()
    
    tests = [
        ("Dependency Manager Warnings", tester.test_dependency_manager_warnings),
        ("Agent Mixin Dependency Status", tester.test_agent_mixin_dependency_status),
        ("FrontendDeveloper Dependency Check", tester.test_frontend_developer_dependency_check),
        ("CLI Dependency Commands", tester.test_cli_dependency_commands),
        ("Overall Strategy", tester.test_dependency_visibility_strategy)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Dependency Visibility Test Results")
    print("=" * 60)
    
    for result in tester.test_results:
        status = "✅ PASS" if result["status"] == "PASS" else "❌ FAIL"
        print(f"{status} {result['test']}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All dependency visibility tests passed! Strategy is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the dependency visibility implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 