#!/usr/bin/env python3
"""
Script to run only the working tests that we know pass.
This helps us focus on the core functionality while we fix the import errors.
"""

import subprocess
import sys
import os

def run_working_tests():
    """Run only the tests that we know work."""
    
    # List of working test files
    working_tests = [
        "tests/unit/core/test_tool_registry_comprehensive.py",
        "tests/unit/core/test_mcp_phase2.py", 
        "tests/unit/core/test_mcp_quality_solutions.py"
    ]
    
    # Build command
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--disable-warnings"
    ] + working_tests
    
    print("🧪 Running Working Tests Only")
    print("=" * 50)
    print(f"Command: {' '.join(cmd)}")
    print("=" * 50)
    
    # Run tests
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All working tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Some tests failed: {e}")
        return False

def run_coverage_on_working_tests():
    """Run coverage on working tests."""
    
    working_tests = [
        "tests/unit/core/test_tool_registry_comprehensive.py",
        "tests/unit/core/test_mcp_phase2.py", 
        "tests/unit/core/test_mcp_quality_solutions.py"
    ]
    
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=bmad.core.mcp",
        "--cov-report=term-missing",
        "-v"
    ] + working_tests
    
    print("\n📊 Running Coverage on Working Tests")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Coverage run failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BMAD Working Tests Runner")
    print("=" * 50)
    
    # Run working tests
    success = run_working_tests()
    
    if success:
        # Run coverage
        run_coverage_on_working_tests()
        
        print("\n🎉 Working test suite completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Continue with mcp_client.py coverage improvement")
        print("2. Systematically fix import errors in other test files")
        print("3. Gradually add more working tests to this suite")
    else:
        print("\n❌ Working test suite failed!")
        sys.exit(1) 