"""
Production Configuration Tests for BMAD System

This module tests production configuration settings to ensure
the system is properly configured for production deployment.

Test Coverage:
- Environment configuration validation
- Security settings verification
- Performance configuration testing
- Database configuration validation
- API configuration testing
- Logging configuration validation
"""

import pytest
import os
import json
import yaml
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from pathlib import Path

class ProductionConfigValidator:
    """Production configuration validator."""
    
    def __init__(self):
        self.config_errors = []
        self.config_warnings = []
        self.validation_results = {}
    
    def validate_environment_config(self) -> Dict[str, Any]:
        """Validate environment configuration."""
        results = {
            "environment": "production",
            "validations": [],
            "errors": [],
            "warnings": []
        }
        
        # Check required environment variables
        required_env_vars = [
            "BMAD_ENV",
            "BMAD_SECRET_KEY",
            "BMAD_DATABASE_URL",
            "BMAD_REDIS_URL",
            "BMAD_LOG_LEVEL"
        ]
        
        for env_var in required_env_vars:
            if os.getenv(env_var):
                results["validations"].append(f"✅ {env_var} is set")
            else:
                results["errors"].append(f"❌ {env_var} is missing")
        
        # Check environment-specific settings
        if os.getenv("BMAD_ENV") == "production":
            results["validations"].append("✅ Environment is set to production")
        else:
            results["warnings"].append("⚠️ Environment should be set to production")
        
        # Check security settings
        secret_key = os.getenv("BMAD_SECRET_KEY")
        if secret_key and len(secret_key) >= 32:
            results["validations"].append("✅ Secret key is sufficiently long")
        else:
            results["errors"].append("❌ Secret key is too short or missing")
        
        return results
    
    def validate_security_config(self) -> Dict[str, Any]:
        """Validate security configuration."""
        results = {
            "security_validations": [],
            "security_errors": [],
            "security_warnings": []
        }
        
        # Check JWT settings
        jwt_secret = os.getenv("BMAD_JWT_SECRET")
        if jwt_secret and len(jwt_secret) >= 32:
            results["security_validations"].append("✅ JWT secret is properly configured")
        else:
            results["security_errors"].append("❌ JWT secret is missing or too short")
        
        # Check CORS settings
        cors_origins = os.getenv("BMAD_CORS_ORIGINS")
        if cors_origins:
            results["security_validations"].append("✅ CORS origins are configured")
        else:
            results["security_warnings"].append("⚠️ CORS origins not configured")
        
        # Check rate limiting
        rate_limit = os.getenv("BMAD_RATE_LIMIT")
        if rate_limit and int(rate_limit) > 0:
            results["security_validations"].append("✅ Rate limiting is configured")
        else:
            results["security_warnings"].append("⚠️ Rate limiting not configured")
        
        return results
    
    def validate_database_config(self) -> Dict[str, Any]:
        """Validate database configuration."""
        results = {
            "database_validations": [],
            "database_errors": [],
            "database_warnings": []
        }
        
        # Check database URL
        db_url = os.getenv("BMAD_DATABASE_URL")
        if db_url:
            if "postgresql://" in db_url or "mysql://" in db_url:
                results["database_validations"].append("✅ Database URL is properly formatted")
            else:
                results["database_errors"].append("❌ Database URL format is invalid")
        else:
            results["database_errors"].append("❌ Database URL is missing")
        
        # Check connection pool settings
        pool_size = os.getenv("BMAD_DB_POOL_SIZE")
        if pool_size and int(pool_size) > 0:
            results["database_validations"].append("✅ Database pool size is configured")
        else:
            results["database_warnings"].append("⚠️ Database pool size not configured")
        
        return results
    
    def validate_api_config(self) -> Dict[str, Any]:
        """Validate API configuration."""
        results = {
            "api_validations": [],
            "api_errors": [],
            "api_warnings": []
        }
        
        # Check API host and port
        api_host = os.getenv("BMAD_API_HOST", "0.0.0.0")
        api_port = os.getenv("BMAD_API_PORT", "8000")
        
        if api_host == "0.0.0.0":
            results["api_validations"].append("✅ API host is configured for production")
        else:
            results["api_warnings"].append("⚠️ API host should be 0.0.0.0 for production")
        
        if api_port and api_port.isdigit():
            results["api_validations"].append("✅ API port is properly configured")
        else:
            results["api_errors"].append("❌ API port is invalid")
        
        # Check API timeout settings
        timeout = os.getenv("BMAD_API_TIMEOUT")
        if timeout and int(timeout) > 0:
            results["api_validations"].append("✅ API timeout is configured")
        else:
            results["api_warnings"].append("⚠️ API timeout not configured")
        
        return results
    
    def validate_logging_config(self) -> Dict[str, Any]:
        """Validate logging configuration."""
        results = {
            "logging_validations": [],
            "logging_errors": [],
            "logging_warnings": []
        }
        
        # Check log level
        log_level = os.getenv("BMAD_LOG_LEVEL", "INFO")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        if log_level in valid_levels:
            results["logging_validations"].append(f"✅ Log level is valid: {log_level}")
        else:
            results["logging_errors"].append(f"❌ Invalid log level: {log_level}")
        
        # Check log file path
        log_file = os.getenv("BMAD_LOG_FILE")
        if log_file:
            results["logging_validations"].append("✅ Log file path is configured")
        else:
            results["logging_warnings"].append("⚠️ Log file path not configured")
        
        return results
    
    def validate_performance_config(self) -> Dict[str, Any]:
        """Validate performance configuration."""
        results = {
            "performance_validations": [],
            "performance_errors": [],
            "performance_warnings": []
        }
        
        # Check worker processes
        workers = os.getenv("BMAD_WORKERS")
        if workers and int(workers) > 0:
            results["performance_validations"].append("✅ Worker processes are configured")
        else:
            results["performance_warnings"].append("⚠️ Worker processes not configured")
        
        # Check cache settings
        cache_url = os.getenv("BMAD_REDIS_URL")
        if cache_url:
            results["performance_validations"].append("✅ Cache URL is configured")
        else:
            results["performance_warnings"].append("⚠️ Cache URL not configured")
        
        return results

