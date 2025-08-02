#!/usr/bin/env python3
"""
Script om alle agents te updaten met framework templates integratie
"""

import os
from pathlib import Path

def get_agent_template_mapping():
    """Get mapping van agents naar hun templates."""
    return {
        "BackendDeveloper": "backend_development",
        "FrontendDeveloper": "frontend_development", 
        "FullstackDeveloper": "fullstack_development",
        "TestEngineer": "testing_engineer",
        "QualityGuardian": "quality_guardian",
        "DataEngineer": "data_engineer",
        "RnD": "rnd",
        "ProductOwner": "product_owner",
        "Scrummaster": "scrummaster",
        "ReleaseManager": "release_manager"
    }

def update_agent_with_framework_template(agent_name, template_name):
    """Update een agent met framework template integratie."""
    agent_path = Path(f"bmad/agents/Agent/{agent_name}")
    
    if not agent_path.exists():
        print(f"  ⚠️  Agent path not found: {agent_path}")
        return False
    
    # Zoek naar Python files in de agent directory
    python_files = list(agent_path.glob("*.py"))
    
    if not python_files:
        print(f"  ⚠️  No Python files found in {agent_path}")
        return False
    
    updated = False
    for py_file in python_files:
        if update_python_file_with_template(py_file, agent_name, template_name):
            updated = True
    
    return updated

def update_python_file_with_template(py_file, agent_name, template_name):
    """Update een Python file met framework template integratie."""
    try:
        content = py_file.read_text(encoding='utf-8')
        
        # Check of framework templates al geïntegreerd zijn
        if "get_framework_templates_manager" in content:
            print(f"    ✅ {py_file.name}: Already has framework templates integration")
            return False
        
        # Voeg imports toe
        if "from bmad.agents.core.utils.framework_templates import" not in content:
            import_line = "from bmad.agents.core.utils.framework_templates import get_framework_templates_manager\n"
            
            # Zoek naar bestaande imports
            lines = content.split('\n')
            import_index = -1
            
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_index = i
            
            if import_index >= 0:
                lines.insert(import_index + 1, import_line)
            else:
                lines.insert(0, import_line)
            
            content = '\n'.join(lines)
        
        # Voeg framework manager toe aan __init__
        if "__init__" in content and "self.framework_manager" not in content:
            # Zoek naar __init__ method
            init_pattern = "def __init__"
            if init_pattern in content:
                # Voeg framework manager toe na self initialization
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if init_pattern in line:
                        # Zoek naar einde van __init__ method
                        indent = len(line) - len(line.lstrip())
                        init_indent = indent
                        
                        # Voeg framework manager toe na self initialization
                        framework_line = " " * (indent + 4) + f"self.framework_manager = get_framework_templates_manager()\n"
                        framework_line += " " * (indent + 4) + f"self.{template_name}_template = self.framework_manager.get_template('{template_name}')\n"
                        framework_line += " " * (indent + 4) + "self.lessons_learned = []\n"
                        
                        # Voeg toe na self initialization
                        insert_index = i + 1
                        while insert_index < len(lines) and lines[insert_index].strip() and not lines[insert_index].startswith(" " * (indent + 4)):
                            insert_index += 1
                        
                        lines.insert(insert_index, framework_line)
                        content = '\n'.join(lines)
                        break
        
        # Schrijf updated content terug
        py_file.write_text(content, encoding='utf-8')
        print(f"    ✅ {py_file.name}: Updated with framework templates integration")
        return True
        
    except Exception as e:
        print(f"    ❌ {py_file.name}: Error updating - {e}")
        return False

def main():
    """Main function om alle agents te updaten."""
    print("🔄 Updating Agents with Framework Templates Integration")
    print("=" * 60)
    
    agent_template_mapping = get_agent_template_mapping()
    
    updated_agents = []
    failed_agents = []
    
    for agent_name, template_name in agent_template_mapping.items():
        print(f"\n🔧 Updating {agent_name} with {template_name} template:")
        
        if update_agent_with_framework_template(agent_name, template_name):
            updated_agents.append(agent_name)
        else:
            failed_agents.append(agent_name)
    
    # Summary
    print(f"\n📋 Update Summary:")
    print("=" * 30)
    print(f"  ✅ Successfully updated: {len(updated_agents)} agents")
    print(f"  ❌ Failed to update: {len(failed_agents)} agents")
    
    if updated_agents:
        print(f"\n✅ Updated Agents:")
        for agent in updated_agents:
            print(f"  • {agent}")
    
    if failed_agents:
        print(f"\n❌ Failed Agents:")
        for agent in failed_agents:
            print(f"  • {agent}")
    
    return len(failed_agents) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 