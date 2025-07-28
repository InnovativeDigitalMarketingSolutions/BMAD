"""
BMAD ClickUp Integration

Dit module biedt integratie met ClickUp voor externe project management,
inclusief task synchronization en bidirectional updates.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from bmad.agents.core.communication.message_bus import publish
from bmad.agents.core.project.project_manager import project_manager
from bmad.agents.core.data.supabase_context import get_context, save_context

logger = logging.getLogger(__name__)

class ClickUpIntegration:
    """
    ClickUp integratie voor externe project management.
    """

    def __init__(self, project_id: Optional[str] = None):
        self.api_key = os.getenv("CLICKUP_API_KEY")
        self.base_url = "https://api.clickup.com/api/v2"

        # Project-specifieke configuratie
        self.project_id = project_id or project_manager.active_project
        clickup_config = project_manager.get_clickup_config(self.project_id)
        self.space_id = clickup_config.get("space_id") or os.getenv("CLICKUP_SPACE_ID")
        self.folder_id = clickup_config.get("folder_id") or os.getenv("CLICKUP_FOLDER_ID")
        self.list_id = clickup_config.get("list_id") or os.getenv("CLICKUP_LIST_ID")

        if not self.api_key:
            logger.warning("CLICKUP_API_KEY niet gezet - ClickUp integratie uitgeschakeld")
            self.enabled = False
        else:
            self.enabled = True
            self.headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }

    def create_project(self, project_name: str, project_type: str, description: str = "") -> Optional[str]:
        """
        Maak een nieuw ClickUp project aan.
        
        :param project_name: Naam van het project
        :param project_type: Type project (web_app, mobile_app, api_service)
        :param description: Project beschrijving
        :return: ClickUp project ID of None bij fout
        """
        if not self.enabled:
            logger.warning("ClickUp integratie uitgeschakeld")
            return None

        try:
            # Maak een nieuwe list in ClickUp
            list_data = {
                "name": project_name,
                "content": description,
                "due_date": None,
                "due_date_time": False,
                "priority": 1,
                "assignee": None,
                "status": "to do"
            }

            url = f"{self.base_url}/list/{self.list_id}/task"
            response = requests.post(url, headers=self.headers, json=list_data)
            response.raise_for_status()

            task_data = response.json()
            task_id = task_data["id"]

            # Sla project mapping op
            project_mapping = {
                "project_name": project_name,
                "project_type": project_type,
                "clickup_task_id": task_id,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }

            project_scope = project_manager.get_project_scope(self.project_id)
            save_context("clickup_projects", project_name, project_mapping, scope=project_scope)

            logger.info(f"ClickUp project aangemaakt: {project_name} (ID: {task_id})")

            # Publish event
            publish("clickup_project_created", {
                "project_name": project_name,
                "clickup_task_id": task_id,
                "project_type": project_type
            })

            return task_id

        except Exception as e:
            logger.error(f"Fout bij aanmaken ClickUp project: {e}")
            return None

    def create_task(self, project_name: str, task_name: str, description: str,
                   priority: str = "medium", assignee: Optional[str] = None) -> Optional[str]:
        """
        Maak een nieuwe taak aan in ClickUp.
        
        :param project_name: Naam van het project
        :param task_name: Naam van de taak
        :param description: Taak beschrijving
        :param priority: Prioriteit (low, medium, high, urgent)
        :param assignee: Toegewezen gebruiker (optioneel)
        :return: ClickUp task ID of None bij fout
        """
        if not self.enabled:
            logger.warning("ClickUp integratie uitgeschakeld")
            return None

        try:
            # Haal project mapping op
            project_scope = project_manager.get_project_scope(self.project_id)
            project_mapping = get_context("clickup_projects", project_name, scope=project_scope)
            if not project_mapping:
                logger.error(f"Project mapping niet gevonden voor: {project_name}")
                return None

            # Converteer prioriteit naar ClickUp format
            priority_map = {
                "low": 4,
                "medium": 3,
                "high": 2,
                "urgent": 1
            }
            clickup_priority = priority_map.get(priority.lower(), 3)

            # Maak taak aan
            task_data = {
                "name": task_name,
                "content": description,
                "due_date": None,
                "due_date_time": False,
                "priority": clickup_priority,
                "assignee": assignee,
                "status": "to do",
                "parent": project_mapping.get("clickup_task_id")
            }

            url = f"{self.base_url}/list/{self.list_id}/task"
            response = requests.post(url, headers=self.headers, json=task_data)
            response.raise_for_status()

            task_data = response.json()
            task_id = task_data["id"]

            # Sla taak mapping op
            task_mapping = {
                "project_name": project_name,
                "task_name": task_name,
                "clickup_task_id": task_id,
                "priority": priority,
                "assignee": assignee,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }

            project_scope = project_manager.get_project_scope(self.project_id)
            save_context("clickup_tasks", task_id, task_mapping, scope=project_scope)

            logger.info(f"ClickUp taak aangemaakt: {task_name} (ID: {task_id})")

            # Publish event
            publish("clickup_task_created", {
                "project_name": project_name,
                "task_name": task_name,
                "clickup_task_id": task_id,
                "priority": priority
            })

            return task_id

        except Exception as e:
            logger.error(f"Fout bij aanmaken ClickUp taak: {e}")
            return None

    def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Update de status van een ClickUp taak.
        
        :param task_id: ClickUp task ID
        :param status: Nieuwe status (to do, in progress, review, done)
        :return: True bij succes, False bij fout
        """
        if not self.enabled:
            logger.warning("ClickUp integratie uitgeschakeld")
            return False

        try:
            # Converteer status naar ClickUp format
            status_map = {
                "to do": "to do",
                "in progress": "in progress",
                "review": "review",
                "done": "done"
            }
            clickup_status = status_map.get(status.lower(), "to do")

            # Update taak status
            update_data = {
                "status": clickup_status
            }

            url = f"{self.base_url}/task/{task_id}"
            response = requests.put(url, headers=self.headers, json=update_data)
            response.raise_for_status()

            # Update lokale mapping
            project_scope = project_manager.get_project_scope(self.project_id)
            task_mapping = get_context("clickup_tasks", task_id, scope=project_scope)
            if task_mapping:
                task_mapping["status"] = clickup_status
                task_mapping["updated_at"] = datetime.now().isoformat()
                save_context("clickup_tasks", task_id, task_mapping, scope=project_scope)

            logger.info(f"ClickUp taak status bijgewerkt: {task_id} -> {clickup_status}")

            # Publish event
            publish("clickup_task_updated", {
                "task_id": task_id,
                "status": clickup_status,
                "updated_at": datetime.now().isoformat()
            })

            return True

        except Exception as e:
            logger.error(f"Fout bij updaten ClickUp taak status: {e}")
            return False

    def sync_project_requirements(self, project_name: str, requirements: List[Dict[str, Any]]) -> bool:
        """
        Synchroniseer project requirements met ClickUp.
        
        :param project_name: Naam van het project
        :param requirements: Lijst van requirements
        :return: True bij succes, False bij fout
        """
        if not self.enabled:
            logger.warning("ClickUp integratie uitgeschakeld")
            return False

        try:
            for req in requirements:
                req_name = f"Requirement: {req.get('description', 'Unknown')}"
                req_description = f"""
**Category:** {req.get('category', 'Unknown')}
**Priority:** {req.get('priority', 'medium')}

**Description:**
{req.get('description', 'No description')}

**Acceptance Criteria:**
{req.get('acceptance_criteria', 'To be defined')}
                """.strip()

                # Maak requirement taak aan
                task_id = self.create_task(
                    project_name=project_name,
                    task_name=req_name,
                    description=req_description,
                    priority=req.get("priority", "medium")
                )

                if task_id:
                    logger.info(f"Requirement gesynchroniseerd: {req_name}")

            logger.info(f"Project requirements gesynchroniseerd voor: {project_name}")
            return True

        except Exception as e:
            logger.error(f"Fout bij synchroniseren requirements: {e}")
            return False

    def sync_user_stories(self, project_name: str, user_stories: List[Dict[str, Any]]) -> bool:
        """
        Synchroniseer user stories met ClickUp.
        
        :param project_name: Naam van het project
        :param user_stories: Lijst van user stories
        :return: True bij succes, False bij fout
        """
        if not self.enabled:
            logger.warning("ClickUp integratie uitgeschakeld")
            return False

        try:
            for story in user_stories:
                story_name = f"User Story: {story.get('title', 'Unknown')}"
                story_description = f"""
**As a:** {story.get('as_a', 'user')}
**I want:** {story.get('i_want', 'feature')}
**So that:** {story.get('so_that', 'benefit')}

**Acceptance Criteria:**
{story.get('acceptance_criteria', 'To be defined')}

**Priority:** {story.get('priority', 'medium')}
**Story Points:** {story.get('story_points', 'TBD')}
                """.strip()

                # Maak user story taak aan
                task_id = self.create_task(
                    project_name=project_name,
                    task_name=story_name,
                    description=story_description,
                    priority=story.get("priority", "medium")
                )

                if task_id:
                    logger.info(f"User story gesynchroniseerd: {story_name}")

            logger.info(f"User stories gesynchroniseerd voor: {project_name}")
            return True

        except Exception as e:
            logger.error(f"Fout bij synchroniseren user stories: {e}")
            return False

    def get_project_tasks(self, project_name: str) -> List[Dict[str, Any]]:
        """
        Haal alle taken op voor een project.
        
        :param project_name: Naam van het project
        :return: Lijst van taken
        """
        if not self.enabled:
            logger.warning("ClickUp integratie uitgeschakeld")
            return []

        try:
            # Haal project mapping op
            project_scope = project_manager.get_project_scope(self.project_id)
            project_mapping = get_context("clickup_projects", project_name, scope=project_scope)
            if not project_mapping:
                logger.error(f"Project mapping niet gevonden voor: {project_name}")
                return []

            project_task_id = project_mapping.get("clickup_task_id")

            # Haal subtaken op
            url = f"{self.base_url}/task/{project_task_id}/subtask"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            tasks_data = response.json()
            tasks = []

            for task in tasks_data.get("subtasks", []):
                task_info = {
                    "id": task["id"],
                    "name": task["name"],
                    "status": task["status"]["status"],
                    "priority": task["priority"],
                    "assignee": task.get("assignees", []),
                    "created_at": task["date_created"],
                    "updated_at": task["date_updated"]
                }
                tasks.append(task_info)

            logger.info(f"{len(tasks)} taken opgehaald voor project: {project_name}")
            return tasks

        except Exception as e:
            logger.error(f"Fout bij ophalen project taken: {e}")
            return []

    def create_agent_task(self, project_name: str, agent_name: str, task_description: str,
                         estimated_hours: Optional[int] = None) -> Optional[str]:
        """
        Maak een taak aan voor een specifieke agent.
        
        :param project_name: Naam van het project
        :param agent_name: Naam van de agent
        :param task_description: Taak beschrijving
        :param estimated_hours: Geschatte uren (optioneel)
        :return: ClickUp task ID of None bij fout
        """
        if not self.enabled:
            logger.warning("ClickUp integratie uitgeschakeld")
            return None

        try:
            task_name = f"[{agent_name}] {task_description[:50]}..."

            description = f"""
**Agent:** {agent_name}
**Task:** {task_description}

**Estimated Hours:** {estimated_hours or 'TBD'}

**Status:** Assigned to {agent_name}
            """.strip()

            # Maak agent taak aan
            task_id = self.create_task(
                project_name=project_name,
                task_name=task_name,
                description=description,
                priority="medium",
                assignee=agent_name
            )

            if task_id:
                logger.info(f"Agent taak aangemaakt: {agent_name} - {task_description}")

                # Publish event
                publish("clickup_agent_task_created", {
                    "project_name": project_name,
                    "agent_name": agent_name,
                    "task_description": task_description,
                    "clickup_task_id": task_id
                })

            return task_id

        except Exception as e:
            logger.error(f"Fout bij aanmaken agent taak: {e}")
            return None

    def mark_task_completed(self, task_id: str, completion_notes: str = "") -> bool:
        """
        Markeer een taak als voltooid.
        
        :param task_id: ClickUp task ID
        :param completion_notes: Notities bij voltooiing
        :return: True bij succes, False bij fout
        """
        if not self.enabled:
            logger.warning("ClickUp integratie uitgeschakeld")
            return False

        try:
            # Update taak status naar done
            success = self.update_task_status(task_id, "done")

            if success and completion_notes:
                # Voeg completion notes toe
                comment_data = {
                    "comment_text": f"✅ Task completed\n\n{completion_notes}"
                }

                url = f"{self.base_url}/task/{task_id}/comment"
                response = requests.post(url, headers=self.headers, json=comment_data)
                response.raise_for_status()

            logger.info(f"Taak gemarkeerd als voltooid: {task_id}")
            return success

        except Exception as e:
            logger.error(f"Fout bij markeren taak als voltooid: {e}")
            return False

    def get_project_metrics(self, project_name: str) -> Dict[str, Any]:
        """
        Haal project metrics op uit ClickUp.
        
        :param project_name: Naam van het project
        :return: Project metrics
        """
        if not self.enabled:
            logger.warning("ClickUp integratie uitgeschakeld")
            return {}

        try:
            tasks = self.get_project_tasks(project_name)

            # Bereken metrics
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t["status"] == "done"])
            in_progress_tasks = len([t for t in tasks if t["status"] == "in progress"])
            pending_tasks = len([t for t in tasks if t["status"] == "to do"])

            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            metrics = {
                "project_name": project_name,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "pending_tasks": pending_tasks,
                "completion_rate": round(completion_rate, 2),
                "last_updated": datetime.now().isoformat()
            }

            logger.info(f"Project metrics opgehaald voor: {project_name}")
            return metrics

        except Exception as e:
            logger.error(f"Fout bij ophalen project metrics: {e}")
            return {}

# Global instance
clickup_integration = ClickUpIntegration()