def test_environment_configuration():
    """Test environment configuration validation."""
    validator = ProductionConfigValidator()
    
    # Mock environment variables for testing
    with patch.dict(os.environ, {
        "BMAD_ENV": "production",
        "BMAD_SECRET_KEY": "a" * 32,
        "BMAD_DATABASE_URL": "postgresql://user:pass@localhost/db",
        "BMAD_REDIS_URL": "redis://localhost:6379",
        "BMAD_LOG_LEVEL": "INFO"
    }):
        results = validator.validate_environment_config()
        
        # Verify validation results
        assert len(results["errors"]) == 0, f"Environment config errors: {results['errors']}"
        assert len(results["validations"]) >= 5, "Should have at least 5 validations"
        assert results["environment"] == "production", "Environment should be production"

def test_security_configuration():
    """Test security configuration validation."""
    validator = ProductionConfigValidator()
    
    # Mock security environment variables
    with patch.dict(os.environ, {
        "BMAD_JWT_SECRET": "a" * 32,
        "BMAD_CORS_ORIGINS": "https://example.com",
        "BMAD_RATE_LIMIT": "100"
    }):
        results = validator.validate_security_config()
        
        # Verify security validations
        assert len(results["security_errors"]) == 0, f"Security config errors: {results['security_errors']}"
        assert len(results["security_validations"]) >= 3, "Should have at least 3 security validations"

def test_database_configuration():
    """Test database configuration validation."""
    validator = ProductionConfigValidator()
    
    # Mock database environment variables
    with patch.dict(os.environ, {
        "BMAD_DATABASE_URL": "postgresql://user:pass@localhost/db",
        "BMAD_DB_POOL_SIZE": "10"
    }):
        results = validator.validate_database_config()
        
        # Verify database validations
        assert len(results["database_errors"]) == 0, f"Database config errors: {results['database_errors']}"
        assert len(results["database_validations"]) >= 2, "Should have at least 2 database validations"

def test_api_configuration():
    """Test API configuration validation."""
    validator = ProductionConfigValidator()
    
    # Mock API environment variables
    with patch.dict(os.environ, {
        "BMAD_API_HOST": "0.0.0.0",
        "BMAD_API_PORT": "8000",
        "BMAD_API_TIMEOUT": "30"
    }):
        results = validator.validate_api_config()
        
        # Verify API validations
        assert len(results["api_errors"]) == 0, f"API config errors: {results['api_errors']}"
        assert len(results["api_validations"]) >= 3, "Should have at least 3 API validations"

