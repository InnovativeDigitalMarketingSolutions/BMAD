"""
Pytest configuration for microservices tests.
This file sets up the correct Python path and test environment.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the microservice src directory to Python path
microservice_root = Path(__file__).parent.parent
src_path = microservice_root / "src"
sys.path.insert(0, str(src_path))

# Add the main project root for shared dependencies
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Ensure the tests directory is in the path for shared test utilities
tests_dir = project_root / "tests"
if tests_dir.exists():
    sys.path.insert(0, str(tests_dir))
    
    # Import shared test utilities if available
    try:
        from tests.fixtures.mocks import mock_redis_client, mock_database_connection
    except ImportError:
        # Create fallback mocks if shared fixtures are not available
        pass

@pytest.fixture(scope="session")
def microservice_environment():
    """Set up microservice test environment."""
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["JWT_SECRET"] = "test-secret-key"
    os.environ["ENCRYPTION_KEY"] = "test-encryption-key-32-chars-long"
    
    return {
        "database_url": os.environ["DATABASE_URL"],
        "jwt_secret": os.environ["JWT_SECRET"],
        "encryption_key": os.environ["ENCRYPTION_KEY"]
    } 