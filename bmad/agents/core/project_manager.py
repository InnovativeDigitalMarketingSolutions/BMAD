"""
BMAD Project Manager

Dit module beheert multi-project configuratie en scoping voor ClickUp integratie.
Het zorgt voor project isolatie en dynamische configuratie.
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from .supabase_context import save_context, get_context

class ProjectManager:
    """
    Beheert project configuratie en scoping voor BMAD agents.
    """
    
    def __init__(self):
        self.projects_config_file = Path("bmad/resources/data/general/projects_config.json")
        self.active_project = os.getenv("BMAD_ACTIVE_PROJECT", "default")
        self.projects = self._load_projects_config()
    
    def _load_projects_config(self) -> Dict[str, Any]:
        """Laad project configuratie uit JSON file."""
        if self.projects_config_file.exists():
            try:
                with open(self.projects_config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load projects config: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Genereer default project configuratie."""
        return {
            "default": {
                "name": "Default Project",
                "description": "Default BMAD project",
                "clickup": {
                    "folder_id": os.getenv("CLICKUP_FOLDER_ID"),
                    "list_id": os.getenv("CLICKUP_LIST_ID")
                },
                "agents": {
                    "product_owner": "default_po",
                    "scrum_master": "default_sm",
                    "architect": "default_arch"
                },
                "settings": {
                    "auto_sync": True,
                    "webhook_enabled": True,
                    "notifications": True
                }
            }
        }
    
    def create_project(self, project_id: str, name: str, description: str = "", 
                      clickup_folder_id: Optional[str] = None, 
                      clickup_list_id: Optional[str] = None) -> bool:
        """
        Maak een nieuw project aan.
        
        :param project_id: Unieke project identifier
        :param name: Project naam
        :param description: Project beschrijving
        :param clickup_folder_id: ClickUp folder ID (optioneel)
        :param clickup_list_id: ClickUp list ID (optioneel)
        :return: True bij succes
        """
        try:
            project_config = {
                "name": name,
                "description": description,
                "clickup": {
                    "folder_id": clickup_folder_id or os.getenv("CLICKUP_FOLDER_ID"),
                    "list_id": clickup_list_id or os.getenv("CLICKUP_LIST_ID")
                },
                "agents": {
                    "product_owner": f"{project_id}_po",
                    "scrum_master": f"{project_id}_sm", 
                    "architect": f"{project_id}_arch"
                },
                "settings": {
                    "auto_sync": True,
                    "webhook_enabled": True,
                    "notifications": True
                },
                "created_at": self._get_timestamp()
            }
            
            self.projects[project_id] = project_config
            self._save_projects_config()
            
            # Sla project configuratie op in Supabase
            save_context("ProjectManager", "project_config", project_config, scope=project_id)
            
            print(f"✅ Project '{name}' (ID: {project_id}) aangemaakt")
            return True
            
        except Exception as e:
            print(f"❌ Fout bij aanmaken project: {e}")
            return False
    
    def get_project_config(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Haal project configuratie op.
        
        :param project_id: Project ID (gebruikt active_project als None)
        :return: Project configuratie
        """
        project_id = project_id or self.active_project
        
        if project_id not in self.projects:
            print(f"⚠️ Project '{project_id}' niet gevonden, gebruik default")
            project_id = "default"
        
        return self.projects[project_id]
    
    def get_clickup_config(self, project_id: Optional[str] = None) -> Dict[str, str]:
        """
        Haal ClickUp configuratie op voor een project.
        :param project_id: Project ID (gebruikt active_project als None)
        :return: ClickUp configuratie (inclusief space_id, folder_id, list_id)
        """
        project_config = self.get_project_config(project_id)
        clickup_config = project_config.get("clickup", {})
        # Fallback naar .env als niet aanwezig
        import os
        return {
            "space_id": clickup_config.get("space_id") or os.getenv("CLICKUP_SPACE_ID"),
            "folder_id": clickup_config.get("folder_id") or os.getenv("CLICKUP_FOLDER_ID"),
            "list_id": clickup_config.get("list_id") or os.getenv("CLICKUP_LIST_ID")
        }
    
    def set_active_project(self, project_id: str) -> bool:
        """
        Stel actief project in.
        
        :param project_id: Project ID
        :return: True bij succes
        """
        if project_id in self.projects:
            self.active_project = project_id
            os.environ["BMAD_ACTIVE_PROJECT"] = project_id
            print(f"✅ Actief project ingesteld op: {project_id}")
            return True
        else:
            print(f"❌ Project '{project_id}' niet gevonden")
            return False
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        Toon alle beschikbare projecten.
        
        :return: Lijst van projecten
        """
        projects = []
        for project_id, config in self.projects.items():
            project_info = {
                "id": project_id,
                "name": config.get("name", "Unknown"),
                "description": config.get("description", ""),
                "active": project_id == self.active_project,
                "created_at": config.get("created_at", "Unknown")
            }
            projects.append(project_info)
        
        return projects
    
    def update_project_config(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update project configuratie.
        
        :param project_id: Project ID
        :param updates: Updates om toe te passen
        :return: True bij succes
        """
        if project_id not in self.projects:
            print(f"❌ Project '{project_id}' niet gevonden")
            return False
        
        try:
            # Update configuratie
            for key, value in updates.items():
                if key in ["clickup", "agents", "settings"]:
                    self.projects[project_id][key].update(value)
                else:
                    self.projects[project_id][key] = value
            
            self.projects[project_id]["updated_at"] = self._get_timestamp()
            self._save_projects_config()
            
            # Update in Supabase
            save_context("ProjectManager", "project_config", self.projects[project_id], scope=project_id)
            
            print(f"✅ Project '{project_id}' configuratie bijgewerkt")
            return True
            
        except Exception as e:
            print(f"❌ Fout bij updaten project configuratie: {e}")
            return False
    
    def delete_project(self, project_id: str) -> bool:
        """
        Verwijder een project.
        
        :param project_id: Project ID
        :return: True bij succes
        """
        if project_id == "default":
            print("❌ Kan default project niet verwijderen")
            return False
        
        if project_id not in self.projects:
            print(f"❌ Project '{project_id}' niet gevonden")
            return False
        
        try:
            # Archiveer project configuratie
            archived_config = self.projects[project_id]
            archived_config["archived_at"] = self._get_timestamp()
            save_context("ProjectManager", "archived_project", archived_config, scope=project_id)
            
            # Verwijder uit actieve configuratie
            del self.projects[project_id]
            self._save_projects_config()
            
            # Als dit het actieve project was, schakel over naar default
            if project_id == self.active_project:
                self.set_active_project("default")
            
            print(f"✅ Project '{project_id}' verwijderd")
            return True
            
        except Exception as e:
            print(f"❌ Fout bij verwijderen project: {e}")
            return False
    
    def get_project_scope(self, project_id: Optional[str] = None) -> str:
        """
        Haal project scope op voor context opslag.
        
        :param project_id: Project ID (gebruikt active_project als None)
        :return: Project scope string
        """
        project_id = project_id or self.active_project
        return f"project:{project_id}"
    
    def _save_projects_config(self) -> None:
        """Sla project configuratie op naar JSON file."""
        try:
            self.projects_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.projects_config_file, 'w') as f:
                json.dump(self.projects, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save projects config: {e}")
    
    def _get_timestamp(self) -> str:
        """Genereer timestamp string."""
        from datetime import datetime
        return datetime.now().isoformat()

# Global instance
project_manager = ProjectManager() 