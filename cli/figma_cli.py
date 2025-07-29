#!/usr/bin/env python3
"""
Figma CLI Tool - Generate components and documentation from Figma designs.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Figma client
from integrations.figma.figma_client import FigmaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FigmaCLI:
    """Figma CLI class for BMAD Figma integration."""
    
    def __init__(self):
        """Initialize Figma CLI."""
        self.client = None
        
    def test_connection(self, file_id: str) -> bool:
        """Test Figma API connection."""
        return test_figma_connection(file_id)
    
    def generate_components(self, file_id: str, output_dir: str = "components") -> bool:
        """Generate Next.js components from Figma file."""
        return generate_components(file_id, output_dir)
    
    def analyze_design(self, file_id: str) -> bool:
        """Analyze Figma design."""
        return analyze_design(file_id)
    
    def generate_documentation(self, file_id: str, output_file: str = None) -> bool:
        """Generate documentation for Figma file."""
        return generate_documentation(file_id, output_file)
    
    def start_monitoring(self, file_id: str) -> bool:
        """Start monitoring Figma file for changes."""
        return start_monitoring(file_id)
    
    def show_help(self):
        """Show help information."""
        print_help()


def print_help():
    """Print help information."""
    help_text = """
BMAD Figma CLI - Figma Integration
==================================

Beschikbare commando's:
  test <file_id>              - Test Figma API connection
  components <file_id>         - Generate Next.js components
  analyze <file_id>            - Analyze Figma design
  document <file_id>           - Generate documentation
  monitor <file_id>            - Start monitoring for changes
  help                         - Toon deze help

Opties:
  --output, -o                 - Output file or directory
  --format, -f                 - Output format (json, markdown, html)

Voorbeelden:
  python figma_cli.py test "abc123def456"
  python figma_cli.py components "abc123def456" --output "src/components"
  python figma_cli.py analyze "abc123def456"
  python figma_cli.py document "abc123def456" --output "figma-docs.md"
  python figma_cli.py monitor "abc123def456"
        """
    print(help_text)


def test_figma_connection(file_id: str):
    """Test Figma API connection."""
    try:
        print(f"🔗 Testing Figma API connection for file: {file_id}")

        client = FigmaClient()

        # Test file info
        print("📄 Fetching file info...")
        file_data = client.get_file(file_id)
        print(f"✅ File: {file_data.get('name', 'Unknown')}")
        print(f"   Version: {file_data.get('version', 'Unknown')}")
        print(f"   Last modified: {file_data.get('lastModified', 'Unknown')}")

        # Test components
        print("🧩 Fetching components...")
        components_data = client.get_components(file_id)
        components_count = len(components_data.get("meta", {}).get("components", {}))
        print(f"✅ Found {components_count} components")

        # Test comments
        print("💬 Fetching comments...")
        comments_data = client.get_comments(file_id)
        comments_count = len(comments_data.get("comments", []))
        print(f"✅ Found {comments_count} comments")

        print("🎉 Figma API connection successful!")
        return True

    except Exception as e:
        print(f"❌ Figma API connection failed: {e}")
        return False


def generate_components(file_id: str, output_dir: str = "components"):
    """Generate Next.js components from Figma file."""
    try:
        print(f"⚡ Generating Next.js components from Figma file: {file_id}")

        client = FigmaClient()
        
        # Get file data
        file_data = client.get_file(file_id)
        file_name = file_data.get("name", "Unknown")
        
        # Get components
        components_data = client.get_components(file_id)
        components = components_data.get("meta", {}).get("components", {})
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Output directory: {output_path.absolute()}")
        print(f"🧩 Found {len(components)} components")
        
        # Generate component files
        generated_count = 0
        for component_id, component_info in components.items():
            component_name = component_info.get("name", f"Component_{component_id}")
            
            # Generate component file
            component_file = output_path / f"{component_name}.tsx"
            
            # Create basic Next.js component
            component_code = '''import React from 'react';

interface ''' + component_name + '''Props {
  // Add your props here
}

export const ''' + component_name + ''': React.FC<''' + component_name + '''Props> = ({ }) => {
  return (
    <div className="''' + component_name.lower() + '''-component">
      {/* Component */}
      <p>Generated from Figma component: ''' + component_name + '''</p>
    </div>
  );
};

export default ''' + component_name + ''';
'''
            
            with open(component_file, "w", encoding="utf-8") as f:
                f.write(component_code)
            
            generated_count += 1
            print(f"✅ Generated: {component_file.name}")
        
        print(f"🎉 Successfully generated {generated_count} components!")
        return True

    except Exception as e:
        print(f"❌ Error generating components: {e}")
        return False


def analyze_design(file_id: str):
    """Analyze Figma design for UX/UI insights."""
    try:
        print(f"🔍 Analyzing Figma design: {file_id}")

        client = FigmaClient()
        
        # Get file data
        file_data = client.get_file(file_id)
        file_name = file_data.get("name", "Unknown")
        
        # Get components
        components_data = client.get_components(file_id)
        components = components_data.get("meta", {}).get("components", {})
        
        # Get comments
        comments_data = client.get_comments(file_id)
        comments = comments_data.get("comments", [])
        
        print(f"📄 File: {file_name}")
        print(f"🧩 Components: {len(components)}")
        print(f"💬 Comments: {len(comments)}")
        
        # Analyze components
        print("\n📊 Component Analysis:")
        component_types = {}
        for component_id, component_info in components.items():
            component_name = component_info.get("name", "Unknown")
            component_type = component_info.get("componentSetId", "Individual")
            
            if component_type not in component_types:
                component_types[component_type] = []
            component_types[component_type].append(component_name)
        
        for component_type, names in component_types.items():
            print(f"   {component_type}: {len(names)} components")
        
        # Analyze comments
        if comments:
            print("\n💬 Comment Analysis:")
            comment_types = {}
            for comment in comments:
                message = comment.get("message", "").lower()
                if "bug" in message or "error" in message:
                    comment_types["bugs"] = comment_types.get("bugs", 0) + 1
                elif "design" in message or "ui" in message or "ux" in message:
                    comment_types["design"] = comment_types.get("design", 0) + 1
                elif "feature" in message or "request" in message:
                    comment_types["features"] = comment_types.get("features", 0) + 1
                else:
                    comment_types["general"] = comment_types.get("general", 0) + 1
            
            for comment_type, count in comment_types.items():
                print(f"   {comment_type.capitalize()}: {count} comments")
        
        print("\n✅ Design analysis completed!")
        return True

    except Exception as e:
        print(f"❌ Error analyzing design: {e}")
        return False


def generate_documentation(file_id: str, output_file: str = None):
    """Generate documentation for Figma file."""
    try:
        print(f"📝 Generating documentation for Figma file: {file_id}")

        client = FigmaClient()
        
        # Get file data
        file_data = client.get_file(file_id)
        file_name = file_data.get("name", "Unknown")
        
        # Get components
        components_data = client.get_components(file_id)
        components = components_data.get("meta", {}).get("components", {})
        
        # Generate documentation
        doc_content = f"""# Figma Design Documentation

