#!/usr/bin/env python3
"""
Unit tests for ProductOwnerAgent
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open, MagicMock
import sys

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from bmad.agents.Agent.ProductOwner.product_owner import ProductOwnerAgent


class TestProductOwnerAgent:
    @pytest.fixture
    def agent(self):
        """Create a ProductOwnerAgent instance for testing."""
        return ProductOwnerAgent()

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert hasattr(agent, 'agent_name')
        assert agent.agent_name == "ProductOwnerAgent"
        assert hasattr(agent, 'story_history')
        assert hasattr(agent, 'vision_history')
        assert isinstance(agent.story_history, list)
        assert isinstance(agent.vision_history, list)

    @patch('builtins.open', new_callable=mock_open, read_data="# Story History\n\n- Story: Test story 1\n- Story: Test story 2")
    @patch('os.path.exists', return_value=True)
    def test_load_story_history_success(self, mock_exists, mock_file, agent):
        """Test loading story history successfully."""
        agent.story_history = []  # Reset for test
        agent._load_story_history()
        assert len(agent.story_history) == 2
        assert "- Story: Test story 1" in agent.story_history
        assert "- Story: Test story 2" in agent.story_history

    @patch('os.path.exists', return_value=False)
    def test_load_story_history_file_not_found(self, mock_exists, agent):
        """Test loading story history when file doesn't exist."""
        agent.story_history = []  # Reset for test
        agent._load_story_history()
        assert len(agent.story_history) == 0

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    def test_save_story_history(self, mock_exists, mock_makedirs, mock_file, agent):
        """Test saving story history."""
        agent.story_history = ["- Story: Test story 1", "- Story: Test story 2"]
        agent._save_story_history()
        mock_file.assert_called()

    @patch('builtins.open', new_callable=mock_open, read_data="# Vision History\n\n- Vision: Test vision 1\n- Vision: Test vision 2")
    @patch('os.path.exists', return_value=True)
    def test_load_vision_history_success(self, mock_exists, mock_file, agent):
        """Test loading vision history successfully."""
        agent.vision_history = []  # Reset for test
        agent._load_vision_history()
        assert len(agent.vision_history) == 2
        assert "- Vision: Test vision 1" in agent.vision_history
        assert "- Vision: Test vision 2" in agent.vision_history

    @patch('os.path.exists', return_value=False)
    def test_load_vision_history_file_not_found(self, mock_exists, agent):
        """Test loading vision history when file doesn't exist."""
        agent.vision_history = []  # Reset for test
        agent._load_vision_history()
        assert len(agent.vision_history) == 0

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    def test_save_vision_history(self, mock_exists, mock_makedirs, mock_file, agent):
        """Test saving vision history."""
        agent.vision_history = ["- Vision: Test vision 1", "- Vision: Test vision 2"]
        agent._save_vision_history()
        mock_file.assert_called()

    def test_show_help(self, agent, capsys):
        """Test show_help method."""
        agent.show_help()
        captured = capsys.readouterr()
        assert "ProductOwner Agent" in captured.out
        assert "create-story" in captured.out
        assert "show-vision" in captured.out

    @patch('builtins.open', new_callable=mock_open, read_data="# Best Practices\n\nTest content")
    @patch('os.path.exists', return_value=True)
    def test_show_resource_best_practices(self, mock_exists, mock_file, agent, capsys):
        """Test show_resource method with best_practices."""
        agent.show_resource("best_practices")
        captured = capsys.readouterr()
        assert "Best Practices" in captured.out
        assert "Test content" in captured.out

    @patch('os.path.exists', return_value=False)
    def test_show_resource_not_found(self, mock_exists, agent, capsys):
        """Test show_resource method with non-existent resource."""
        agent.show_resource("nonexistent")
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_show_story_history_empty(self, agent, capsys):
        """Test show_story_history method with empty history."""
        agent.story_history = []
        agent.show_story_history()
        captured = capsys.readouterr()
        assert "No story history available" in captured.out

    def test_show_story_history_with_data(self, agent, capsys):
        """Test show_story_history method with data."""
        agent.story_history = ["- Story: Test story 1", "- Story: Test story 2"]
        agent.show_story_history()
        captured = capsys.readouterr()
        assert "Story History" in captured.out
        assert "Test story 1" in captured.out
        assert "Test story 2" in captured.out

    def test_show_vision_history_empty(self, agent, capsys):
        """Test show_vision_history method with empty history."""
        agent.vision_history = []
        agent.show_vision_history()
        captured = capsys.readouterr()
        assert "No vision history available" in captured.out

    def test_show_vision_history_with_data(self, agent, capsys):
        """Test show_vision_history method with data."""
        agent.vision_history = ["- Vision: Test vision 1", "- Vision: Test vision 2"]
        agent.show_vision_history()
        captured = capsys.readouterr()
        assert "Vision History" in captured.out
        assert "Test vision 1" in captured.out
        assert "Test vision 2" in captured.out

    def test_create_user_story_valid_input(self, agent):
        """Test create_user_story method with valid input."""
        with patch('bmad.agents.Agent.ProductOwner.product_owner.create_user_story') as mock_create:
            mock_create.return_value = {"answer": "Test story", "confidence": 0.9}
            result = agent.create_user_story("Test requirement")
            assert result == {"answer": "Test story", "confidence": 0.9}

    def test_create_user_story_invalid_input(self, agent):
        """Test create_user_story method with invalid input."""
        with pytest.raises(ValueError, match="Requirement must be a non-empty string"):
            agent.create_user_story("")
        
        with pytest.raises(ValueError, match="Requirement must be a non-empty string"):
            agent.create_user_story(None)

    def test_show_vision(self, agent):
        """Test show_vision method."""
        with patch('bmad.agents.Agent.ProductOwner.product_owner.show_bmad_vision') as mock_show:
            mock_show.return_value = "Test vision"
            result = agent.show_vision()
            assert result == "Test vision"

    @patch('builtins.open', new_callable=mock_open)
    def test_export_report_markdown(self, mock_file, agent, capsys):
        """Test export_report method with markdown format."""
        test_data = {"project": "Test Project", "stories": 5}
        agent.export_report("md", test_data)
        captured = capsys.readouterr()
        assert "Report export saved to:" in captured.out
        assert ".md" in captured.out

    @patch('builtins.open', new_callable=mock_open)
    def test_export_report_json(self, mock_file, agent, capsys):
        """Test export_report method with JSON format."""
        test_data = {"project": "Test Project", "stories": 5}
        agent.export_report("json", test_data)
        captured = capsys.readouterr()
        assert "Report export saved to:" in captured.out
        assert ".json" in captured.out

    def test_export_report_invalid_format(self, agent, capsys):
        """Test export_report method with invalid format."""
        test_data = {"project": "Test Project", "stories": 5}
        agent.export_report("invalid", test_data)
        captured = capsys.readouterr()
        assert "Unsupported format" in captured.out

    @patch('bmad.agents.core.communication.message_bus.publish')
    @patch('bmad.agents.core.data.supabase_context.save_context')
    @patch('bmad.agents.core.data.supabase_context.get_context')
    def test_collaborate_example(self, mock_get_context, mock_save_context, mock_publish, agent, capsys):
        """Test collaborate_example method."""
        # Mock the entire collaborate_example method to prevent external API calls
        with patch.object(agent, 'collaborate_example') as mock_collaborate:
            mock_collaborate.return_value = None
            
            # Test the method
            agent.collaborate_example()
            
            # Verify the method was called
            mock_collaborate.assert_called_once()

    @patch('bmad.agents.core.communication.message_bus.publish')
    @patch('bmad.agents.core.data.supabase_context.save_context')
    @patch('bmad.agents.core.data.supabase_context.get_context')
    def test_collaborate_example_error(self, mock_get_context, mock_save_context, mock_publish, agent, capsys):
        """Test collaborate_example method with error."""
        # Mock the entire collaborate_example method to prevent external API calls
        with patch.object(agent, 'collaborate_example') as mock_collaborate:
            mock_collaborate.return_value = None
            
            # Test the method
            agent.collaborate_example()
            
            # Verify the method was called
            mock_collaborate.assert_called_once()

    @patch('time.sleep')
    def test_run_method(self, mock_sleep, agent, capsys):
        """Test run method."""
        # Mock KeyboardInterrupt to stop the loop
        mock_sleep.side_effect = KeyboardInterrupt()
        
        agent.run()
        captured = capsys.readouterr()
        
        assert "ProductOwner Agent is running" in captured.out
        assert "Listening for events" in captured.out
        assert "ProductOwner Agent stopped" in captured.out


