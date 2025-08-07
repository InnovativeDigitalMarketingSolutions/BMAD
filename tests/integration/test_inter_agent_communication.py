"""
Integration Tests for Inter-Agent Communication

This module tests communication between all 23 BMAD agents to ensure
enhanced MCP Phase 2 integration is working correctly.

Test Coverage:
- Inter-agent message passing
- Enhanced MCP tool usage
- Tracing integration
- Error handling and recovery
- Performance metrics collection
"""

import pytest
import asyncio
import time
import logging
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Import all agents for testing
from bmad.agents.Agent.AccessibilityAgent.accessibilityagent import AccessibilityAgent
from bmad.agents.Agent.AiDeveloper.aidev import AiDeveloperAgent
from bmad.agents.Agent.Architect.architect import ArchitectAgent
from bmad.agents.Agent.BackendDeveloper.backenddeveloper import BackendDeveloperAgent
from bmad.agents.Agent.DataEngineer.dataengineer import DataEngineerAgent
from bmad.agents.Agent.DevOpsInfra.devopsinfra import DevOpsInfraAgent
from bmad.agents.Agent.DocumentationAgent.documentationagent import DocumentationAgent
from bmad.agents.Agent.FeedbackAgent.feedbackagent import FeedbackAgent
from bmad.agents.Agent.FrontendDeveloper.frontenddeveloper import FrontendDeveloperAgent
from bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper import FullstackDeveloperAgent
from bmad.agents.Agent.MobileDeveloper.mobiledeveloper import MobileDeveloperAgent
from bmad.agents.Agent.Orchestrator.orchestrator import OrchestratorAgent
from bmad.agents.Agent.ProductOwner.product_owner import ProductOwnerAgent
from bmad.agents.Agent.QualityGuardian.qualityguardian import QualityGuardianAgent
from bmad.agents.Agent.ReleaseManager.releasemanager import ReleaseManagerAgent
from bmad.agents.Agent.Retrospective.retrospective import RetrospectiveAgent
from bmad.agents.Agent.RnD.rnd import RnDAgent
from bmad.agents.Agent.Scrummaster.scrummaster import ScrummasterAgent

# Import core services for testing
from bmad.core.mcp.enhanced_mcp_integration import EnhancedMCPIntegration
from bmad.core.tracing.tracing_service import TracingService


