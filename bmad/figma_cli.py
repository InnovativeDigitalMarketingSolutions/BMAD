#!/usr/bin/env python3
"""
BMAD Figma CLI Tool
===================

Een command-line interface voor het gebruiken van de Figma API integratie.

Gebruik:
    python figma_cli.py <command> [options]

Commands:
    components <file_id>     - Genereer Next.js componenten uit Figma file
    analyze <file_id>        - Analyseer Figma design (layout, kleuren, accessibility)
    document <file_id>       - Genereer documentatie voor Figma file
    monitor <file_id>        - Start monitoring van Figma file voor wijzigingen
    test <file_id>           - Test Figma API verbinding
    help                     - Toon deze help
"""

import sys
import json
import logging
from typing import Dict, Any
from agents.core.figma_client import FigmaClient
from agents.Agent.FrontendDeveloper.frontenddeveloper import generate_components_from_figma
from agents.Agent.UXUIDesigner.uxuidesigner import analyze_figma_design
from agents.Agent.DocumentationAgent.documentationagent import document_figma_ui

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def print_help():
    """Print help informatie."""
    print(__doc__)

def test_figma_connection(file_id: str):
    """Test Figma API verbinding."""
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
        components_count = len(components_data.get('meta', {}).get('components', {}))
        print(f"✅ Found {components_count} components")
        
        # Test comments
        print("💬 Fetching comments...")
        comments_data = client.get_comments(file_id)
        comments_count = len(comments_data.get('comments', []))
        print(f"✅ Found {comments_count} comments")
        
        print("🎉 Figma API connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Figma API connection failed: {str(e)}")
        return False

def generate_components(file_id: str, output_dir: str = "components"):
    """Genereer Next.js componenten uit Figma file."""
    try:
        print(f"⚡ Generating Next.js components from Figma file: {file_id}")
        
        result = generate_components_from_figma(file_id, output_dir)
        
        if 'error' in result:
            print(f"❌ Error generating components: {result['error']}")
            return False
        
        print(f"✅ Successfully generated {result['total_generated']} components")
        print(f"📁 Output directory: {output_dir}")
        
        # Toon gegenereerde componenten
        for component in result['generated_components']:
            print(f"   • {component['name']} -> {component['file_path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating components: {str(e)}")
        return False

def analyze_design(file_id: str):
    """Analyseer Figma design."""
    try:
        print(f"🔍 Analyzing Figma design: {file_id}")
        
        result = analyze_figma_design(file_id)
        
        if 'error' in result:
            print(f"❌ Error analyzing design: {result['error']}")
            return False
        
        print(f"✅ Analysis completed for: {result['file_name']}")
        print(f"📊 Results:")
        print(f"   • Pages: {result['total_pages']}")
        print(f"   • Colors: {len(result['color_analysis'].get('color_frequency', {}))}")
        print(f"   • Layout depth: {result['layout_analysis'].get('nested_depth', 0)}")
        print(f"   • Accessibility issues: {len(result['accessibility_issues'])}")
        
        # Toon accessibility issues
        if result['accessibility_issues']:
            print("\n⚠️  Accessibility Issues:")
            for issue in result['accessibility_issues'][:5]:  # Max 5 issues
                print(f"   • {issue['message']} (severity: {issue['severity']})")
        
        # Toon top kleuren
        if result['color_analysis'].get('primary_colors'):
            print("\n🎨 Top Colors:")
            for color, count in result['color_analysis']['primary_colors'][:3]:
                print(f"   • {color} (used {count} times)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing design: {str(e)}")
        return False

def generate_documentation(file_id: str, output_file: str = None):
    """Genereer documentatie voor Figma file."""
    try:
        print(f"📝 Generating documentation for Figma file: {file_id}")
        
        result = document_figma_ui(file_id)
        
        if 'error' in result:
            print(f"❌ Error generating documentation: {result['error']}")
            return False
        
        print(f"✅ Documentation generated for: {result['documentation']['file_name']}")
        print(f"📊 Summary:")
        print(f"   • Components: {result['total_components']}")
        print(f"   • Pages: {result['total_pages']}")
        print(f"   • Colors: {len(result['documentation']['design_system'].get('colors', []))}")
        print(f"   • Typography: {len(result['documentation']['design_system'].get('typography', []))}")
        
        # Sla markdown op als bestand
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['markdown'])
            print(f"📄 Documentation saved to: {output_file}")
        else:
            # Toon markdown in console
            print("\n" + "="*50)
            print("DOCUMENTATION PREVIEW")
            print("="*50)
            print(result['markdown'][:1000] + "..." if len(result['markdown']) > 1000 else result['markdown'])
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating documentation: {str(e)}")
        return False

def start_monitoring(file_id: str):
    """Start monitoring van Figma file."""
    try:
        print(f"👀 Starting monitoring for Figma file: {file_id}")
        print("Press Ctrl+C to stop monitoring...")
        
        from bmad.agents.core.figma_slack_notifier import FigmaSlackNotifier
        
        notifier = FigmaSlackNotifier()
        
        # Test initial connection
        if not test_figma_connection(file_id):
            return False
        
        # Start monitoring loop
        while True:
            try:
                notifier._check_file_updates(file_id)
                notifier._check_new_comments(file_id)
                print("✅ Monitoring check completed")
                
                import time
                time.sleep(60)  # Check elke minuut
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped")
                break
            except Exception as e:
                print(f"⚠️  Monitoring error: {str(e)}")
                time.sleep(30)
        
        return True
        
    except Exception as e:
        print(f"❌ Error starting monitoring: {str(e)}")
        return False

def main():
    """Hoofdfunctie voor CLI."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help":
        print_help()
        return
    
    if command == "test":
        if len(sys.argv) < 3:
            print("❌ Please provide a file ID: python figma_cli.py test <file_id>")
            return
        file_id = sys.argv[2]
        test_figma_connection(file_id)
        return
    
    if command == "components":
        if len(sys.argv) < 3:
            print("❌ Please provide a file ID: python figma_cli.py components <file_id> [output_dir]")
            return
        file_id = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else "components"
        generate_components(file_id, output_dir)
        return
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print("❌ Please provide a file ID: python figma_cli.py analyze <file_id>")
            return
        file_id = sys.argv[2]
        analyze_design(file_id)
        return
    
    if command == "document":
        if len(sys.argv) < 3:
            print("❌ Please provide a file ID: python figma_cli.py document <file_id> [output_file]")
            return
        file_id = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        generate_documentation(file_id, output_file)
        return
    
    if command == "monitor":
        if len(sys.argv) < 3:
            print("❌ Please provide a file ID: python figma_cli.py monitor <file_id>")
            return
        file_id = sys.argv[2]
        start_monitoring(file_id)
        return
    
    print(f"❌ Unknown command: {command}")
    print_help()

if __name__ == "__main__":
    main() 