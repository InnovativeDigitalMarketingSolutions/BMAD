"""
Pytest configuration for E2E tests.
This file sets up the correct Python path and test environment for end-to-end testing.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Ensure the tests directory is in the path
tests_dir = Path(__file__).parent.parent
sys.path.insert(0, str(tests_dir))

@pytest.fixture(scope="session")
def e2e_environment():
    """Set up E2E test environment."""
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["E2E_TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["REDIS_URL"] = "redis://localhost:6379/2"
    os.environ["JWT_SECRET"] = "e2e-test-secret-key"
    
    return {
        "database_url": os.environ["DATABASE_URL"],
        "redis_url": os.environ["REDIS_URL"],
        "jwt_secret": os.environ["JWT_SECRET"]
    }

@pytest.fixture(scope="function")
def clean_environment():
    """Clean environment for each test."""
    # Store original environment
    original_env = os.environ.copy()
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env) 