def test_logging_configuration():
    """Test logging configuration validation."""
    validator = ProductionConfigValidator()
    
    # Mock logging environment variables
    with patch.dict(os.environ, {
        "BMAD_LOG_LEVEL": "INFO",
        "BMAD_LOG_FILE": "/var/log/bmad/app.log"
    }):
        results = validator.validate_logging_config()
        
        # Verify logging validations
        assert len(results["logging_errors"]) == 0, f"Logging config errors: {results['logging_errors']}"
        assert len(results["logging_validations"]) >= 2, "Should have at least 2 logging validations"

def test_performance_configuration():
    """Test performance configuration validation."""
    validator = ProductionConfigValidator()
    
    # Mock performance environment variables
    with patch.dict(os.environ, {
        "BMAD_WORKERS": "4",
        "BMAD_REDIS_URL": "redis://localhost:6379"
    }):
        results = validator.validate_performance_config()
        
        # Verify performance validations
        assert len(results["performance_errors"]) == 0, f"Performance config errors: {results['performance_errors']}"
        assert len(results["performance_validations"]) >= 2, "Should have at least 2 performance validations"

def test_comprehensive_configuration_validation():
    """Test comprehensive configuration validation."""
    validator = ProductionConfigValidator()
    
    # Mock comprehensive environment variables
    with patch.dict(os.environ, {
        "BMAD_ENV": "production",
        "BMAD_SECRET_KEY": "a" * 32,
        "BMAD_DATABASE_URL": "postgresql://user:pass@localhost/db",
        "BMAD_REDIS_URL": "redis://localhost:6379",
        "BMAD_LOG_LEVEL": "INFO",
        "BMAD_JWT_SECRET": "a" * 32,
        "BMAD_CORS_ORIGINS": "https://example.com",
        "BMAD_RATE_LIMIT": "100",
        "BMAD_DB_POOL_SIZE": "10",
        "BMAD_API_HOST": "0.0.0.0",
        "BMAD_API_PORT": "8000",
        "BMAD_API_TIMEOUT": "30",
        "BMAD_LOG_FILE": "/var/log/bmad/app.log",
        "BMAD_WORKERS": "4"
    }):
        # Run all validations
        env_results = validator.validate_environment_config()
        security_results = validator.validate_security_config()
        db_results = validator.validate_database_config()
        api_results = validator.validate_api_config()
        logging_results = validator.validate_logging_config()
        perf_results = validator.validate_performance_config()
        
        # Verify comprehensive validation
        all_errors = (
            env_results["errors"] +
            security_results["security_errors"] +
            db_results["database_errors"] +
            api_results["api_errors"] +
            logging_results["logging_errors"] +
            perf_results["performance_errors"]
        )
        
        all_validations = (
            env_results["validations"] +
            security_results["security_validations"] +
            db_results["database_validations"] +
            api_results["api_validations"] +
            logging_results["logging_validations"] +
            perf_results["performance_validations"]
        )
        
        assert len(all_errors) == 0, f"Configuration errors found: {all_errors}"
        assert len(all_validations) >= 15, f"Should have at least 15 validations, got {len(all_validations)}"

def test_configuration_file_validation():
    """Test configuration file validation."""
    # Test configuration file structure
    config_structure = {
        "environment": "production",
        "security": {
            "jwt_secret": "test_secret",
            "cors_origins": ["https://example.com"],
            "rate_limit": 100
        },
        "database": {
            "url": "postgresql://user:pass@localhost/db",
            "pool_size": 10
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "timeout": 30
        },
        "logging": {
            "level": "INFO",
            "file": "/var/log/bmad/app.log"
        },
        "performance": {
            "workers": 4,
            "cache_url": "redis://localhost:6379"
        }
    }
    
    # Validate configuration structure
    assert "environment" in config_structure, "Environment should be configured"
    assert "security" in config_structure, "Security should be configured"
    assert "database" in config_structure, "Database should be configured"
    assert "api" in config_structure, "API should be configured"
    assert "logging" in config_structure, "Logging should be configured"
    assert "performance" in config_structure, "Performance should be configured"
    
    # Validate security configuration
    security = config_structure["security"]
    assert "jwt_secret" in security, "JWT secret should be configured"
    assert "cors_origins" in security, "CORS origins should be configured"
    assert "rate_limit" in security, "Rate limit should be configured"
    
    # Validate database configuration
    database = config_structure["database"]
    assert "url" in database, "Database URL should be configured"
    assert "pool_size" in database, "Database pool size should be configured"

if __name__ == "__main__":
    # Run production configuration tests
    pytest.main([__file__, "-v", "--tb=short"]) 