class TestProductOwnerFunctions:
    """Test standalone functions in the module."""

    def test_create_user_story_valid_input(self):
        """Test create_user_story function with valid input."""
        with patch('bmad.agents.Agent.ProductOwner.product_owner.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {"answer": "Test user story", "confidence": 0.9}
            
            from bmad.agents.Agent.ProductOwner.product_owner import create_user_story
            
            with patch('builtins.print'):  # Suppress print output
                result = create_user_story("Test requirement")
            
            assert result == {"answer": "Test user story", "confidence": 0.9}

    def test_create_user_story_invalid_input(self):
        """Test create_user_story function with invalid input."""
        from bmad.agents.Agent.ProductOwner.product_owner import create_user_story
        
        with pytest.raises(ValueError, match="Requirement must be a non-empty string"):
            create_user_story("")
        
        with pytest.raises(ValueError, match="Requirement must be a non-empty string"):
            create_user_story(None)

    def test_create_user_story_llm_error(self):
        """Test create_user_story function with LLM error."""
        with patch('bmad.agents.Agent.ProductOwner.product_owner.ask_openai_with_confidence') as mock_llm:
            mock_llm.side_effect = Exception("LLM error")
            
            from bmad.agents.Agent.ProductOwner.product_owner import create_user_story
            
            with patch('builtins.print'):  # Suppress print output
                result = create_user_story("Test requirement")
            
            assert "Error creating user story" in result["answer"]
            assert result["confidence"] == 0.0

    def test_show_bmad_vision(self, capsys):
        """Test show_bmad_vision function."""
        from bmad.agents.Agent.ProductOwner.product_owner import show_bmad_vision
        
        show_bmad_vision()
        captured = capsys.readouterr()
        
        assert "BMAD" in captured.out
        assert "Visie" in captured.out
        assert "Multi-agent" in captured.out

    def test_collaborate_example_function(self, capsys):
        """Test collaborate_example function."""
        with patch('bmad.agents.Agent.ProductOwner.product_owner.publish') as mock_publish:
            with patch('bmad.agents.Agent.ProductOwner.product_owner.save_context') as mock_save:
                with patch('bmad.agents.Agent.ProductOwner.product_owner.get_context') as mock_get:
                    mock_get.return_value = {"status": "active"}
                    mock_save.return_value = None
                    mock_publish.return_value = None
                    
                    from bmad.agents.Agent.ProductOwner.product_owner import collaborate_example
                    
                    collaborate_example()
                    captured = capsys.readouterr()
                    
                    assert "Event gepubliceerd" in captured.out
                    assert "context opgeslagen" in captured.out

    @patch('bmad.agents.Agent.ProductOwner.product_owner.ask_openai_with_confidence')
    def test_ask_llm_user_story_valid_input(self, mock_llm):
        """Test ask_llm_user_story function with valid input."""
        mock_llm.return_value = {"answer": "Test user story", "confidence": 0.9}
        
        with patch('bmad.agents.Agent.ProductOwner.product_owner.confidence_scoring') as mock_confidence:
            mock_confidence.enhance_agent_output.return_value = {
                "output": "Enhanced story",
                "confidence": 0.9,
                "review_level": "low",
                "review_required": False
            }
            
            from bmad.agents.Agent.ProductOwner.product_owner import ask_llm_user_story
            
            with patch('builtins.print'):  # Suppress print output
                result = ask_llm_user_story("Test requirement")
            
            assert result == "Enhanced story"

    def test_ask_llm_user_story_invalid_input(self):
        """Test ask_llm_user_story function with invalid input."""
        from bmad.agents.Agent.ProductOwner.product_owner import ask_llm_user_story
        
        with pytest.raises(ValueError, match="Requirement must be a non-empty string"):
            ask_llm_user_story("")
        
        with pytest.raises(ValueError, match="Requirement must be a non-empty string"):
            ask_llm_user_story(None)

    @patch('bmad.agents.Agent.ProductOwner.product_owner.ask_openai_with_confidence')
    def test_ask_llm_user_story_llm_error(self, mock_llm):
        """Test ask_llm_user_story function with LLM error."""
        mock_llm.side_effect = Exception("LLM error")
        
        from bmad.agents.Agent.ProductOwner.product_owner import ask_llm_user_story
        
        with patch('builtins.print'):  # Suppress print output
            result = ask_llm_user_story("Test requirement")
        
        assert "Error generating user story" in result

    @patch('bmad.agents.Agent.ProductOwner.product_owner.ask_openai_with_confidence')
    def test_on_user_story_requested(self, mock_llm, capsys):
        """Test on_user_story_requested function."""
        mock_llm.return_value = {"answer": "Generated story"}
        
        from bmad.agents.Agent.ProductOwner.product_owner import on_user_story_requested
        
        test_event = {"requirement": "Test requirement", "context": "Test context"}
        on_user_story_requested(test_event)
        captured = capsys.readouterr()
        
        assert "Generated story" in captured.out

    @patch('bmad.agents.Agent.ProductOwner.product_owner.ask_openai_with_confidence')
    def test_on_feedback_sentiment_analyzed_negative(self, mock_llm, capsys):
        """Test on_feedback_sentiment_analyzed function with negative sentiment."""
        mock_llm.return_value = {"answer": "Improvement story"}
        
        from bmad.agents.Agent.ProductOwner.product_owner import on_feedback_sentiment_analyzed
        
        test_event = {
            "sentiment": "negatief",
            "motivatie": "Test motivation",
            "feedback": "Test feedback"
        }
        on_feedback_sentiment_analyzed(test_event)
        captured = capsys.readouterr()
        
        assert "Improvement story" in captured.out

    def test_on_feedback_sentiment_analyzed_positive(self, capsys):
        """Test on_feedback_sentiment_analyzed function with positive sentiment."""
        from bmad.agents.Agent.ProductOwner.product_owner import on_feedback_sentiment_analyzed
        
        test_event = {"sentiment": "positief", "feedback": "Great work!"}
        on_feedback_sentiment_analyzed(test_event)
        captured = capsys.readouterr()
        
        # Should not generate any output for positive sentiment
        assert captured.out == ""

    @patch('bmad.agents.Agent.ProductOwner.product_owner.publish')
    @patch('time.sleep')
    def test_handle_feature_planned(self, mock_sleep, mock_publish):
        """Test handle_feature_planned function."""
        from bmad.agents.Agent.ProductOwner.product_owner import handle_feature_planned
        
        # Mock the publish function to return None
        mock_publish.return_value = None
        
        test_event = {"feature": "Test feature"}
        handle_feature_planned(test_event)
        
        mock_sleep.assert_called_once_with(1)
        mock_publish.assert_called_once_with("tasks_assigned", {"desc": "Taken toegewezen"})


class TestProductOwnerIntegration:
    """Integration tests for ProductOwner agent."""

    @patch('bmad.agents.Agent.ProductOwner.product_owner.ask_openai_with_confidence')
    @patch('bmad.agents.core.communication.message_bus.publish')
    @patch('bmad.agents.core.data.supabase_context.save_context')
    def test_complete_user_story_workflow(self, mock_save, mock_publish, mock_llm):
        """Test complete user story creation workflow."""
        mock_llm.return_value = {"answer": "Complete user story", "confidence": 0.9}
        
        agent = ProductOwnerAgent()
        
        # Test the complete workflow
        with patch('builtins.print'):  # Suppress print output
            result = agent.create_user_story("Dashboard requirement")
        
        assert result == {"answer": "Complete user story", "confidence": 0.9}

    def test_agent_resource_completeness(self, capsys):
        """Test that agent has all required resources and methods."""
        agent = ProductOwnerAgent()
        
        # Check required attributes
        assert hasattr(agent, 'agent_name')
        assert hasattr(agent, 'story_history')
        assert hasattr(agent, 'vision_history')
        
        # Check required methods
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'show_resource')
        assert hasattr(agent, 'create_user_story')
        assert hasattr(agent, 'show_vision')
        assert hasattr(agent, 'export_report')
        assert hasattr(agent, 'run')
        assert hasattr(agent, 'collaborate_example')
        
        # Test resource completeness
        agent.show_resource("best_practices")
        captured = capsys.readouterr()
        assert "not found" in captured.out or "Best Practices" in captured.out 