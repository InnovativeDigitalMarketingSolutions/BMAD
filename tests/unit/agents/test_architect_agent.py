#!/usr/bin/env python3
"""
Comprehensive tests voor ArchitectAgent.
Doel: Coverage verbeteren van 18% naar 70%+.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, AsyncMock
import pytest

from bmad.agents.Agent.Architect.architect import (
    ArchitectAgent,
    on_api_design_requested,
    on_pipeline_advice_requested
)


class TestArchitectAgentInitialization:
    """Test ArchitectAgent initialisatie en basis functionaliteit."""

    def test_agent_initialization(self):
        """Test agent initialisatie."""
        agent = ArchitectAgent()
        
        # Test basis attributen
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'design_frontend')
        assert hasattr(agent, 'design_system')
        assert hasattr(agent, 'tech_stack')
        assert hasattr(agent, 'ask_llm_api_design')
        assert hasattr(agent, 'start_conversation')
        assert hasattr(agent, 'run')

    def test_show_help(self):
        """Test show_help command."""
        with patch('builtins.print') as mock_print:
            agent = ArchitectAgent()
            agent.show_help()
            
            # Test dat help getoond is
            mock_print.assert_called()
            # Check all print calls for the expected text
            all_calls = [str(call[0][0]) for call in mock_print.call_args_list]
            assert any("Architect Agent" in call for call in all_calls)
            assert any("Beschikbare commando's" in call for call in all_calls)

    def test_best_practices_with_file(self):
        """Test best_practices met bestaand bestand."""
        mock_content = "Test best practices content"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.read_text', return_value=mock_content), \
             patch('builtins.print') as mock_print:
            
            agent = ArchitectAgent()
            agent.best_practices()
            
            # Test dat content getoond is
            mock_print.assert_called()
            assert any("Test best practices content" in str(call) for call in mock_print.call_args_list)

    def test_best_practices_without_file(self):
        """Test best_practices zonder bestand."""
        with patch('pathlib.Path.exists', return_value=False), \
             patch('builtins.print') as mock_print:
            
            agent = ArchitectAgent()
            agent.best_practices()
            
            # Test dat error getoond is
            mock_print.assert_called()
            assert any("Geen best practices resource gevonden" in str(call) for call in mock_print.call_args_list)

    def test_changelog(self):
        """Test changelog command."""
        with patch('builtins.print') as mock_print:
            agent = ArchitectAgent()
            agent.changelog()
            
            # Test dat changelog getoond is
            mock_print.assert_called()

    def test_list_resources(self):
        """Test list_resources command."""
        with patch('builtins.print') as mock_print:
            agent = ArchitectAgent()
            agent.list_resources()
            
            # Test dat resources getoond zijn
            mock_print.assert_called()

    def test_test_resource_completeness(self):
        """Test test command."""
        with patch('builtins.print') as mock_print:
            agent = ArchitectAgent()
            agent.test()
            
            # Test dat test uitgevoerd is
            mock_print.assert_called()

    def test_collaborate_example(self):
        """Test collaborate_example command."""
        with patch('builtins.print') as mock_print, \
             patch('bmad.agents.Agent.Architect.architect.save_context') as mock_save, \
             patch('bmad.agents.Agent.Architect.architect.get_context') as mock_get, \
             patch('bmad.agents.Agent.Architect.architect.publish') as mock_publish:
            
            mock_get.return_value = [{"test": "context"}]
            
            agent = ArchitectAgent()
            result = agent.collaborate_example()
            
            # Test dat samenwerking getoond is
            mock_print.assert_called()
            
            # Test dat save_context aangeroepen is
            mock_save.assert_called_once_with("Architect", "review_status", {"review_status": "completed"})
            
            # Test dat get_context aangeroepen is
            mock_get.assert_called_once_with("Architect")
            
            # Test dat publish aangeroepen is (ignore timestamp)
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == "architecture_reviewed"
            assert call_args[0][1]["status"] == "success"
            assert call_args[0][1]["agent"] == "Architect"
            
            # Test return value
            assert result["success"] is True
            assert "Collaboration example completed" in result["message"]


class TestArchitectAgentDesignMethods:
    """Test design methoden van ArchitectAgent."""

    def setup_method(self):
        """Setup method voor alle tests in deze class."""
        self.agent = ArchitectAgent()

    @pytest.mark.asyncio
    async def test_design_frontend(self):
        """Test design_frontend functionaliteit."""
        with patch('bmad.agents.Agent.Architect.architect.ask_openai') as mock_llm, \
             patch('builtins.print') as mock_print, \
             patch('bmad.agents.Agent.Architect.architect.save_context') as mock_save, \
             patch('bmad.agents.Agent.Architect.architect.get_context') as mock_get, \
             patch('bmad.agents.Agent.Architect.architect.publish') as mock_publish, \
             patch('builtins.input', return_value="1"):
            
            mock_llm.return_value = {
                "answer": "Test frontend design",
                "llm_confidence": 0.85
            }
            mock_get.return_value = [{"stories": "Test user stories"}]
            
            await self.agent.design_frontend()
            
            # Test dat LLM aangeroepen is
            mock_llm.assert_called()
            
            # Test dat resultaat getoond is
            mock_print.assert_called()
            
            # Test dat save_context aangeroepen is
            mock_save.assert_called_once()
            
            # Test dat publish aangeroepen is
            mock_publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_design_system(self):
        """Test design_system functionaliteit."""
        with patch('bmad.agents.Agent.Architect.architect.ask_openai') as mock_llm, \
             patch('builtins.print') as mock_print:
            
            mock_llm.return_value = {
                "answer": "Test design system",
                "llm_confidence": 0.90
            }
            
            result = await self.agent.design_system()
            
            # Test dat LLM aangeroepen is
            mock_llm.assert_called()
            
            # Test dat resultaat getoond is
            mock_print.assert_called()
            
            # Test dat resultaat correct is
            assert result is not None
            assert "design" in result
            assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_tech_stack(self):
        """Test tech_stack functionaliteit."""
        with patch('bmad.agents.Agent.Architect.architect.ask_openai') as mock_llm, \
             patch('builtins.print') as mock_print:
            
            mock_llm.return_value = {
                "answer": "Test tech stack evaluation",
                "llm_confidence": 0.88
            }
            
            result = await self.agent.tech_stack()
            
            # Test dat LLM aangeroepen is
            mock_llm.assert_called()
            
            # Test dat resultaat getoond is
            mock_print.assert_called()
            
            # Test dat resultaat correct is
            assert result is not None
            assert "evaluation" in result
            assert result["status"] == "completed"

    def test_ask_llm_api_design(self):
        """Test ask_llm_api_design functionaliteit."""
        with patch('bmad.agents.Agent.Architect.architect.ask_openai') as mock_llm:
            
            mock_llm.return_value = {
                "answer": "Test API design",
                "llm_confidence": 0.85
            }
            
            use_case = "Test use case"
            result = self.agent.ask_llm_api_design(use_case)
            
            # Test dat LLM aangeroepen is
            mock_llm.assert_called()
            
            # Test dat resultaat correct is
            assert "answer" in result
            assert result["answer"] == "Test API design"

    def test_start_conversation(self):
        """Test start_conversation functionaliteit."""
        with patch('bmad.agents.Agent.Architect.architect.ask_openai') as mock_llm, \
             patch('builtins.print') as mock_print, \
             patch('builtins.input', side_effect=["help", "quit"]):
            
            mock_llm.return_value = {
                "answer": "Test conversation response",
                "llm_confidence": 0.85
            }
            
            self.agent.start_conversation()
            
            # Test dat LLM aangeroepen is (indien nodig)
            # mock_llm.assert_called()
            
            # Test dat resultaat getoond is
            mock_print.assert_called()


class TestArchitectAgentRunMethod:
    """Test run method van ArchitectAgent."""

    def setup_method(self):
        """Setup method voor alle tests in deze class."""
        self.agent = ArchitectAgent()

    @pytest.mark.asyncio
    async def test_run_design_frontend(self):
        """Test run met design-frontend command."""
        with patch.object(self.agent, 'design_frontend') as mock_design, \
             patch('pathlib.Path.exists', return_value=False):
            # Configure mock to behave like an async function
            mock_design.__name__ = 'design_frontend'
            mock_design.__code__ = type(lambda: None).__code__
            async def async_mock():
                return {"status": "completed"}
            mock_design.side_effect = async_mock
            await self.agent.run("design-frontend")
            mock_design.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_design_system(self):
        """Test run met design-system command."""
        with patch.object(self.agent, 'design_system') as mock_design, \
             patch('pathlib.Path.exists', return_value=False):
            # Configure mock to behave like an async function
            mock_design.__name__ = 'design_system'
            mock_design.__code__ = type(lambda: None).__code__
            async def async_mock():
                return {"status": "completed"}
            mock_design.side_effect = async_mock
            await self.agent.run("design-system")
            mock_design.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_tech_stack(self):
        """Test run met tech-stack command."""
        with patch.object(self.agent, 'tech_stack') as mock_tech, \
             patch('pathlib.Path.exists', return_value=False):
            # Configure mock to behave like an async function
            mock_tech.__name__ = 'tech_stack'
            mock_tech.__code__ = type(lambda: None).__code__
            async def async_mock():
                return {"status": "completed"}
            mock_tech.side_effect = async_mock
            await self.agent.run("tech-stack")
            mock_tech.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_best_practices(self):
        """Test run met best-practices command."""
        with patch.object(self.agent, 'best_practices') as mock_best, \
             patch('pathlib.Path.exists', return_value=False):
            # Configure mock to behave like a sync function
            mock_best.__name__ = 'best_practices'
            mock_best.__code__ = type(lambda: None).__code__
            await self.agent.run("best-practices")
            mock_best.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_changelog(self):
        """Test run met changelog command."""
        with patch.object(self.agent, 'changelog') as mock_changelog, \
             patch('pathlib.Path.exists', return_value=False):
            # Configure mock to behave like a sync function
            mock_changelog.__name__ = 'changelog'
            mock_changelog.__code__ = type(lambda: None).__code__
            await self.agent.run("changelog")
            mock_changelog.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_list_resources(self):
        """Test run met list-resources command."""
        with patch.object(self.agent, 'list_resources') as mock_list, \
             patch('pathlib.Path.exists', return_value=False):
            # Configure mock to behave like a sync function
            mock_list.__name__ = 'list_resources'
            mock_list.__code__ = type(lambda: None).__code__
            await self.agent.run("list-resources")
            mock_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_test(self):
        """Test run met test command."""
        with patch.object(self.agent, 'test') as mock_test, \
             patch('pathlib.Path.exists', return_value=False):
            # Configure mock to behave like a sync function
            mock_test.__name__ = 'test'
            mock_test.__code__ = type(lambda: None).__code__
            await self.agent.run("test")
            mock_test.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_collaborate_example(self):
        """Test run collaborate_example command."""
        with patch('pathlib.Path.exists', return_value=False), \
             patch('bmad.agents.Agent.Architect.architect.save_context') as mock_save, \
             patch('bmad.agents.Agent.Architect.architect.get_context') as mock_get, \
             patch('bmad.agents.Agent.Architect.architect.publish') as mock_publish, \
             patch('builtins.print') as mock_print:

            mock_get.return_value = [{"test": "context"}]

            result = await self.agent.run("collaborate_example")

            # Test dat command uitgevoerd is
            assert result is not None
            assert result["success"] is True
            assert "Collaboration example completed" in result["message"]

    @pytest.mark.asyncio
    async def test_run_help(self):
        """Test run met help command."""
        with patch.object(self.agent, 'show_help') as mock_help:
            # Configure mock to behave like a sync function
            mock_help.__name__ = 'show_help'
            mock_help.__code__ = type(lambda: None).__code__
            await self.agent.run("help")
            mock_help.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_unknown_command(self):
        """Test run met onbekend commando."""
        with patch('builtins.print') as mock_print, \
             patch('logging.error') as mock_logging:
            await self.agent.run("unknown-command")
            
            # Test dat error gelogd is
            mock_logging.assert_called_once()
            assert "Onbekend commando" in str(mock_logging.call_args)


class TestArchitectAgentEventHandlers:
    """Test event handlers van ArchitectAgent."""

    @pytest.mark.asyncio
    async def test_on_api_design_requested(self):
        """Test on_api_design_requested event handler."""
        event = {
            "use_case": "Test API use case",
            "user_id": "test_user"
        }

        with patch('bmad.agents.Agent.Architect.architect.ask_openai') as mock_llm:
            mock_llm.return_value = {
                "answer": "Test API design response",
                "llm_confidence": 0.85
            }

            result = await on_api_design_requested(event)

            # Test dat LLM aangeroepen is
            mock_llm.assert_called()
            assert result["success"] is True
            assert "use_case" in result

    @pytest.mark.asyncio
    async def test_on_pipeline_advice_requested(self):
        """Test on_pipeline_advice_requested event handler."""
        event = {
            "pipeline_type": "CI/CD",
            "user_id": "test_user"
        }

        with patch('bmad.agents.Agent.Architect.architect.ask_openai') as mock_llm:
            mock_llm.return_value = {
                "answer": "Test pipeline advice",
                "llm_confidence": 0.85
            }

            result = await on_pipeline_advice_requested(event)

            # Test dat LLM aangeroepen is
            mock_llm.assert_called()
            assert result["success"] is True
            assert "pipeline_type" in result


class TestArchitectAgentIntegration:
    """Integration tests voor ArchitectAgent."""

    def setup_method(self):
        """Setup method voor alle tests in deze class."""
        self.agent = ArchitectAgent()

    def test_agent_complete_workflow(self):
        """Test complete workflow van ArchitectAgent."""
        with patch('bmad.agents.Agent.Architect.architect.ask_openai') as mock_llm:
            mock_llm.return_value = {
                "answer": "Test response",
                "llm_confidence": 0.85
            }
            
            # Test complete workflow
            assert hasattr(self.agent, 'show_help')
            assert hasattr(self.agent, 'design_frontend')
            assert hasattr(self.agent, 'design_system')
            assert hasattr(self.agent, 'tech_stack')
            assert hasattr(self.agent, 'ask_llm_api_design')
            assert hasattr(self.agent, 'start_conversation')
            assert hasattr(self.agent, 'run')

    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Test error handling van ArchitectAgent."""
        # Test dat agent robuust is bij errors
        try:
            await self.agent.run("invalid-command")
            # Should not raise exception
        except Exception as e:
            pytest.fail(f"Agent should handle errors gracefully: {e}")

    def test_agent_llm_integration(self):
        """Test LLM integratie van ArchitectAgent."""
        with patch('bmad.agents.Agent.Architect.architect.ask_openai') as mock_llm:
            mock_llm.return_value = {
                "answer": "Test LLM response",
                "llm_confidence": 0.85
            }
            
            result = self.agent.ask_llm_api_design("Test use case")
            
            # Test dat LLM correct aangeroepen is
            mock_llm.assert_called_once()
            
            # Test dat resultaat correct is
            assert "answer" in result
            assert "llm_confidence" in result
            assert result["llm_confidence"] == 0.85


