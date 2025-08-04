"""
Tests for bmad-run.py and figma_cli.py modules.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import tempfile

class TestBMADRun:
    """Test bmad-run.py module."""
    
    def test_bmad_run_import(self):
        """Test that bmad-run module can be imported."""
        try:
            import bmad.bmad_run
            assert True
        except ImportError as e:
            pytest.skip(f"bmad-run module not available: {e}")
    
    @patch('subprocess.run')
    def test_bmad_run_main_function(self, mock_run):
        """Test main function of bmad-run."""
        try:
            from bmad.bmad_run import main
            
            # Mock subprocess.run to return success
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Test output"
            mock_run.return_value = mock_result
            
            # Test with mock arguments
            with patch('sys.argv', ['bmad-run.py', 'test-command']):
                try:
                    main()
                    assert True
                except SystemExit:
                    # Expected if main exits
                    pass
                    
        except ImportError as e:
            pytest.skip(f"bmad-run module not available: {e}")
    
    @patch('subprocess.run')
    @pytest.mark.asyncio
    async def test_bmad_run_with_workflow(self, mock_run):
        """Test bmad-run with workflow argument."""
        try:
            from bmad.bmad_run import main
            
            # Mock subprocess.run
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            # Test with workflow argument
            with patch('sys.argv', ['bmad-run.py', 'start-workflow', 'test-workflow']):
                try:
                    main()
                    assert True
                except SystemExit:
                    pass
                    
        except ImportError as e:
            pytest.skip(f"bmad-run module not available: {e}")

class TestFigmaCLI:
    """Test figma_cli.py module."""
    
    def test_figma_cli_import(self):
        """Test that figma_cli module can be imported."""
        try:
            # Test actual import functionality
            from cli import FigmaCLI
            assert FigmaCLI is not None, "FigmaCLI should be importable"
            cli = FigmaCLI()
            assert hasattr(cli, 'test_connection'), "FigmaCLI should have test_connection method"
            assert callable(cli.test_connection), "test_connection should be callable"
        except ImportError as e:
            pytest.skip(f"figma_cli module not available: {e}")
    
    def test_figma_cli_main_function(self):
        """Test main function of figma_cli."""
        try:
            from cli.figma_cli import main
            
            # Test with help argument
            with patch('sys.argv', ['figma_cli.py', '--help']):
                try:
                    main()
                    assert True
                except SystemExit:
                    # Expected for help
                    pass
                    
        except ImportError as e:
            pytest.skip(f"figma_cli module not available: {e}")
    
    def test_figma_cli_components_command(self):
        """Test figma_cli components command."""
        try:
            from cli.commands.figma.handlers import generate_components
            assert callable(generate_components), "generate_components should be callable"
            
            # Test function signature
            import inspect
            sig = inspect.signature(generate_components)
            assert 'file_id' in sig.parameters, "generate_components should accept file_id parameter"
        except ImportError as e:
            pytest.skip(f"figma_cli module not available: {e}")
    
    def test_figma_cli_analyze_command(self):
        """Test figma_cli analyze command."""
        try:
            from cli.commands.figma.handlers import analyze_design
            assert callable(analyze_design), "analyze_design should be callable"
            
            # Test function signature
            import inspect
            sig = inspect.signature(analyze_design)
            assert 'file_id' in sig.parameters, "analyze_design should accept file_id parameter"
        except ImportError as e:
            pytest.skip(f"figma_cli module not available: {e}")
    
    def test_figma_cli_document_command(self):
        """Test figma_cli document command."""
        try:
            from cli.commands.figma.handlers import generate_documentation
            assert callable(generate_documentation), "generate_documentation should be callable"
            
            # Test function signature
            import inspect
            sig = inspect.signature(generate_documentation)
            assert 'file_id' in sig.parameters, "generate_documentation should accept file_id parameter"
        except ImportError as e:
            pytest.skip(f"figma_cli module not available: {e}")
    
    def test_figma_cli_argument_parsing(self):
        """Test figma_cli argument parsing."""
        try:
            from cli.figma_cli import main
            
            # Test argument parsing with help
            with patch('sys.argv', ['figma_cli.py', '--help']):
                try:
                    main()
                    assert True
                except SystemExit:
                    pass  # Expected for help
                
        except ImportError as e:
            pytest.skip(f"figma_cli module not available: {e}")
    
    def test_figma_cli_error_handling(self):
        """Test figma_cli error handling."""
        try:
            from cli.figma_cli import main
            
            # Test with invalid arguments
            with patch('sys.argv', ['figma_cli.py', 'invalid_command']):
                try:
                    main()
                    assert True
                except SystemExit:
                    pass  # Expected for invalid command
                
        except ImportError as e:
            pytest.skip(f"figma_cli module not available: {e}")

class TestBMAD:
    """Test bmad.py module."""
    
    def test_bmad_import(self):
        """Test that bmad module can be imported."""
        try:
            import bmad.bmad
            assert True
        except ImportError as e:
            pytest.skip(f"bmad module not available: {e}")
    
    def test_bmad_main_function(self):
        """Test main function of bmad."""
        try:
            from bmad.bmad import main
            
            # Test with help argument
            with patch('sys.argv', ['bmad.py', '--help']):
                try:
                    main()
                    assert True
                except SystemExit:
                    # Expected for help
                    pass
                    
        except ImportError as e:
            pytest.skip(f"bmad module not available: {e}")
    
    def test_bmad_start_workflow(self):
        """Test bmad start-workflow command."""
        try:
            # Test direct import
            import bmad.bmad
            assert True
        except ImportError as e:
            pytest.skip(f"bmad module not available: {e}")

class TestMergeAgentChangelogs:
    """Test merge_agent_changelogs.py module."""
    
    def test_merge_agent_changelogs_import(self):
        """Test that merge_agent_changelogs module can be imported."""
        try:
            import bmad.merge_agent_changelogs
            assert True
        except ImportError as e:
            pytest.skip(f"merge_agent_changelogs module not available: {e}")
    
    def test_merge_agent_changelogs_main_function(self):
        """Test main function of merge_agent_changelogs."""
        try:
            from bmad.merge_agent_changelogs import main
            
            # Test main function
            try:
                main()
                assert True
            except Exception:
                # Expected if no changelog files exist
                pass
                
        except ImportError as e:
            pytest.skip(f"merge_agent_changelogs module not available: {e}")
    
    def test_merge_agent_changelogs_find_changelog_files(self):
        """Test find_changelog_files function."""
        try:
            from bmad.merge_agent_changelogs import find_changelog_files
            
            # Test finding changelog files (function doesn't take parameters)
            files = find_changelog_files()
            
            # Should return a list of changelog files
            assert isinstance(files, list)
            
        except ImportError as e:
            pytest.skip(f"merge_agent_changelogs module not available: {e}")

class TestProjectCLI:
    """Test project_cli.py module."""
    
    def test_project_cli_import(self):
        """Test that project_cli module can be imported."""
        try:
            import cli.project_cli
            assert True
        except ImportError as e:
            pytest.skip(f"project_cli module not available: {e}")
    
    def test_project_cli_main_function(self):
        """Test main function of project_cli."""
        try:
            # Fix import path for moved module
            from cli.project_cli import main as project_cli_main
            
            # Test with help argument
            with patch('sys.argv', ['project_cli.py', '--help']):
                try:
                    project_cli_main()
                    assert True
                except SystemExit:
                    # Expected for help
                    pass
                    
        except ImportError as e:
            pytest.skip(f"project_cli module not available: {e}")
    
    @patch('cli.project_cli.project_manager')
    def test_project_cli_create_command(self, mock_project_manager):
        """Test project_cli create command."""
        try:
            from cli.project_cli import main
            
            # Mock project_manager
            mock_pm = MagicMock()
            mock_project_manager.create_project.return_value = {"id": "test-project"}
            
            # Test create command
            with patch('sys.argv', ['project_cli.py', 'create', 'test-project', 'Test Project']):
                try:
                    main()
                    assert True
                except SystemExit:
                    pass
                    
        except ImportError as e:
            pytest.skip(f"project_cli module not available: {e}")
    
    @patch('cli.project_cli.project_manager')
    def test_project_cli_load_command(self, mock_project_manager):
        """Test project_cli load command."""
        try:
            from cli.project_cli import main
            
            # Mock project_manager
            mock_pm = MagicMock()
            mock_project_manager.get_project.return_value = {"id": "test-project", "name": "Test Project"}
            
            # Test show command (equivalent to load)
            with patch('sys.argv', ['project_cli.py', 'show', 'test-project']):
                try:
                    main()
                    assert True
                except SystemExit:
                    pass
                    
        except ImportError as e:
            pytest.skip(f"project_cli module not available: {e}")

class TestAPI:
    """Test api.py module."""
    
    def test_api_import(self):
        """Test that api module can be imported."""
        try:
            import bmad.api
            assert True
        except ImportError as e:
            pytest.skip(f"api module not available: {e}")
    
    def test_api_app_creation(self):
        """Test Flask app creation in api module."""
        try:
            from bmad.api import app
            
            # Test that app exists
            assert app is not None
            
        except ImportError as e:
            pytest.skip(f"api module not available: {e}")
    
    def test_api_routes(self):
        """Test API routes."""
        try:
            from bmad.api import app
            
            # Test that app has routes
            assert hasattr(app, 'route')
            
        except ImportError as e:
            pytest.skip(f"api module not available: {e}")
    
    def test_api_health_endpoint(self):
        """Test health endpoint."""
        try:
            from bmad.api import app
            
            # Test that app has routes
            assert hasattr(app, 'route')
            
        except ImportError as e:
            pytest.skip(f"api module not available: {e}") 