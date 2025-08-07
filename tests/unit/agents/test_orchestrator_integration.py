"""
Test Orchestrator Agent Integration with Message Bus
"""
import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from bmad.agents.Agent.Orchestrator.orchestrator import OrchestratorAgent
from bmad.core.message_bus import EventTypes, get_message_bus


class TestOrchestratorIntegration:
    """Test Orchestrator Agent integration with message bus"""

    @pytest_asyncio.fixture
    async def orchestrator_agent(self):
        """Create Orchestrator agent instance"""
        agent = OrchestratorAgent()
        yield agent
        # Cleanup - MessageBus doesn't have a close method

    @pytest.mark.asyncio
    async def test_agent_initialization(self, orchestrator_agent):
        """Test that agent initializes correctly with message bus integration"""
        assert orchestrator_agent.agent_name == "Orchestrator"
        assert hasattr(orchestrator_agent, 'message_bus')
        # The agent extends AgentMessageBusIntegration, so it has all those methods
        assert hasattr(orchestrator_agent, 'publish_agent_event')
        assert hasattr(orchestrator_agent, 'subscribe_to_event')

    @pytest.mark.asyncio
    async def test_message_bus_initialization(self, orchestrator_agent):
        """Test message bus initialization"""
        await orchestrator_agent.initialize_message_bus()
        
        # Check that agent is subscribed to relevant event types (not categories)
        # The agent should be subscribed to specific event types, not category names
        assert len(orchestrator_agent.subscribed_events) > 0
        # Check for some specific event types that should be subscribed
        assert EventTypes.AGENT_COLLABORATION_REQUESTED in orchestrator_agent.subscribed_events
        assert EventTypes.TASK_DELEGATED in orchestrator_agent.subscribed_events

    @pytest.mark.asyncio
    async def test_event_handler_registration(self, orchestrator_agent):
        """Test that event handlers are registered correctly"""
        await orchestrator_agent.initialize_message_bus()
        
        # Check that specific event handlers are registered
        assert EventTypes.WORKFLOW_EXECUTION_REQUESTED in orchestrator_agent.event_handlers
        assert EventTypes.WORKFLOW_OPTIMIZATION_REQUESTED in orchestrator_agent.event_handlers
        assert EventTypes.WORKFLOW_MONITORING_REQUESTED in orchestrator_agent.event_handlers
        assert EventTypes.AGENT_COLLABORATION_REQUESTED in orchestrator_agent.event_handlers
        assert EventTypes.TASK_DELEGATED in orchestrator_agent.event_handlers

    @pytest.mark.asyncio
    async def test_workflow_execution_handler(self, orchestrator_agent):
        """Test workflow execution event handler"""
        await orchestrator_agent.initialize_message_bus()
        
        # Mock the start_workflow method
        with patch.object(orchestrator_agent, 'start_workflow', return_value={"status": "started"}):
            with patch.object(orchestrator_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
                # Create test event
                event = {
                    "data": {
                        "workflow_name": "test_workflow"
                    }
                }
                
                # Call the handler
                await orchestrator_agent._handle_workflow_execution_requested(event)
                
                # Verify start_workflow was called
                orchestrator_agent.start_workflow.assert_called_once_with("test_workflow")
                
                # Verify event was published
                mock_publish.assert_called_once_with(
                    EventTypes.WORKFLOW_EXECUTION_STARTED,
                    {
                        "workflow_name": "test_workflow",
                        "status": "started",
                        "result": {"status": "started"}
                    }
                )

    @pytest.mark.asyncio
    async def test_workflow_optimization_handler(self, orchestrator_agent):
        """Test workflow optimization event handler"""
        await orchestrator_agent.initialize_message_bus()
        
        # Mock the analyze_metrics method
        with patch.object(orchestrator_agent, 'analyze_metrics', return_value={"optimization": "result"}):
            with patch.object(orchestrator_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
                # Create test event
                event = {
                    "data": {
                        "workflow_name": "test_workflow"
                    }
                }
                
                # Call the handler
                await orchestrator_agent._handle_workflow_optimization_requested(event)
                
                # Verify analyze_metrics was called
                orchestrator_agent.analyze_metrics.assert_called_once_with("workflow_performance", "30 days")
                
                # Verify event was published
                mock_publish.assert_called_once_with(
                    EventTypes.WORKFLOW_OPTIMIZATION_COMPLETED,
                    {
                        "workflow_name": "test_workflow",
                        "optimization_result": {"optimization": "result"}
                    }
                )

    @pytest.mark.asyncio
    async def test_workflow_monitoring_handler(self, orchestrator_agent):
        """Test workflow monitoring event handler"""
        await orchestrator_agent.initialize_message_bus()
        
        # Mock the monitor_workflows method
        with patch.object(orchestrator_agent, 'monitor_workflows', return_value={"monitoring": "result"}):
            with patch.object(orchestrator_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
                # Create test event
                event = {"data": {}}
                
                # Call the handler
                await orchestrator_agent._handle_workflow_monitoring_requested(event)
                
                # Verify monitor_workflows was called
                orchestrator_agent.monitor_workflows.assert_called_once()
                
                # Verify event was published
                mock_publish.assert_called_once_with(
                    EventTypes.WORKFLOW_MONITORING_COMPLETED,
                    {
                        "monitoring_result": {"monitoring": "result"}
                    }
                )

    @pytest.mark.asyncio
    async def test_agent_collaboration_handler(self, orchestrator_agent):
        """Test agent collaboration event handler"""
        await orchestrator_agent.initialize_message_bus()
        
        # Mock the request_collaboration method
        with patch.object(orchestrator_agent, 'request_collaboration', new_callable=AsyncMock) as mock_request:
            # Create test event
            event = {
                "data": {
                    "target_agent": "TestAgent",
                    "task": "test_task"
                }
            }
            
            # Call the handler
            await orchestrator_agent._handle_agent_collaboration_requested(event)
            
            # Verify request_collaboration was called
            mock_request.assert_called_once_with("TestAgent", "test_task")

    @pytest.mark.asyncio
    async def test_task_delegation_handler(self, orchestrator_agent):
        """Test task delegation event handler"""
        await orchestrator_agent.initialize_message_bus()
        
        # Mock the accept_task method
        with patch.object(orchestrator_agent, 'accept_task', new_callable=AsyncMock) as mock_accept:
            # Create test event
            event = {
                "data": {
                    "task": "test_task",
                    "target_agent": "TestAgent"
                }
            }
            
            # Call the handler
            await orchestrator_agent._handle_task_delegated(event)
            
            # Verify accept_task was called
            mock_accept.assert_called_once_with("test_task", "TestAgent")

    @pytest.mark.asyncio
    async def test_collaborate_example_with_message_bus(self, orchestrator_agent):
        """Test collaborate_example method with new message bus"""
        await orchestrator_agent.initialize_message_bus()
        
        # Mock the publish_agent_event method
        with patch.object(orchestrator_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            with patch.object(orchestrator_agent, 'monitor_workflows', return_value={"workflow_metrics": {"success_rate": 95}}):
                with patch.object(orchestrator_agent, 'orchestrate_agents', return_value={"status": "success"}):
                    with patch.object(orchestrator_agent, 'manage_escalations', return_value={"status": "handled"}):
                        with patch('bmad.agents.Agent.Orchestrator.orchestrator.send_slack_message'):
                            with patch('bmad.agents.Agent.Orchestrator.orchestrator.get_context', return_value={"status": "active"}):
                                with patch('bmad.agents.Agent.Orchestrator.orchestrator.save_context'):
                                    # Call collaborate_example
                                    await orchestrator_agent.collaborate_example()
                                    
                                    # Verify events were published
                                    assert mock_publish.call_count >= 3  # At least 3 events should be published
                                    
                                    # Check specific events
                                    calls = mock_publish.call_args_list
                                    event_types = [call[0][0] for call in calls]
                                    
                                    assert EventTypes.WORKFLOW_STARTED in event_types
                                    assert EventTypes.IDEA_VALIDATION_REQUESTED in event_types
                                    assert EventTypes.ORCHESTRATION_COMPLETED in event_types

    @pytest.mark.asyncio
    async def test_run_async_with_message_bus(self, orchestrator_agent):
        """Test run_async method includes message bus initialization"""
        # Mock all initialization methods
        with patch.object(orchestrator_agent, 'initialize_mcp', new_callable=AsyncMock) as mock_mcp:
            with patch.object(orchestrator_agent, 'initialize_enhanced_mcp', new_callable=AsyncMock) as mock_enhanced_mcp:
                with patch.object(orchestrator_agent, 'initialize_tracing', new_callable=AsyncMock) as mock_tracing:
                    with patch.object(orchestrator_agent, 'initialize_message_bus', new_callable=AsyncMock) as mock_message_bus:
                        with patch.object(orchestrator_agent, 'collaborate_example', new_callable=AsyncMock) as mock_collaborate:
                            # Call run_async
                            await orchestrator_agent.run_async()
                            
                            # Verify all initialization methods were called
                            mock_mcp.assert_called_once()
                            mock_enhanced_mcp.assert_called_once()
                            mock_tracing.assert_called_once()
                            mock_message_bus.assert_called_once()
                            mock_collaborate.assert_called_once()

    @pytest.mark.asyncio
    async def test_hitl_decision_waiting(self, orchestrator_agent):
        """Test wait_for_hitl_decision with new message bus"""
        await orchestrator_agent.initialize_message_bus()
        
        # Mock the message bus get_events method
        with patch.object(orchestrator_agent.message_bus, 'get_events', new_callable=AsyncMock) as mock_get_events:
            # Mock events with the expected structure
            mock_event = Mock()
            mock_event.data = {"alert_id": "test_alert", "approved": True}
            mock_get_events.return_value = [mock_event]
            
            # Call wait_for_hitl_decision
            result = await orchestrator_agent.wait_for_hitl_decision("test_alert", timeout=1)
            
            # Verify result
            assert result is True
            mock_get_events.assert_called_with(EventTypes.HITL_DECISION)

    @pytest.mark.asyncio
    async def test_route_event_with_message_bus(self, orchestrator_agent):
        """Test route_event method with new message bus"""
        await orchestrator_agent.initialize_message_bus()
        
        # Mock the publish_agent_event method
        with patch.object(orchestrator_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            with patch.object(orchestrator_agent, 'log_event'):
                # Test feedback event
                feedback_event = {"event_type": "feedback", "data": "test_feedback"}
                await orchestrator_agent.route_event(feedback_event)
                
                # Verify event was published
                mock_publish.assert_called_once_with(EventTypes.FEEDBACK_RECEIVED, feedback_event)
                
                # Test pipeline_advice event
                mock_publish.reset_mock()
                advice_event = {"event_type": "pipeline_advice", "data": "test_advice"}
                await orchestrator_agent.route_event(advice_event)
                
                # Verify event was published
                mock_publish.assert_called_once_with(EventTypes.PIPELINE_ADVICE_REQUESTED, advice_event)

    @pytest.mark.asyncio
    async def test_replay_history_with_message_bus(self, orchestrator_agent):
        """Test replay_history method with new message bus"""
        await orchestrator_agent.initialize_message_bus()
        
        # Mock event log
        orchestrator_agent.event_log = [
            {"event_type": "test_event_1", "data": "test1"},
            {"event_type": "test_event_2", "data": "test2"}
        ]
        
        # Mock the publish_agent_event method
        with patch.object(orchestrator_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            # Call replay_history
            await orchestrator_agent.replay_history()
            
            # Verify events were published
            assert mock_publish.call_count == 2
            calls = mock_publish.call_args_list
            assert calls[0][0] == ("test_event_1", {"event_type": "test_event_1", "data": "test1"})
            assert calls[1][0] == ("test_event_2", {"event_type": "test_event_2", "data": "test2"})


if __name__ == "__main__":
    pytest.main([__file__]) 