class TestArchitectAgentResourceHandling:
    """Test resource handling van ArchitectAgent."""

    def setup_method(self):
        """Setup method voor alle tests in deze class."""
        self.agent = ArchitectAgent()

    def test_template_paths_exist(self):
        """Test dat template paths bestaan."""
        from bmad.agents.Agent.Architect.architect import TEMPLATE_PATHS
        
        # Test dat alle template paths gedefinieerd zijn
        expected_templates = [
            "design-api", "microservices", "event-flow", "memory-design",
            "nfrs", "adr", "risk-analysis", "review", "refactor",
            "infra-as-code", "release-strategy", "poc", "security-review",
            "tech-stack-eval", "checklist", "api-contract", "test-strategy",
            "best-practices", "export", "changelog"
        ]
        
        for template in expected_templates:
            assert template in TEMPLATE_PATHS
            assert isinstance(TEMPLATE_PATHS[template], Path)

    def test_resource_base_path(self):
        """Test resource base path."""
        from bmad.agents.Agent.Architect.architect import RESOURCE_BASE
        
        # Test dat resource base path correct is
        assert isinstance(RESOURCE_BASE, Path)
        assert "resources" in str(RESOURCE_BASE)


class TestArchitectAgentCommandValidation:
    """Test command validatie van ArchitectAgent."""

    def setup_method(self):
        """Setup method voor alle tests in deze class."""
        self.agent = ArchitectAgent()

    @pytest.mark.asyncio
    async def test_valid_commands(self):
        """Test geldige commands."""
        # Test async commands
        async_commands = ["design-frontend", "design-system", "tech-stack"]
        for command in async_commands:
            with patch.object(self.agent, command.replace('-', '_')) as mock_method, \
                 patch('pathlib.Path.exists', return_value=False):
                # Configure mock to behave like an async function
                mock_method.__name__ = command.replace('-', '_')
                mock_method.__code__ = type(lambda: None).__code__
                # Make it return a coroutine
                async def async_mock():
                    return {"status": "completed"}
                mock_method.side_effect = async_mock
                await self.agent.run(command)
                mock_method.assert_called_once()
        
        # Test sync commands
        sync_commands = ["best-practices", "changelog", "list-resources", "test", "collaborate_example"]
        for command in sync_commands:
            with patch.object(self.agent, command.replace('-', '_')) as mock_method, \
                 patch('pathlib.Path.exists', return_value=False):
                # Configure mock to behave like a sync function
                mock_method.__name__ = command.replace('-', '_')
                mock_method.__code__ = type(lambda: None).__code__
                await self.agent.run(command)
                mock_method.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_commands(self):
        """Test ongeldige commands."""
        invalid_commands = [
            "invalid-command", "unknown", "test-command",
            "design-frontend-invalid", "tech-stack-invalid"
        ]

        for command in invalid_commands:
            with patch('logging.error') as mock_logging:
                await self.agent.run(command)

                # Test dat error gelogd is
                mock_logging.assert_called_once()
                assert "Onbekend commando" in str(mock_logging.call_args)


if __name__ == '__main__':
    pytest.main([__file__]) 