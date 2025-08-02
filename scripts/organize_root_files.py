#!/usr/bin/env python3
"""
Script om files in de root folder te organiseren in de juiste mappen
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def organize_root_files():
    """Organiseer files in de root folder."""
    print("🗂️ Organizing Root Folder Files")
    print("=" * 50)
    
    # Define file organization rules
    file_organization = {
        # Test files
        "test_*.py": "tests/",
        "test_*_framework_templates.py": "tests/",
        "test_*_templates.py": "tests/",
        "test_*_simple.py": "tests/",
        "test_*_only.py": "tests/",
        "test_*_services.py": "tests/",
        "test_*_microservices.py": "tests/",
        "test_*_database_setup.py": "tests/",
        "test_*_auth_service.py": "tests/",
        "test_*_individual_services.py": "tests/",
        "simple_*_test.py": "tests/",
        "verify_*.py": "tests/",
        "setup_*.py": "tests/",
        
        # Database files
        "DATABASE_SETUP_README.md": "docs/status/",
        "database_setup_complete.sql": "docs/status/",
        "SUPABASE_SETUP_STATUS.md": "docs/status/",
        
        # Report files
        "*_report_*.md": "docs/reports/temporary/",
        "*_report_*.json": "docs/reports/temporary/",
        "*_report_*.csv": "docs/reports/temporary/",
        
        # Configuration files
        "docker-compose.yml": "microservices/",
        "microservices_env_template.env": "microservices/",
        "start_bmad.sh": "scripts/",
        "bmad_clickup_workflow.py": "integrations/clickup/",
        "clickup_id_finder.py": "integrations/clickup/",
        "implement_clickup_template.py": "integrations/clickup/",
        "setup_clickup.py": "integrations/clickup/",
        
        # Log files
        "bmad.log": "logs/",
        "event_log.json": "logs/",
        "performance_test_results.json": "logs/",
        "security-*.json": "logs/",
        "metrics.json": "logs/",
        "TestApp_config_*.json": "logs/",
        
        # Coverage files
        ".coverage": "tests/coverage/",
        "quality_report_*.md": "tests/coverage/",
        
        # Temporary files
        "uxui_report_*.json": "docs/reports/temporary/",
        "uxui_report_*.md": "docs/reports/temporary/",
        "rnd_report_*.json": "docs/reports/temporary/",
        "rnd_report_*.csv": "docs/reports/temporary/",
        "rnd_report_*.md": "docs/reports/temporary/",
        "retrospective_report_*.json": "docs/reports/temporary/",
        "retrospective_report_*.csv": "docs/reports/temporary/",
        "retrospective_report_*.md": "docs/reports/temporary/",
        "release_report_*.json": "docs/reports/temporary/",
        "release_report_*.csv": "docs/reports/temporary/",
        "release_report_*.md": "docs/reports/temporary/",
        "feedback_report_*.json": "docs/reports/temporary/",
        "feedback_report_*.csv": "docs/reports/temporary/",
        "feedback_report_*.md": "docs/reports/temporary/",
        "documentation_report_*.json": "docs/reports/temporary/",
        "documentation_report_*.csv": "docs/reports/temporary/",
        "documentation_report_*.md": "docs/reports/temporary/",
        "infrastructure_report_*.json": "docs/reports/temporary/",
        "infrastructure_report_*.csv": "docs/reports/temporary/",
        "infrastructure_report_*.md": "docs/reports/temporary/",
        "data_pipeline_report_*.json": "docs/reports/temporary/",
        "data_pipeline_report_*.csv": "docs/reports/temporary/",
        "data_pipeline_report_*.md": "docs/reports/temporary/",
        "mobile_development_report_*.json": "docs/reports/temporary/",
        "mobile_development_report_*.csv": "docs/reports/temporary/",
        "mobile_development_report_*.md": "docs/reports/temporary/",
        "orchestration_report_*.json": "docs/reports/temporary/",
        
        # Utility files
        "health_check.py": "scripts/",
        "update_agents_with_framework_templates.py": "scripts/",
        "organize_root_files.py": "scripts/"
    }
    
    # Files die in root moeten blijven
    keep_in_root = [
        "README.md",
        ".gitignore",
        ".flake8",
        "pytest.ini",
        "pyproject.toml",
        "docker-compose.yml"  # Keep main docker-compose in root
    ]
    
    moved_files = []
    failed_files = []
    
    # Create necessary directories
    directories_to_create = [
        "tests/coverage",
        "docs/reports/temporary", 
        "scripts",
        "logs",
        "microservices"
    ]
    
    for directory in directories_to_create:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Process files in root
    root_path = Path(".")
    
    for file_path in root_path.iterdir():
        if file_path.is_file() and file_path.name not in keep_in_root:
            file_moved = False
            
            # Check against organization rules
            for pattern, destination in file_organization.items():
                if file_path.match(pattern):
                    try:
                        dest_path = Path(destination) / file_path.name
                        
                        # Handle duplicates
                        if dest_path.exists():
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            name_parts = file_path.stem, timestamp, file_path.suffix
                            new_name = f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                            dest_path = Path(destination) / new_name
                        
                        shutil.move(str(file_path), str(dest_path))
                        moved_files.append((file_path.name, destination))
                        print(f"  ✅ Moved {file_path.name} → {destination}")
                        file_moved = True
                        break
                        
                    except Exception as e:
                        failed_files.append((file_path.name, str(e)))
                        print(f"  ❌ Failed to move {file_path.name}: {e}")
                        break
            
            # If no pattern matched, move to temporary
            if not file_moved and file_path.suffix in ['.py', '.md', '.json', '.csv']:
                try:
                    dest_path = Path("docs/reports/temporary") / file_path.name
                    
                    if dest_path.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        name_parts = file_path.stem, timestamp, file_path.suffix
                        new_name = f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                        dest_path = Path("docs/reports/temporary") / new_name
                    
                    shutil.move(str(file_path), str(dest_path))
                    moved_files.append((file_path.name, "docs/reports/temporary"))
                    print(f"  ✅ Moved {file_path.name} → docs/reports/temporary")
                    
                except Exception as e:
                    failed_files.append((file_path.name, str(e)))
                    print(f"  ❌ Failed to move {file_path.name}: {e}")
    
    # Summary
    print(f"\n📋 Organization Summary:")
    print("=" * 30)
    print(f"  ✅ Successfully moved: {len(moved_files)} files")
    print(f"  ❌ Failed to move: {len(failed_files)} files")
    
    if moved_files:
        print(f"\n✅ Moved Files:")
        for file_name, destination in moved_files:
            print(f"  • {file_name} → {destination}")
    
    if failed_files:
        print(f"\n❌ Failed Files:")
        for file_name, error in failed_files:
            print(f"  • {file_name}: {error}")
    
    return len(failed_files) == 0

def main():
    """Main function."""
    success = organize_root_files()
    
    if success:
        print(f"\n🎉 Root folder organization completed successfully!")
    else:
        print(f"\n⚠️  Root folder organization completed with some errors.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 