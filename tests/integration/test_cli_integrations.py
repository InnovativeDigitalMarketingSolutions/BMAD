"""
Integration Tests for CLI with Real Dependencies

This test suite tests the CLI with actual external dependencies to ensure
integrations work correctly in real scenarios.

Note: These tests require actual API keys and external services to be configured.
They are slower and may fail due to external service issues, but they provide
confidence that integrations actually work.
"""

import pytest
import asyncio
from unittest.mock import patch
from cli.integrated_workflow_cli import IntegratedWorkflowCLI
from cli.enterprise_cli import EnterpriseCLI
import os


class TestCLIIntegrations:
    """Integration tests for CLI with real external dependencies."""
    
    @pytest.fixture(autouse=True)
    def setup_integration_tests(self):
        """Setup for integration tests with real dependencies."""
        # Skip if integration tests are disabled
        if not pytest.config.getoption("--run-integration"):
            pytest.skip("Integration tests disabled. Use --run-integration to enable.")
        
        # Check if required environment variables are set
        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_KEY", 
            "OPENROUTER_API_KEY",
            "OPENAI_API_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_supabase_integration(self):
        """Test real Supabase database integration."""
        # This test uses the actual Supabase database
        # It will create, read, update, delete real data
        cli = EnterpriseCLI()
        
        # Test tenant creation with real database
        result = await cli.create_tenant(
            name="integration-test-tenant",
            domain="integration-test.com",
            plan="basic"
        )
        
        assert result is not None
        assert "tenant_id" in result
        
        # Clean up - delete the test tenant
        await cli.delete_tenant(result["tenant_id"])
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_openrouter_integration(self):
        """Test real OpenRouter API integration."""
        cli = IntegratedWorkflowCLI()
        
        # Test actual LLM response generation
        response = await cli.test_llm_integration(
            prompt="Hello, this is an integration test",
            model="gpt-3.5-turbo"
        )
        
        assert response is not None
        assert "content" in response
        assert len(response["content"]) > 0
        assert "cost" in response
        assert "duration" in response
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_opentelemetry_integration(self):
        """Test real OpenTelemetry tracing integration."""
        cli = IntegratedWorkflowCLI()
        
        # Test actual tracing functionality
        with cli.tracer.start_span("integration-test") as span:
            span.set_attribute("test.type", "integration")
            span.set_attribute("test.component", "cli")
            
            # Perform some operation
            result = await cli.test_tracing_integration()
            
            assert result is not None
            assert span.is_recording()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_langgraph_integration(self):
        """Test real LangGraph workflow integration."""
        cli = IntegratedWorkflowCLI()
        
        # Test actual workflow execution
        workflow_result = await cli.execute_langgraph_workflow(
            workflow_name="test-workflow",
            input_data={"test": "integration"}
        )
        
        assert workflow_result is not None
        assert "status" in workflow_result
        assert "duration" in workflow_result
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_integration_workflow(self):
        """Test complete integration workflow with all dependencies."""
        cli = IntegratedWorkflowCLI()
        
        # Test a complete workflow that uses all integrations
        result = await cli.execute_integration_workflow(
            workflow_name="full-integration-test",
            context={
                "database": "supabase",
                "llm": "openrouter", 
                "tracing": "opentelemetry",
                "workflow": "langgraph"
            }
        )
        
        assert result is not None
        assert result["status"] == "completed"
        assert "database_result" in result
        assert "llm_result" in result
        assert "tracing_result" in result
        assert "workflow_result" in result


class TestIntegrationErrorHandling:
    """Test error handling in integration scenarios."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_supabase_connection_failure(self):
        """Test handling of Supabase connection failures."""
        cli = EnterpriseCLI()
        
        # Temporarily break the connection
        with patch('integrations.supabase.supabase_client.SupabaseClient') as mock_client:
            mock_client.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception) as exc_info:
                await cli.create_tenant("test", "test.com", "basic")
            
            assert "Connection failed" in str(exc_info.value)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_openrouter_api_failure(self):
        """Test handling of OpenRouter API failures."""
        cli = IntegratedWorkflowCLI()
        
        # Test with invalid API key
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "invalid-key"}):
            with pytest.raises(Exception) as exc_info:
                await cli.test_llm_integration("test", "gpt-3.5-turbo")
            
            assert "authentication" in str(exc_info.value).lower()


# Pytest configuration for integration tests
def pytest_addoption(parser):
    """Add command line options for integration tests."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests with real dependencies"
    )


def pytest_collection_modifyitems(config, items):
    """Mark integration tests appropriately."""
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(reason="Integration tests disabled")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration) 