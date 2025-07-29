"""
CLI Utilities

Common utility functions for CLI tools.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, List


class CLIUtils:
    """Utility functions for CLI tools."""
    
    @staticmethod
    def load_config(config_file: str) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading config {config_file}: {e}")
            return {}

    @staticmethod
    def save_config(config: Dict[str, Any], config_file: str) -> bool:
        """Save configuration to file."""
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving config {config_file}: {e}")
            return False

    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Ensure directory exists."""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"❌ Error creating directory {path}: {e}")
            return False

    @staticmethod
    def check_environment_variable(var_name: str, required: bool = True) -> Optional[str]:
        """Check if environment variable is set."""
        value = os.getenv(var_name)
        if required and not value:
            print(f"❌ Required environment variable {var_name} is not set")
            return None
        return value

    @staticmethod
    def print_table(headers: List[str], rows: List[List[str]]):
        """Print data in table format."""
        if not rows:
            print("No data to display")
            return
            
        # Calculate column widths
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(header)
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width)
        
        # Print header
        header_line = " | ".join(header.ljust(width) for header, width in zip(headers, col_widths))
        print(header_line)
        print("-" * len(header_line))
        
        # Print rows
        for row in rows:
            row_line = " | ".join(str(cell).ljust(width) for cell, width in zip(row, col_widths))
            print(row_line)

    @staticmethod
    def confirm_action(message: str) -> bool:
        """Ask user to confirm an action."""
        response = input(f"{message} (y/N): ").strip().lower()
        return response in ['y', 'yes']

    @staticmethod
    def progress_bar(current: int, total: int, width: int = 50):
        """Display a progress bar."""
        progress = int(width * current / total)
        bar = "█" * progress + "░" * (width - progress)
        percentage = current / total * 100
        print(f"\r[{bar}] {percentage:.1f}% ({current}/{total})", end="", flush=True)
        if current == total:
            print()


# Legacy function exports for backward compatibility
def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from file."""
    return CLIUtils.load_config(config_file)


def save_config(config: Dict[str, Any], config_file: str) -> bool:
    """Save configuration to file."""
    return CLIUtils.save_config(config, config_file)


def ensure_directory(path: str) -> bool:
    """Ensure directory exists."""
    return CLIUtils.ensure_directory(path)


def check_environment_variable(var_name: str, required: bool = True) -> Optional[str]:
    """Check if environment variable is set."""
    return CLIUtils.check_environment_variable(var_name, required)


def print_table(headers: List[str], rows: List[List[str]]):
    """Print data in table format."""
    CLIUtils.print_table(headers, rows)


def confirm_action(message: str) -> bool:
    """Ask user to confirm an action."""
    return CLIUtils.confirm_action(message)


def progress_bar(current: int, total: int, width: int = 50):
    """Display a progress bar."""
    CLIUtils.progress_bar(current, total, width) 