#!/usr/bin/env python3
"""
BMAD Project Manager
Centraal systeem voor project management en configuratie
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
load_dotenv()

from bmad.agents.core.data.supabase_context import save_context, get_context
from bmad.agents.core.message_bus import publish

class ProjectManager:
    def __init__(self):
        self.projects_dir = Path(__file__).parent / "configs"
        self.projects_dir.mkdir(exist_ok=True)
        self.current_project = None
        self.project_config = None

    def list_projects(self) -> List[str]:
        """Toon alle beschikbare projecten."""
        projects = []
        for config_file in self.projects_dir.glob("*.json"):
            projects.append(config_file.stem)
        return projects

    def create_project(self, project_name: str, project_type: str = "web_app") -> Dict[str, Any]:
        """Maak een nieuw project aan."""
        template = self._get_project_template(project_type)
        
        config = {
            "project_name": project_name,
            "project_type": project_type,
            "created_at": time.time(),
            "updated_at": time.time(),
            "status": "active",
            **template
        }
        
        config_file = self.projects_dir / f"{project_name}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Project '{project_name}' aangemaakt!")
        return config

    def load_project(self, project_name: str) -> Dict[str, Any]:
        """Laad een project configuratie."""
        config_file = self.projects_dir / f"{project_name}.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Project '{project_name}' niet gevonden!")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        self.current_project = project_name
        self.project_config = config
        
        # Publiceer project loaded event
        publish("project_loaded", {
            "project_name": project_name,
            "config": config
        })
        
        print(f"📁 Project '{project_name}' geladen!")
        return config

    def get_current_project(self) -> Optional[Dict[str, Any]]:
        """Haal huidige project configuratie op."""
        return self.project_config

    def update_project(self, updates: Dict[str, Any]) -> None:
        """Update project configuratie."""
        if not self.current_project:
            raise ValueError("Geen project geladen!")
        
        self.project_config.update(updates)
        self.project_config["updated_at"] = time.time()
        
        config_file = self.projects_dir / f"{self.current_project}.json"
        with open(config_file, 'w') as f:
            json.dump(self.project_config, f, indent=2)
        
        # Publiceer project updated event
        publish("project_updated", {
            "project_name": self.current_project,
            "updates": updates
        })
        
        print(f"✅ Project '{self.current_project}' bijgewerkt!")

    def add_requirement(self, requirement: str, category: str = "general") -> None:
        """Voeg een requirement toe aan het project."""
        if not self.current_project:
            raise ValueError("Geen project geladen!")
        
        if "requirements" not in self.project_config:
            self.project_config["requirements"] = {}
        
        if category not in self.project_config["requirements"]:
            self.project_config["requirements"][category] = []
        
        self.project_config["requirements"][category].append({
            "id": len(self.project_config["requirements"][category]) + 1,
            "description": requirement,
            "status": "pending",
            "created_at": time.time()
        })
        
        self.update_project({})

    def add_user_story(self, story: str, priority: str = "medium") -> None:
        """Voeg een user story toe aan het project."""
        if not self.current_project:
            raise ValueError("Geen project geladen!")
        
        if "user_stories" not in self.project_config:
            self.project_config["user_stories"] = []
        
        self.project_config["user_stories"].append({
            "id": len(self.project_config["user_stories"]) + 1,
            "story": story,
            "priority": priority,
            "status": "pending",
            "created_at": time.time()
        })
        
        self.update_project({})

    def get_project_context(self) -> Dict[str, Any]:
        """Haal alle project context op voor agents."""
        if not self.current_project:
            return {}
        
        return {
            "project_name": self.current_project,
            "config": self.project_config,
            "requirements": self.project_config.get("requirements", {}),
            "user_stories": self.project_config.get("user_stories", []),
            "tech_stack": self.project_config.get("tech_stack", {}),
            "architecture": self.project_config.get("architecture", {}),
            "api_endpoints": self.project_config.get("api_endpoints", []),
            "database_schema": self.project_config.get("database_schema", {}),
            "deployment_config": self.project_config.get("deployment_config", {})
        }

    def _get_project_template(self, project_type: str) -> Dict[str, Any]:
        """Haal project template op basis van type."""
        templates = {
            "web_app": {
                "description": "Web applicatie met frontend en backend",
                "tech_stack": {
                    "frontend": ["React", "TypeScript", "Vite"],
                    "backend": ["Python", "FastAPI", "PostgreSQL"],
                    "deployment": ["Docker", "AWS/GCP"]
                },
                "architecture": {
                    "type": "microservices",
                    "frontend": "SPA",
                    "backend": "REST API",
                    "database": "PostgreSQL"
                },
                "requirements": {
                    "functional": [],
                    "non_functional": [],
                    "technical": []
                },
                "user_stories": [],
                "api_endpoints": [],
                "database_schema": {},
                "deployment_config": {}
            },
            "mobile_app": {
                "description": "Mobile applicatie",
                "tech_stack": {
                    "frontend": ["React Native", "TypeScript"],
                    "backend": ["Python", "FastAPI", "PostgreSQL"],
                    "deployment": ["Expo", "App Store"]
                },
                "architecture": {
                    "type": "client-server",
                    "frontend": "React Native",
                    "backend": "REST API",
                    "database": "PostgreSQL"
                },
                "requirements": {
                    "functional": [],
                    "non_functional": [],
                    "technical": []
                },
                "user_stories": [],
                "api_endpoints": [],
                "database_schema": {},
                "deployment_config": {}
            },
            "api_service": {
                "description": "API service",
                "tech_stack": {
                    "backend": ["Python", "FastAPI", "PostgreSQL"],
                    "deployment": ["Docker", "Kubernetes"]
                },
                "architecture": {
                    "type": "api_service",
                    "backend": "REST API",
                    "database": "PostgreSQL"
                },
                "requirements": {
                    "functional": [],
                    "non_functional": [],
                    "technical": []
                },
                "user_stories": [],
                "api_endpoints": [],
                "database_schema": {},
                "deployment_config": {}
            }
        }
        
        return templates.get(project_type, templates["web_app"])

# Global project manager instance
project_manager = ProjectManager() 