## File Information
- **File Name**: {file_name}
- **File ID**: {file_id}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Components ({len(components)})

"""
        
        for component_id, component_info in components.items():
            component_name = component_info.get("name", "Unknown")
            component_description = component_info.get("description", "No description available")
            
            doc_content += f"""### {component_name}

**ID**: `{component_id}`

**Description**: {component_description}

---

"""
        
        # Save documentation
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(doc_content)
            print(f"📁 Documentation saved to: {output_file}")
        else:
            print("\n" + doc_content)
        
        print("✅ Documentation generated successfully!")
        return True

    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        return False


def start_monitoring(file_id: str):
    """Start monitoring Figma file for changes."""
    try:
        print(f"👀 Starting monitoring for Figma file: {file_id}")
        print("🚧 This function is a placeholder. Actual monitoring would go here.")
        print("   To implement this, you would need to:")
        print("   1. Set up webhook or polling mechanism.")
        print("   2. Detect file changes and version updates.")
        print("   3. Trigger automatic component regeneration.")
        print("   4. Send notifications for design updates.")
        print("   5. Maintain change history and versioning.")
        
        return True

    except Exception as e:
        print(f"❌ Error starting monitoring: {e}")
        return False


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="BMAD Figma CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Voorbeelden:
  python figma_cli.py test <file_id>
  python figma_cli.py components <file_id>
  python figma_cli.py analyze <file_id>
  python figma_cli.py document <file_id>
  python figma_cli.py monitor <file_id>
        """
    )

    parser.add_argument(
        "command",
        choices=["test", "components", "analyze", "document", "monitor", "help"],
        help="Het commando om uit te voeren"
    )

    parser.add_argument(
        "file_id",
        nargs="?",
        help="Figma file ID"
    )

    parser.add_argument(
        "--output",
        help="Output file or directory"
    )

    args = parser.parse_args()

    # Check environment
    if not os.getenv("FIGMA_API_TOKEN"):
        print("❌ FIGMA_API_TOKEN niet gevonden in environment")
        print("Zorg dat je .env file geladen is: source .env")
        return False

    # Execute command
    if args.command == "help":
        print_help()
        return True
    elif args.command == "test":
        if not args.file_id:
            print("❌ File ID required for test command")
            return False
        return test_figma_connection(args.file_id)
    elif args.command == "components":
        if not args.file_id:
            print("❌ File ID required for components command")
            return False
        return generate_components(args.file_id, args.output or "components")
    elif args.command == "analyze":
        if not args.file_id:
            print("❌ File ID required for analyze command")
            return False
        return analyze_design(args.file_id)
    elif args.command == "document":
        if not args.file_id:
            print("❌ File ID required for document command")
            return False
        return generate_documentation(args.file_id, args.output)
    elif args.command == "monitor":
        if not args.file_id:
            print("❌ File ID required for monitor command")
            return False
        return start_monitoring(args.file_id)
    else:
        print(f"❌ Onbekend commando: {args.command}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
