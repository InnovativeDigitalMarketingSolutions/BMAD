"""
Base CLI Class

Provides common functionality for all BMAD CLI tools.
"""

import argparse
import logging
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseCLI(ABC):
    """Base class for all BMAD CLI tools."""
    
    def __init__(self, name: str, description: str):
        """Initialize base CLI."""
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"cli.{name.lower()}")
        
    @abstractmethod
    def setup_parser(self) -> argparse.ArgumentParser:
        """Setup argument parser for the CLI."""
        pass
        
    @abstractmethod
    def execute_command(self, args: argparse.Namespace) -> bool:
        """Execute the CLI command."""
        pass
        
    def run(self, argv: Optional[List[str]] = None) -> bool:
        """Run the CLI tool."""
        try:
            parser = self.setup_parser()
            args = parser.parse_args(argv)
            
            if hasattr(args, 'command') and args.command == 'help':
                parser.print_help()
                return True
                
            return self.execute_command(args)
            
        except Exception as e:
            self.logger.error(f"Error running {self.name}: {e}")
            return False
            
    def print_help(self):
        """Print help information."""
        parser = self.setup_parser()
        parser.print_help()
        
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)
        print(f"ℹ️  {message}")
        
    def log_success(self, message: str):
        """Log success message."""
        self.logger.info(message)
        print(f"✅ {message}")
        
    def log_error(self, message: str):
        """Log error message."""
        self.logger.error(message)
        print(f"❌ {message}")
        
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
        print(f"⚠️  {message}")


class CLIUtils:
    """Utility functions for CLI tools."""
    
    @staticmethod
    def create_subparser(parser: argparse.ArgumentParser, name: str, help_text: str) -> argparse.ArgumentParser:
        """Create a subparser for a command."""
        return parser.add_parser(name, help=help_text)
        
    @staticmethod
    def add_common_args(parser: argparse.ArgumentParser):
        """Add common arguments to a parser."""
        parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
        parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output")
        
    @staticmethod
    def format_output(data: Any, format_type: str = "text") -> str:
        """Format output data."""
        if format_type == "json":
            import json
            return json.dumps(data, indent=2)
        elif format_type == "yaml":
            import yaml
            return yaml.dump(data, default_flow_style=False)
        else:
            return str(data) 