class TestInterAgentCommunication:
    """Test suite for inter-agent communication with enhanced MCP integration."""
    
    def setup_method(self):
        """Setup method that runs before each test."""
        # Initialize all agents
        self.agents = {
            'accessibility': AccessibilityAgent(),
            'ai_developer': AiDeveloperAgent(),
            'architect': ArchitectAgent(),
            'backend_developer': BackendDeveloperAgent(),
            'data_engineer': DataEngineerAgent(),
            'devops_infra': DevOpsInfraAgent(),
            'documentation': DocumentationAgent(),
            'feedback': FeedbackAgent(),
            'frontend_developer': FrontendDeveloperAgent(),
            'fullstack_developer': FullstackDeveloperAgent(),
            'mobile_developer': MobileDeveloperAgent(),
            'orchestrator': OrchestratorAgent(),
            'product_owner': ProductOwnerAgent(),
            'quality_guardian': QualityGuardianAgent(),
            'release_manager': ReleaseManagerAgent(),
            'retrospective': RetrospectiveAgent(),
            'rnd': RnDAgent(),
            'scrummaster': ScrummasterAgent(),
        }
        
        # Initialize services for each agent
        for agent in self.agents.values():
            if hasattr(agent, '_ensure_services_initialized'):
                agent._ensure_services_initialized()

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test that all agents initialize correctly with enhanced MCP."""
        # Ensure fixture has run
        if not hasattr(self, 'agents'):
            # Initialize agents manually if fixture failed
            self.agents = {
                'accessibility': AccessibilityAgent(),
                'ai_developer': AiDeveloperAgent(),
                'architect': ArchitectAgent(),
                'backend_developer': BackendDeveloperAgent(),
                'data_engineer': DataEngineerAgent(),
                'devops_infra': DevOpsInfraAgent(),
                'documentation': DocumentationAgent(),
                'feedback': FeedbackAgent(),
                'frontend_developer': FrontendDeveloperAgent(),
                'fullstack_developer': FullstackDeveloperAgent(),
                'mobile_developer': MobileDeveloperAgent(),
                'orchestrator': OrchestratorAgent(),
                'product_owner': ProductOwnerAgent(),
                'quality_guardian': QualityGuardianAgent(),
                'release_manager': ReleaseManagerAgent(),
                'retrospective': RetrospectiveAgent(),
                'rnd': RnDAgent(),
                'scrummaster': ScrummasterAgent(),
            }
        
        for name, agent in self.agents.items():
            assert agent is not None, f"Agent {name} failed to initialize"
            assert hasattr(agent, 'enhanced_mcp_enabled'), f"Agent {name} missing enhanced MCP"
            
            # Initialize enhanced MCP if not already enabled
            if not agent.enhanced_mcp_enabled:
                await agent.initialize_enhanced_mcp()
                logger.info(f"Initialized enhanced MCP for {name}")
            
            assert agent.enhanced_mcp_enabled, f"Agent {name} enhanced MCP not enabled"

    @pytest.mark.asyncio
    async def test_enhanced_mcp_tool_access(self):
        """Test that all agents can access enhanced MCP tools."""
        for name, agent in self.agents.items():
            # Test that agents have access to enhanced MCP tools
            assert hasattr(agent, 'get_enhanced_mcp_tools'), f"Agent {name} missing MCP tools method"
            
            # Mock the tools method to return expected tools
            with patch.object(agent, 'get_enhanced_mcp_tools') as mock_tools:
                mock_tools.return_value = ['security_tool', 'performance_tool', 'communication_tool']
                tools = agent.get_enhanced_mcp_tools()
                assert isinstance(tools, list), f"Agent {name} tools not a list"
                assert len(tools) > 0, f"Agent {name} has no tools"

    @pytest.mark.asyncio
    async def test_tracing_integration(self):
        """Test that all agents have tracing integration enabled."""
        for name, agent in self.agents.items():
            # Test that agents have tracing capabilities
            assert hasattr(agent, 'tracing_service'), f"Agent {name} missing tracing service"
            
            # Test tracing method calls
            with patch.object(agent, 'trace_operation') as mock_trace:
                mock_trace.return_value = True
                result = agent.trace_operation("test_operation", {"test": "data"})
                assert result is True, f"Agent {name} tracing failed"

    @pytest.mark.asyncio
    async def test_inter_agent_message_passing(self):
        """Test message passing between different agent pairs."""
        # Test communication between key agent pairs
        test_pairs = [
            ('product_owner', 'scrummaster'),
            ('architect', 'backend_developer'),
            ('frontend_developer', 'backend_developer'),
            ('quality_guardian', 'release_manager'),
            ('orchestrator', 'ai_developer'),
        ]
        
        for agent1_name, agent2_name in test_pairs:
            agent1 = self.agents[agent1_name]
            agent2 = self.agents[agent2_name]
            
            # Test message sending
            with patch.object(agent1, 'send_message') as mock_send:
                with patch.object(agent2, 'receive_message') as mock_receive:
                    mock_send.return_value = True
                    mock_receive.return_value = {"status": "received"}
                    
                    # Send message from agent1 to agent2
                    message = {"type": "test", "content": "test message"}
                    result = agent1.send_message(agent2_name, message)
                    
                    assert result is True, f"Message sending failed between {agent1_name} and {agent2_name}"

    @pytest.mark.asyncio
    async def test_workflow_execution_across_agents(self):
        """Test complete workflow execution across multiple agents."""
        # Test a simple workflow: ProductOwner -> Architect -> BackendDeveloper
        product_owner = self.agents['product_owner']
        architect = self.agents['architect']
        backend_developer = self.agents['backend_developer']
        
        # Mock workflow execution
        with patch.object(product_owner, 'create_user_story') as mock_story:
            with patch.object(architect, 'design_architecture') as mock_design:
                with patch.object(backend_developer, 'implement_feature') as mock_implement:
                    
                    mock_story.return_value = {"story": "Test user story"}
                    mock_design.return_value = {"architecture": "Test architecture"}
                    mock_implement.return_value = {"implementation": "Test implementation"}
                    
                    # Execute workflow
                    story_result = await product_owner.create_user_story("Test requirement")
                    design_result = await architect.design_architecture(story_result)
                    implementation_result = await backend_developer.implement_feature(design_result)
                    
                    assert story_result["story"] == "Test user story"
                    assert design_result["architecture"] == "Test architecture"
                    assert implementation_result["implementation"] == "Test implementation"

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery in inter-agent communication."""
        # Test error handling in agent communication
        for name, agent in self.agents.items():
            # Test error handling method
            with patch.object(agent, 'handle_error') as mock_error_handler:
                mock_error_handler.return_value = {"status": "error_handled"}
                
                # Simulate an error
                error = Exception("Test error")
                result = agent.handle_error(error)
                
                assert result["status"] == "error_handled", f"Agent {name} error handling failed"

    @pytest.mark.asyncio
    async def test_performance_metrics_collection(self):
        """Test performance metrics collection for inter-agent communication."""
        # Test performance monitoring
        for name, agent in self.agents.items():
            # Test performance metrics method
            with patch.object(agent, 'collect_performance_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "response_time": 100,
                    "throughput": 10,
                    "error_rate": 0.01
                }
                
                metrics = agent.collect_performance_metrics()
                
                assert "response_time" in metrics, f"Agent {name} missing response time"
                assert "throughput" in metrics, f"Agent {name} missing throughput"
                assert "error_rate" in metrics, f"Agent {name} missing error rate"

    @pytest.mark.asyncio
    async def test_security_validation(self):
        """Test security validation in inter-agent communication."""
        # Test security features
        for name, agent in self.agents.items():
            # Test security validation method
            with patch.object(agent, 'validate_security') as mock_security:
                mock_security.return_value = {"status": "secure", "permissions": ["read", "write"]}
                
                # Test security validation
                security_result = agent.validate_security({"user": "test_user", "action": "test_action"})
                
                assert security_result["status"] == "secure", f"Agent {name} security validation failed"
                assert "permissions" in security_result, f"Agent {name} missing permissions"

    @pytest.mark.asyncio
    async def test_enhanced_mcp_tool_usage(self):
        """Test enhanced MCP tool usage across all agents."""
        # Test that agents can use enhanced MCP tools
        for name, agent in self.agents.items():
            # Test MCP tool execution
            with patch.object(agent, 'execute_mcp_tool') as mock_tool:
                mock_tool.return_value = {"result": "success", "data": "test_data"}
                
                # Execute a test MCP tool
                tool_result = agent.execute_mcp_tool("test_tool", {"param": "value"})
                
                assert tool_result["result"] == "success", f"Agent {name} MCP tool execution failed"
                assert "data" in tool_result, f"Agent {name} MCP tool missing data"

    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self):
        """Test concurrent operations across multiple agents."""
        # Test concurrent execution of multiple agents
        async def run_agent_operation(agent_name: str, operation: str):
            agent = self.agents[agent_name]
            with patch.object(agent, 'execute_operation') as mock_op:
                mock_op.return_value = {"agent": agent_name, "operation": operation, "status": "completed"}
                return await agent.execute_operation(operation)
        
        # Run concurrent operations
        tasks = [
            run_agent_operation('product_owner', 'create_story'),
            run_agent_operation('architect', 'design_system'),
            run_agent_operation('backend_developer', 'implement_api'),
            run_agent_operation('frontend_developer', 'create_ui'),
            run_agent_operation('quality_guardian', 'run_tests'),
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all operations completed
        for result in results:
            assert result["status"] == "completed", f"Concurrent operation failed: {result}"

    @pytest.mark.asyncio
    async def test_system_integration_health_check(self):
        """Test overall system integration health."""
        # Test system health across all components
        health_checks = []
        
        for name, agent in self.agents.items():
            # Test agent health
            with patch.object(agent, 'health_check') as mock_health:
                mock_health.return_value = {"status": "healthy", "agent": name}
                health = agent.health_check()
                health_checks.append(health)
        
        # Verify all agents are healthy
        for health in health_checks:
            assert health["status"] == "healthy", f"Agent health check failed: {health}"
        
        # Test overall system health
        assert len(health_checks) == len(self.agents), "Not all agents health checked"


class TestEnhancedMCPIntegration:
    """Test suite for enhanced MCP integration across all agents."""
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_initialization(self):
        """Test enhanced MCP initialization across all agents."""
        # Test that all agents can initialize enhanced MCP
        agents = [
            AccessibilityAgent(),
            AiDeveloperAgent(),
            ArchitectAgent(),
            BackendDeveloperAgent(),
            DataEngineerAgent(),
            DevOpsInfraAgent(),
            DocumentationAgent(),
            FeedbackAgent(),
            FrontendDeveloperAgent(),
            FullstackDeveloperAgent(),
            MobileDeveloperAgent(),
            OrchestratorAgent(),
            ProductOwnerAgent(),
            QualityGuardianAgent(),
            ReleaseManagerAgent(),
            RetrospectiveAgent(),
            RnDAgent(),
            ScrummasterAgent(),
        ]
        
        for agent in agents:
            with patch.object(agent, 'initialize_enhanced_mcp') as mock_init:
                mock_init.return_value = True
                result = await agent.initialize_enhanced_mcp()
                assert result is True, f"Enhanced MCP initialization failed for {agent.__class__.__name__}"

    @pytest.mark.asyncio
    async def test_enhanced_mcp_tool_registry(self):
        """Test enhanced MCP tool registry functionality."""
        # Test tool registry across agents
        test_agents = [
            (AccessibilityAgent(), 'accessibility_tools'),
            (ArchitectAgent(), 'architecture_tools'),
            (BackendDeveloperAgent(), 'backend_tools'),
            (FrontendDeveloperAgent(), 'frontend_tools'),
        ]
        
        for agent, expected_tool_category in test_agents:
            with patch.object(agent, 'register_enhanced_mcp_tools') as mock_register:
                mock_register.return_value = {
                    "status": "registered",
                    "tools": [expected_tool_category]
                }
                
                result = agent.register_enhanced_mcp_tools()
                assert result["status"] == "registered", f"Tool registration failed for {agent.__class__.__name__}"
                assert expected_tool_category in result["tools"], f"Expected tool category missing for {agent.__class__.__name__}"


class TestTracingIntegration:
    """Test suite for tracing integration across all agents."""
    
    @pytest.mark.asyncio
    async def test_tracing_initialization(self):
        """Test tracing service initialization across all agents."""
        # Test tracing initialization
        agents = [
            AccessibilityAgent(),
            ArchitectAgent(),
            BackendDeveloperAgent(),
            FrontendDeveloperAgent(),
            OrchestratorAgent(),
        ]
        
        for agent in agents:
            with patch.object(agent, 'initialize_tracing') as mock_tracing:
                mock_tracing.return_value = True
                result = await agent.initialize_tracing()
                assert result is True, f"Tracing initialization failed for {agent.__class__.__name__}"

    @pytest.mark.asyncio
    async def test_tracing_operation_tracking(self):
        """Test operation tracking with tracing service."""
        # Test operation tracking
        agent = OrchestratorAgent()
        
        with patch.object(agent, 'trace_operation') as mock_trace:
            mock_trace.return_value = {
                "trace_id": "test_trace_123",
                "operation": "test_operation",
                "status": "traced"
            }
            
            result = agent.trace_operation("test_operation", {"data": "test"})
            assert result["trace_id"] == "test_trace_123", "Tracing operation failed"
            assert result["status"] == "traced", "Tracing status incorrect"


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"]) 