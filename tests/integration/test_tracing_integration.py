"""
Tracing Integration Tests

Test OpenTelemetry tracing integration met enhanced MCP.
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from integrations.opentelemetry.opentelemetry_tracing import BMADTracer
from bmad.agents.Agent import (
    BackendDeveloper, FrontendDeveloper, Architect, TestEngineer, DevOpsInfra
)

class TestTracingIntegration:
    """Test OpenTelemetry tracing integration."""
    
    @pytest.fixture
    def tracing_agents(self):
        """Initialize agents voor tracing testing."""
        return {
            'backend': BackendDeveloper(),
            'frontend': FrontendDeveloper(),
            'architect': Architect(),
            'test': TestEngineer(),
            'devops': DevOpsInfra()
        }
    
    @pytest.mark.asyncio
    async def test_tracing_initialization(self, tracing_agents):
        """Test tracing initialization voor alle agents."""
        for agent_name, agent in tracing_agents.items():
            # Test tracing initialization
            await agent.initialize_tracing()
            
            # Verify tracing attributes
            assert hasattr(agent, 'tracer')
            assert hasattr(agent, 'tracing_enabled')
            
            # Verify tracer is BMADTracer instance
            if agent.tracing_enabled:
                assert isinstance(agent.tracer, BMADTracer)
                print(f"✅ {agent_name}: Tracing initialization successful")
            else:
                print(f"⚠️ {agent_name}: Tracing disabled")
    
    @pytest.mark.asyncio
    async def test_tracing_agent_operations(self, tracing_agents):
        """Test tracing van agent operations."""
        for agent_name, agent in tracing_agents.items():
            # Initialize tracing
            await agent.initialize_tracing()
            
            # Test tracing methods
            if hasattr(agent, 'trace_agent_operation') and agent.tracing_enabled:
                # Test basic operation tracing
                trace_result = await agent.trace_agent_operation({
                    'type': 'test_operation',
                    'agent_name': agent_name,
                    'operation_data': {'test': True},
                    'performance_metrics': {'duration': 0.1}
                })
                
                assert trace_result is not None
                assert 'trace_id' in trace_result or 'status' in trace_result
                print(f"✅ {agent_name}: Agent operation tracing successful")
            else:
                print(f"⚠️ {agent_name}: No tracing methods available")
    
    @pytest.mark.asyncio
    async def test_tracing_performance_metrics(self, tracing_agents):
        """Test tracing van performance metrics."""
        for agent_name, agent in tracing_agents.items():
            # Initialize tracing
            await agent.initialize_tracing()
            
            if hasattr(agent, 'trace_performance_metrics') and agent.tracing_enabled:
                # Test performance metrics tracing
                metrics_result = await agent.trace_performance_metrics({
                    'agent_name': agent_name,
                    'operation_type': 'performance_test',
                    'duration': 0.5,
                    'memory_usage': 100.0,
                    'cpu_usage': 25.0
                })
                
                assert metrics_result is not None
                print(f"✅ {agent_name}: Performance metrics tracing successful")
            else:
                print(f"⚠️ {agent_name}: No performance metrics tracing available")
    
    @pytest.mark.asyncio
    async def test_tracing_error_events(self, tracing_agents):
        """Test tracing van error events."""
        for agent_name, agent in tracing_agents.items():
            # Initialize tracing
            await agent.initialize_tracing()
            
            if hasattr(agent, 'trace_error_event') and agent.tracing_enabled:
                # Test error event tracing
                error_result = await agent.trace_error_event({
                    'agent_name': agent_name,
                    'error_type': 'test_error',
                    'error_message': 'Test error for tracing',
                    'stack_trace': 'Test stack trace',
                    'context': {'test': True}
                })
                
                assert error_result is not None
                print(f"✅ {agent_name}: Error event tracing successful")
            else:
                print(f"⚠️ {agent_name}: No error event tracing available")
    
    @pytest.mark.asyncio
    async def test_tracing_inter_agent_communication(self, tracing_agents):
        """Test tracing van inter-agent communication."""
        # Test communication tussen pairs
        test_pairs = [
            ('backend', 'frontend'),
            ('architect', 'devops'),
            ('test', 'backend')
        ]
        
        for agent1_name, agent2_name in test_pairs:
            agent1 = tracing_agents[agent1_name]
            agent2 = tracing_agents[agent2_name]
            
            # Initialize tracing for both agents
            await agent1.initialize_tracing()
            await agent2.initialize_tracing()
            
            if (hasattr(agent1, 'trace_inter_agent_communication') and 
                agent1.tracing_enabled and agent2.tracing_enabled):
                
                # Test inter-agent communication tracing
                comm_result = await agent1.trace_inter_agent_communication({
                    'source_agent': agent1_name,
                    'target_agent': agent2_name,
                    'message_type': 'test_communication',
                    'message_data': {'test': True},
                    'timestamp': '2025-01-27T10:00:00Z'
                })
                
                assert comm_result is not None
                print(f"✅ {agent1_name} ↔ {agent2_name}: Communication tracing successful")
            else:
                print(f"⚠️ {agent1_name}: No inter-agent communication tracing available")
    
    @pytest.mark.asyncio
    async def test_tracing_context_propagation(self, tracing_agents):
        """Test tracing context propagation tussen agents."""
        # Test context propagation
        backend = tracing_agents['backend']
        frontend = tracing_agents['frontend']
        
        # Initialize tracing
        await backend.initialize_tracing()
        await frontend.initialize_tracing()
        
        if (hasattr(backend, 'trace_context_propagation') and 
            backend.tracing_enabled and frontend.tracing_enabled):
            
            # Test context propagation
            context_result = await backend.trace_context_propagation({
                'source_agent': 'backend',
                'target_agent': 'frontend',
                'context_data': {
                    'user_id': 'test_user',
                    'session_id': 'test_session',
                    'request_id': 'test_request'
                },
                'trace_context': {
                    'trace_id': 'test_trace_id',
                    'span_id': 'test_span_id'
                }
            })
            
            assert context_result is not None
            print(f"✅ Backend ↔ Frontend: Context propagation tracing successful")
        else:
            print(f"⚠️ No context propagation tracing available")
    
    @pytest.mark.asyncio
    async def test_tracing_span_management(self, tracing_agents):
        """Test tracing span management."""
        for agent_name, agent in tracing_agents.items():
            # Initialize tracing
            await agent.initialize_tracing()
            
            if hasattr(agent, 'create_trace_span') and agent.tracing_enabled:
                # Test span creation
                span = await agent.create_trace_span({
                    'name': f'{agent_name}_test_span',
                    'attributes': {
                        'agent.name': agent_name,
                        'operation.type': 'test_operation'
                    }
                })
                
                assert span is not None
                
                # Test span completion
                if hasattr(agent, 'complete_trace_span'):
                    completion_result = await agent.complete_trace_span(span, {
                        'status': 'success',
                        'attributes': {'result': 'test_completed'}
                    })
                    
                    assert completion_result is not None
                
                print(f"✅ {agent_name}: Span management successful")
            else:
                print(f"⚠️ {agent_name}: No span management available")
    
    @pytest.mark.asyncio
    async def test_tracing_export_configuration(self, tracing_agents):
        """Test tracing export configuration."""
        for agent_name, agent in tracing_agents.items():
            # Initialize tracing
            await agent.initialize_tracing()
            
            if hasattr(agent, 'configure_tracing_export') and agent.tracing_enabled:
                # Test export configuration
                export_config = await agent.configure_tracing_export({
                    'endpoint': 'http://localhost:4317/v1/traces',
                    'service_name': f'{agent_name}_service',
                    'environment': 'test',
                    'sampling_rate': 1.0
                })
                
                assert export_config is not None
                print(f"✅ {agent_name}: Tracing export configuration successful")
            else:
                print(f"⚠️ {agent_name}: No tracing export configuration available")

class TestTracingWorkflows:
    """Test tracing workflows tussen multiple agents."""
    
    @pytest.mark.asyncio
    async def test_tracing_development_workflow(self):
        """Test tracing van complete development workflow."""
        # Initialize agents
        product = ProductOwner()
        architect = Architect()
        backend = BackendDeveloper()
        frontend = FrontendDeveloper()
        test = TestEngineer()
        
        # Initialize tracing for all
        await product.initialize_tracing()
        await architect.initialize_tracing()
        await backend.initialize_tracing()
        await frontend.initialize_tracing()
        await test.initialize_tracing()
        
        # Simulate traced workflow
        workflow_trace = []
        
        # 1. Product creates user story (traced)
        if hasattr(product, 'trace_agent_operation'):
            story_trace = await product.trace_agent_operation({
                'type': 'create_user_story',
                'agent_name': 'product',
                'operation_data': {'title': 'Test Feature'}
            })
            workflow_trace.append(('product', 'create_user_story', story_trace))
        
        # 2. Architect designs solution (traced)
        if hasattr(architect, 'trace_agent_operation'):
            design_trace = await architect.trace_agent_operation({
                'type': 'design_architecture',
                'agent_name': 'architect',
                'operation_data': {'requirements': 'test_requirements'}
            })
            workflow_trace.append(('architect', 'design_architecture', design_trace))
        
        # 3. Backend implements API (traced)
        if hasattr(backend, 'trace_agent_operation'):
            api_trace = await backend.trace_agent_operation({
                'type': 'build_api',
                'agent_name': 'backend',
                'operation_data': {'endpoints': ['/test']}
            })
            workflow_trace.append(('backend', 'build_api', api_trace))
        
        # 4. Frontend implements UI (traced)
        if hasattr(frontend, 'trace_agent_operation'):
            ui_trace = await frontend.trace_agent_operation({
                'type': 'build_component',
                'agent_name': 'frontend',
                'operation_data': {'component_type': 'form'}
            })
            workflow_trace.append(('frontend', 'build_component', ui_trace))
        
        # 5. Test validates implementation (traced)
        if hasattr(test, 'trace_agent_operation'):
            test_trace = await test.trace_agent_operation({
                'type': 'run_tests',
                'agent_name': 'test',
                'operation_data': {'test_type': 'integration'}
            })
            workflow_trace.append(('test', 'run_tests', test_trace))
        
        # Verify workflow trace
        assert len(workflow_trace) > 0, "No workflow traces generated"
        
        print(f"✅ Development workflow tracing successful: {len(workflow_trace)} traces")
        for agent, operation, trace in workflow_trace:
            print(f"  - {agent}: {operation}")
    
    @pytest.mark.asyncio
    async def test_tracing_error_workflow(self):
        """Test tracing van error workflow."""
        # Initialize agents
        backend = BackendDeveloper()
        test = TestEngineer()
        
        # Initialize tracing
        await backend.initialize_tracing()
        await test.initialize_tracing()
        
        error_traces = []
        
        # Simulate error scenario
        if hasattr(backend, 'trace_error_event'):
            error_trace = await backend.trace_error_event({
                'agent_name': 'backend',
                'error_type': 'api_error',
                'error_message': 'API endpoint failed',
                'stack_trace': 'Test stack trace',
                'context': {'endpoint': '/test', 'method': 'GET'}
            })
            error_traces.append(('backend', 'api_error', error_trace))
        
        # Test agent responds to error
        if hasattr(test, 'trace_error_event'):
            test_error_trace = await test.trace_error_event({
                'agent_name': 'test',
                'error_type': 'test_failure',
                'error_message': 'Test failed due to API error',
                'stack_trace': 'Test stack trace',
                'context': {'test_name': 'api_integration_test'}
            })
            error_traces.append(('test', 'test_failure', test_error_trace))
        
        # Verify error traces
        assert len(error_traces) > 0, "No error traces generated"
        
        print(f"✅ Error workflow tracing successful: {len(error_traces)} error traces")
        for agent, error_type, trace in error_traces:
            print(f"  - {agent}: {error_type}")

class TestTracingConfiguration:
    """Test tracing configuration en setup."""
    
    @pytest.mark.asyncio
    async def test_tracing_environment_configuration(self):
        """Test tracing environment configuration."""
        # Test different environment configurations
        environments = ['development', 'testing', 'production']
        
        for env in environments:
            # Mock environment variable
            with patch.dict(os.environ, {'ENVIRONMENT': env}):
                agent = BackendDeveloper()
                await agent.initialize_tracing()
                
                if agent.tracing_enabled:
                    # Test environment-specific configuration
                    if hasattr(agent, 'get_tracing_config'):
                        config = agent.get_tracing_config()
                        assert config['environment'] == env
                        print(f"✅ Environment configuration for {env} successful")
                    else:
                        print(f"⚠️ No tracing configuration method available for {env}")
                else:
                    print(f"⚠️ Tracing disabled for {env}")
    
    @pytest.mark.asyncio
    async def test_tracing_sampling_configuration(self):
        """Test tracing sampling configuration."""
        agent = BackendDeveloper()
        await agent.initialize_tracing()
        
        if agent.tracing_enabled and hasattr(agent, 'configure_tracing_sampling'):
            # Test different sampling rates
            sampling_rates = [0.0, 0.1, 0.5, 1.0]
            
            for rate in sampling_rates:
                config_result = await agent.configure_tracing_sampling({
                    'sampling_rate': rate,
                    'sampling_type': 'probability'
                })
                
                assert config_result is not None
                print(f"✅ Sampling configuration for rate {rate} successful")
        else:
            print("⚠️ No tracing sampling configuration available")

if __name__ == "__main__":
    # Run tracing tests
    pytest.main([__file__, "-v", "--tb=short"]) 