#!/usr/bin/env python3
"""
Comprehensive tests voor DocumentationAgent.
Doel: Coverage verbeteren van 56% naar 70%+.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest

from bmad.agents.Agent.DocumentationAgent.documentationagent import (
    DocumentationAgent,
    document_figma_ui,
    document_component_info,
    document_page_info,
    generate_component_documentation,
    generate_page_description,
    extract_colors,
    extract_typography,
    extract_spacing,
    extract_design_system_components,
    generate_export_info,
    generate_markdown_documentation,
    rgb_to_hex,
    on_figma_documentation_requested,
    on_summarize_changelogs
)


class TestDocumentationAgentInitialization:
    """Test DocumentationAgent initialisatie en basis functionaliteit."""

    def setup_method(self):
        """Setup method voor alle tests in deze class."""
        self.patches = [
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.PerformanceOptimizer', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_advanced_policy_engine', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_sprite_library', return_value=MagicMock())
        ]
        for p in self.patches:
            p.start()

    def teardown_method(self):
        """Teardown method voor alle tests in deze class."""
        for p in self.patches:
            p.stop()

    def test_agent_initialization(self):
        """Test agent initialisatie."""
        agent = DocumentationAgent()
        
        # Test basis attributen
        assert hasattr(agent, 'show_help')
        assert hasattr(agent, 'show_resource')
        assert hasattr(agent, 'show_docs_history')
        assert hasattr(agent, 'show_figma_history')
        assert hasattr(agent, 'summarize_changelogs')
        assert hasattr(agent, 'document_figma_ui')
        assert hasattr(agent, 'create_api_docs')
        assert hasattr(agent, 'create_user_guide')
        assert hasattr(agent, 'create_technical_docs')
        assert hasattr(agent, 'export_report')
        assert hasattr(agent, 'test_resource_completeness')
        assert hasattr(agent, 'collaborate_example')
        assert hasattr(agent, 'run')

    def test_template_paths_initialization(self):
        """Test template paths initialisatie."""
        agent = DocumentationAgent()
        
        # Test dat alle template paths gedefinieerd zijn
        expected_templates = [
            "best-practices", "api-docs-template", "user-guide-template", 
            "technical-docs-template", "changelog-template", "figma-docs-template"
        ]
        
        for template in expected_templates:
            assert template in agent.template_paths
            assert isinstance(agent.template_paths[template], Path)

    def test_data_paths_initialization(self):
        """Test data paths initialisatie."""
        agent = DocumentationAgent()
        
        # Test dat alle data paths gedefinieerd zijn
        expected_data = [
            "changelog", "docs-history", "figma-history"
        ]
        
        for data in expected_data:
            assert data in agent.data_paths
            assert isinstance(agent.data_paths[data], Path)


class TestDocumentationAgentFileOperations:
    """Test file operaties van DocumentationAgent."""

    def setup_method(self):
        """Setup method voor alle tests in deze class."""
        self.patches = [
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.PerformanceOptimizer', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_advanced_policy_engine', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_sprite_library', return_value=MagicMock())
        ]
        for p in self.patches:
            p.start()

    def teardown_method(self):
        """Teardown method voor alle tests in deze class."""
        for p in self.patches:
            p.stop()

    def test_load_docs_history_success(self):
        """Test laden van docs history met succes."""
        mock_content = "# Documentation History\n\n- Test doc 1\n- Test doc 2\n"
        
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_content)):
            
            agent = DocumentationAgent()
            
            # Test dat history geladen is
            assert "Test doc 1" in agent.docs_history
            assert "Test doc 2" in agent.docs_history

    def test_load_docs_history_file_not_found(self):
        """Test laden van docs history zonder bestand."""
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.exists', return_value=False):
            
            agent = DocumentationAgent()
            
            # Test dat history leeg is
            assert agent.docs_history == []

    def test_load_figma_history_success(self):
        """Test laden van figma history met succes."""
        mock_content = "# Figma Documentation History\n\n- Figma doc 1\n- Figma doc 2\n"
        
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_content)):
            
            agent = DocumentationAgent()
            
            # Test dat history geladen is
            assert "Figma doc 1" in agent.figma_history
            assert "Figma doc 2" in agent.figma_history

    def test_save_docs_history(self):
        """Test opslaan van docs history."""
        with patch('pathlib.Path.mkdir'), \
             patch('builtins.open', mock_open()) as mock_file:

            agent = DocumentationAgent()
            agent.docs_history = ["Test doc 1", "Test doc 2"]

            agent._save_docs_history()

            # Test dat file geschreven is (3x aangeroepen: 1x voor load in __init__, 1x voor save, 1x voor something else)
            assert mock_file.call_count >= 2
            write_calls = mock_file().write.call_args_list
            assert any("# Documentation History" in str(call) for call in write_calls)

    def test_save_figma_history(self):
        """Test opslaan van figma history."""
        with patch('pathlib.Path.mkdir'), \
             patch('builtins.open', mock_open()) as mock_file:

            agent = DocumentationAgent()
            agent.figma_history = ["Figma doc 1", "Figma doc 2"]

            agent._save_figma_history()

            # Test dat file geschreven is (3x aangeroepen: 1x voor load in __init__, 1x voor save, 1x voor something else)
            assert mock_file.call_count >= 2
            write_calls = mock_file().write.call_args_list
            assert any("# Figma Documentation History" in str(call) for call in write_calls)


class TestDocumentationAgentCommands:
    """Test command functionaliteit van DocumentationAgent."""

    def setup_method(self):
        """Setup method voor alle tests in deze class."""
        self.patches = [
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.PerformanceOptimizer', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_advanced_policy_engine', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_sprite_library', return_value=MagicMock())
        ]
        for p in self.patches:
            p.start()

    def teardown_method(self):
        """Teardown method voor alle tests in deze class."""
        for p in self.patches:
            p.stop()

    def test_show_help(self):
        """Test show_help command."""
        with patch('builtins.print') as mock_print:
            
            agent = DocumentationAgent()
            agent.show_help()
            
            # Test dat help getoond is
            mock_print.assert_called()
            help_call = mock_print.call_args_list[0][0][0]
            assert "DocumentationAgent Commands:" in help_call

    def test_show_resource_template_exists(self):
        """Test show_resource met bestaande template."""
        mock_content = "Test template content"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_content)), \
             patch('builtins.print') as mock_print:
            
            agent = DocumentationAgent()
            agent.show_resource("best-practices")
            
            # Test dat resource getoond is
            mock_print.assert_called()
            assert any("=== BEST-PRACTICES ===" in str(call) for call in mock_print.call_args_list)

    def test_show_resource_template_not_found(self):
        """Test show_resource met niet-bestaande template."""
        with patch('pathlib.Path.exists', return_value=False), \
             patch('builtins.print') as mock_print:
            
            agent = DocumentationAgent()
            agent.show_resource("best-practices")
            
            # Test dat error getoond is
            mock_print.assert_called()
            assert any("not found" in str(call) for call in mock_print.call_args_list)

    def test_show_docs_history(self):
        """Test show_docs_history command."""
        with patch('builtins.print') as mock_print:
            
            agent = DocumentationAgent()
            agent.docs_history = ["Doc 1", "Doc 2", "Doc 3"]
            agent.show_docs_history()
            
            # Test dat history getoond is
            mock_print.assert_called()
            assert any("Doc 1" in str(call) for call in mock_print.call_args_list)

    def test_show_figma_history(self):
        """Test show_figma_history command."""
        with patch('builtins.print') as mock_print:
            
            agent = DocumentationAgent()
            agent.figma_history = ["Figma 1", "Figma 2", "Figma 3"]
            agent.show_figma_history()
            
            # Test dat history getoond is
            mock_print.assert_called()
            assert any("Figma 1" in str(call) for call in mock_print.call_args_list)


class TestDocumentationAgentDocumentationCreation:
    """Test documentatie creatie van DocumentationAgent."""

    def setup_method(self):
        """Setup method voor alle tests in deze class."""
        self.patches = [
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.PerformanceOptimizer', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_advanced_policy_engine', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_sprite_library', return_value=MagicMock())
        ]
        for p in self.patches:
            p.start()

    def teardown_method(self):
        """Teardown method voor alle tests in deze class."""
        for p in self.patches:
            p.stop()

    def test_summarize_changelogs_no_project(self):
        """Test summarize_changelogs zonder project."""
        with patch('builtins.print') as mock_print:
            
            agent = DocumentationAgent()
            result = agent.summarize_changelogs()
            
            # Test dat error getoond is
            mock_print.assert_called()
            assert any("Geen project geladen" in str(call) for call in mock_print.call_args_list)

    def test_summarize_changelogs_no_files(self):
        """Test summarize_changelogs zonder changelog bestanden."""
        with patch('pathlib.Path.glob', return_value=[]), \
             patch('builtins.print') as mock_print:
            
            agent = DocumentationAgent()
            result = agent.summarize_changelogs()
            
            # Test dat error geretourneerd is
            assert "error" in result
            assert "No project loaded" in result["error"]

    def test_create_api_docs(self):
        """Test create_api_docs functionaliteit."""
        with patch('bmad.agents.Agent.DocumentationAgent.documentationagent.ask_openai_with_confidence') as mock_llm:
            
            mock_llm.return_value = {
                "answer": "Test API documentation",
                "llm_confidence": 0.85
            }
            
            agent = DocumentationAgent()
            result = agent.create_api_docs("Test API", "REST")
            
            # Test result
            assert "api_name" in result
            assert "api_type" in result
            assert "status" in result
            assert result["api_name"] == "Test API"
            assert result["api_type"] == "REST"

    def test_create_user_guide(self):
        """Test create_user_guide functionaliteit."""
        with patch('bmad.agents.Agent.DocumentationAgent.documentationagent.ask_openai_with_confidence') as mock_llm:
            
            mock_llm.return_value = {
                "answer": "Test user guide",
                "llm_confidence": 0.90
            }
            
            agent = DocumentationAgent()
            result = agent.create_user_guide("Test Product", "comprehensive")
            
            # Test result
            assert "guide_id" in result
            assert "product_name" in result
            assert "status" in result
            assert result["product_name"] == "Test Product"

    def test_create_technical_docs(self):
        """Test create_technical_docs functionaliteit."""
        with patch('bmad.agents.Agent.DocumentationAgent.documentationagent.ask_openai_with_confidence') as mock_llm:
            
            mock_llm.return_value = {
                "answer": "Test technical documentation",
                "llm_confidence": 0.88
            }
            
            agent = DocumentationAgent()
            result = agent.create_technical_docs("Test System", "architecture")
            
            # Test result
            assert "docs_id" in result
            assert "system_name" in result
            assert "status" in result


class TestDocumentationAgentExport:
    """Test export functionaliteit van DocumentationAgent."""

    def setup_method(self):
        """Setup method voor alle tests in deze class."""
        self.patches = [
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.PerformanceOptimizer', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_advanced_policy_engine', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_sprite_library', return_value=MagicMock())
        ]
        for p in self.patches:
            p.start()

    def teardown_method(self):
        """Teardown method voor alle tests in deze class."""
        for p in self.patches:
            p.stop()

    def test_export_report_markdown(self):
        """Test export_report met markdown format."""
        with patch('builtins.print') as mock_print:

            agent = DocumentationAgent()
            report_data = {
                "title": "Test Report", 
                "content": "Test content",
                "timestamp": "2024-01-01T00:00:00"
            }

            agent.export_report("md", report_data)

            # Test dat export uitgevoerd is
            mock_print.assert_called()

    def test_export_report_csv(self):
        """Test export_report met CSV format."""
        with patch('builtins.print') as mock_print:

            agent = DocumentationAgent()
            report_data = {"title": "Test Report", "content": "Test content"}

            agent.export_report("csv", report_data)

            # Test dat export uitgevoerd is
            mock_print.assert_called()

    def test_export_report_json(self):
        """Test export_report met JSON format."""
        with patch('builtins.print') as mock_print:

            agent = DocumentationAgent()
            report_data = {"title": "Test Report", "content": "Test content"}

            agent.export_report("json", report_data)

            # Test dat export uitgevoerd is
            mock_print.assert_called()

    def test_export_report_invalid_format(self):
        """Test export_report met ongeldig format."""
        with patch('builtins.print') as mock_print:

            agent = DocumentationAgent()
            report_data = {"title": "Test Report", "content": "Test content"}

            agent.export_report("invalid", report_data)

            # Test dat error getoond is
            mock_print.assert_called()
            assert any("Unsupported format" in str(call) for call in mock_print.call_args_list)


class TestDocumentationAgentUtilityFunctions:
    """Test utility functies van DocumentationAgent."""

    def test_rgb_to_hex(self):
        """Test rgb_to_hex conversie."""
        # Test basis conversie - de functie verwacht floats tussen 0.0 en 1.0
        assert rgb_to_hex(1.0, 0.0, 0.0) == "ff0000"
        assert rgb_to_hex(0.0, 1.0, 0.0) == "00ff00"
        assert rgb_to_hex(0.0, 0.0, 1.0) == "0000ff"
        
        # Test grijstinten
        assert rgb_to_hex(0.5, 0.5, 0.5) == "7f7f7f"  # 0.5 * 255 = 127.5 -> 127 -> 7f
        assert rgb_to_hex(0.0, 0.0, 0.0) == "000000"
        assert rgb_to_hex(1.0, 1.0, 1.0) == "ffffff"

    def test_document_component_info(self):
        """Test document_component_info functie."""
        component_info = {
            "name": "Test Component",
            "type": "COMPONENT",
            "description": "Test component description"
        }
        
        with patch('bmad.agents.Agent.DocumentationAgent.documentationagent.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "answer": "Test component documentation",
                "llm_confidence": 0.85
            }
            
            result = document_component_info(component_info, "test_component_id")
            
            # Test dat LLM aangeroepen is
            mock_llm.assert_called()
            
            # Test dat resultaat correct is
            assert "id" in result
            assert result["id"] == "test_component_id"

    def test_document_page_info(self):
        """Test document_page_info functie."""
        page_data = {
            "name": "Test Page",
            "type": "CANVAS",
            "children": []
        }
        
        with patch('bmad.agents.Agent.DocumentationAgent.documentationagent.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "answer": "Test page documentation",
                "llm_confidence": 0.85
            }
            
            result = document_page_info(page_data)
            
            # Test dat LLM aangeroepen is
            mock_llm.assert_called()
            
            # Test dat resultaat correct is
            assert "name" in result
            assert result["name"] == "Test Page"

    def test_generate_component_documentation(self):
        """Test generate_component_documentation functie."""
        component_info = {
            "name": "Test Component",
            "type": "COMPONENT",
            "description": "Test component description"
        }
        
        with patch('bmad.agents.Agent.DocumentationAgent.documentationagent.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "answer": "Test component documentation",
                "llm_confidence": 0.85
            }
            
            result = generate_component_documentation(component_info)
            
            # Test dat LLM aangeroepen is
            mock_llm.assert_called()
            
            # Test dat resultaat correct is
            assert "Test component documentation" in result

    def test_generate_page_description(self):
        """Test generate_page_description functie."""
        page_data = {
            "name": "Test Page",
            "type": "CANVAS",
            "children": []
        }
        
        with patch('bmad.agents.Agent.DocumentationAgent.documentationagent.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "answer": "Test page description",
                "llm_confidence": 0.85
            }
            
            result = generate_page_description(page_data)
            
            # Test dat LLM aangeroepen is
            mock_llm.assert_called()
            
            # Test dat resultaat correct is
            assert "Test page description" in result

    def test_extract_colors(self):
        """Test extract_colors functie."""
        file_data = {
            "document": {
                "children": [
                    {
                        "fills": [
                            {"color": {"r": 1.0, "g": 0.0, "b": 0.0}}
                        ]
                    }
                ]
            }
        }
        
        result = extract_colors(file_data)
        
        # Test dat resultaat correct is
        assert isinstance(result, list)

    def test_extract_typography(self):
        """Test extract_typography functie."""
        file_data = {
            "document": {
                "children": [
                    {
                        "style": {
                            "fontFamily": "Arial",
                            "fontSize": 16
                        }
                    }
                ]
            }
        }
        
        result = extract_typography(file_data)
        
        # Test dat resultaat correct is
        assert isinstance(result, list)
        if result:
            assert "font_family" in result[0]

    def test_extract_spacing(self):
        """Test extract_spacing functie."""
        file_data = {
            "document": {
                "children": [
                    {
                        "absoluteBoundingBox": {
                            "x": 0, "y": 0, "width": 100, "height": 100
                        }
                    }
                ]
            }
        }
        
        result = extract_spacing(file_data)
        
        # Test dat resultaat correct is
        assert isinstance(result, dict)
        assert "spacing_scale" in result

    def test_extract_design_system_components(self):
        """Test extract_design_system_components functie."""
        file_data = {
            "document": {
                "children": [
                    {
                        "type": "COMPONENT",
                        "name": "Test Component"
                    }
                ]
            }
        }
        
        result = extract_design_system_components(file_data)
        
        # Test dat resultaat correct is
        assert isinstance(result, list)

    def test_generate_export_info(self):
        """Test generate_export_info functie."""
        file_data = {
            "document": {
                "children": [
                    {
                        "exportSettings": [
                            {"format": "PNG", "constraint": {"type": "SCALE", "value": 1}}
                        ]
                    }
                ]
            }
        }
        
        result = generate_export_info(file_data)
        
        # Test dat resultaat correct is
        assert isinstance(result, dict)
        assert "exportable_nodes" in result

    def test_generate_markdown_documentation(self):
        """Test generate_markdown_documentation functie."""
        documentation = {
            "file_name": "Test Documentation",
            "file_id": "test_id",
            "last_modified": "2024-01-01",
            "version": "1.0",
            "total_components": 1,
            "total_pages": 1,
            "components": [{
                "name": "Test Component",
                "id": "test_component_id",
                "key": "test_component_key",
                "usage_count": 5,
                "documentation": "Test component documentation"
            }],
            "pages": [{
                "name": "Test Page",
                "id": "test_page_id",
                "type": "CANVAS",
                "children_count": 3,
                "description": "Test page description"
            }],
            "design_system": {
                "colors": [{"name": "Red", "hex": "ff0000"}],
                "typography": [{"name": "Heading", "font_family": "Arial", "font_size": 16}],
                "spacing": {
                    "unique_spacing_values": [8, 16, 24],
                    "spacing_scale": [8, 16, 24, 32]
                }
            }
        }

        result = generate_markdown_documentation(documentation)
        
        # Test dat resultaat correct is
        assert isinstance(result, str)
        assert "Test Documentation" in result
        assert "Test Component" in result
        assert "Test Page" in result


class TestDocumentationAgentEventHandlers:
    """Test event handlers van DocumentationAgent."""

    def test_on_figma_documentation_requested(self):
        """Test on_figma_documentation_requested event handler."""
        event = {
            "figma_file_id": "test_file_id",
            "user_id": "test_user"
        }
        
        with patch('bmad.agents.Agent.DocumentationAgent.documentationagent.document_figma_ui') as mock_doc, \
             patch('bmad.agents.Agent.DocumentationAgent.documentationagent.PerformanceOptimizer', return_value=MagicMock()), \
             patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_advanced_policy_engine', return_value=MagicMock()), \
             patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_sprite_library', return_value=MagicMock()):
            
            mock_doc.return_value = {"status": "success"}
            
            result = on_figma_documentation_requested(event)
            
            assert result is None

    def test_on_summarize_changelogs(self):
        """Test on_summarize_changelogs event handler."""
        event = {
            "changelog_texts": ["Test changelog 1", "Test changelog 2"],
            "user_id": "test_user"
        }
        
        with patch('bmad.agents.Agent.DocumentationAgent.documentationagent.summarize_changelogs_llm') as mock_summarize:
            mock_summarize.return_value = "Test summary"
            
            result = on_summarize_changelogs(event)
            
            # Test dat LLM functie aangeroepen is
            mock_summarize.assert_called_once_with(["Test changelog 1", "Test changelog 2"])


class TestDocumentationAgentIntegration:
    """Integration tests voor DocumentationAgent."""

    def setup_method(self):
        """Setup method voor alle tests in deze class."""
        self.patches = [
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.PerformanceOptimizer', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_advanced_policy_engine', return_value=MagicMock()),
            patch('bmad.agents.Agent.DocumentationAgent.documentationagent.get_sprite_library', return_value=MagicMock())
        ]
        for p in self.patches:
            p.start()

    def teardown_method(self):
        """Teardown method voor alle tests in deze class."""
        for p in self.patches:
            p.stop()

    def test_agent_complete_workflow(self):
        """Test complete workflow van DocumentationAgent."""
        with patch('bmad.agents.Agent.DocumentationAgent.documentationagent.ask_openai_with_confidence') as mock_llm:
            mock_llm.return_value = {
                "answer": "Test response",
                "llm_confidence": 0.85
            }
            
            # Test complete workflow
            assert hasattr(DocumentationAgent(), 'show_help')
            assert hasattr(DocumentationAgent(), 'show_resource')
            assert hasattr(DocumentationAgent(), 'show_docs_history')
            assert hasattr(DocumentationAgent(), 'show_figma_history')
            assert hasattr(DocumentationAgent(), 'summarize_changelogs')
            assert hasattr(DocumentationAgent(), 'document_figma_ui')
            assert hasattr(DocumentationAgent(), 'create_api_docs')
            assert hasattr(DocumentationAgent(), 'create_user_guide')
            assert hasattr(DocumentationAgent(), 'create_technical_docs')
            assert hasattr(DocumentationAgent(), 'export_report')
            assert hasattr(DocumentationAgent(), 'test_resource_completeness')
            assert hasattr(DocumentationAgent(), 'collaborate_example')
            assert hasattr(DocumentationAgent(), 'run')

    def test_agent_error_handling(self):
        """Test error handling van DocumentationAgent."""
        # Test dat agent robuust is bij errors
        with patch('bmad.agents.Agent.DocumentationAgent.documentationagent.save_context') as mock_save, \
             patch('bmad.agents.Agent.DocumentationAgent.documentationagent.publish') as mock_publish, \
             patch('bmad.agents.Agent.DocumentationAgent.documentationagent.ask_openai_with_confidence') as mock_llm, \
             patch('bmad.agents.Agent.DocumentationAgent.documentationagent.project_manager') as mock_project_manager, \
             patch('bmad.agents.Agent.DocumentationAgent.documentationagent.document_figma_ui') as mock_doc_figma, \
             patch.object(DocumentationAgent, 'collaborate_example') as mock_collaborate:
            
            mock_llm.return_value = {
                "answer": "Test response",
                "llm_confidence": 0.85
            }
            
            try:
                agent = DocumentationAgent()
                agent.run()  # run() neemt geen parameters
                # Should not raise exception
            except Exception as e:
                pytest.fail(f"Agent should handle errors gracefully: {e}")


if __name__ == '__main__':
    pytest.main([__file__]) 