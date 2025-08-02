"""
Template service for the Notification Service.

This module handles template rendering, validation, and management
for different notification channels.
"""

import re
from typing import Dict, Any, Optional, List
from jinja2 import Environment, Template as JinjaTemplate, TemplateError
from jinja2.exceptions import UndefinedError

from ..models.schemas import TemplateCreate, NotificationChannel
from ..models.database import Template
from .database import DatabaseService


class TemplateService:
    """Template service for notification templates."""
    
    def __init__(self, database_service: DatabaseService):
        """Initialize template service."""
        self.database_service = database_service
        self.jinja_env = Environment(
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    async def create_template(self, template_data: TemplateCreate) -> Template:
        """Create a new template."""
        # Validate template syntax
        await self._validate_template_syntax(template_data.content_template)
        
        # Check for variable consistency
        await self._validate_template_variables(template_data.content_template, template_data.variables)
        
        return await self.database_service.create_template(template_data)
    
    async def get_template(self, template_id: str) -> Optional[Template]:
        """Get template by ID."""
        return await self.database_service.get_template(template_id)
    
    async def get_templates(
        self,
        channel: Optional[NotificationChannel] = None,
        language: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 20
    ) -> tuple[List[Template], int]:
        """Get templates with filters."""
        return await self.database_service.get_templates(
            channel=channel.value if channel else None,
            language=language,
            is_active=is_active,
            page=page,
            size=size
        )
    
    async def update_template(
        self,
        template_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Template]:
        """Update template."""
        # Validate template syntax if content is being updated
        if "content_template" in update_data:
            await self._validate_template_syntax(update_data["content_template"])
            
            # Check for variable consistency
            if "variables" in update_data:
                await self._validate_template_variables(
                    update_data["content_template"],
                    update_data["variables"]
                )
        
        return await self.database_service.update_template(template_id, update_data)
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete template."""
        return await self.database_service.delete_template(template_id)
    
    async def render_template(
        self,
        template_id: str,
        variables: Dict[str, Any]
    ) -> Dict[str, str]:
        """Render template with variables."""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        if not template.is_active:
            raise ValueError(f"Template {template_id} is not active")
        
        try:
            # Render content template
            content_template = self.jinja_env.from_string(template.content_template)
            rendered_content = content_template.render(**variables)
            
            result = {"content": rendered_content}
            
            # Render subject template if exists
            if template.subject_template:
                subject_template = self.jinja_env.from_string(template.subject_template)
                rendered_subject = subject_template.render(**variables)
                result["subject"] = rendered_subject
            
            return result
            
        except TemplateError as e:
            raise ValueError(f"Template rendering error: {str(e)}")
        except UndefinedError as e:
            raise ValueError(f"Undefined variable in template: {str(e)}")
    
    async def test_template(
        self,
        template_id: str,
        variables: Dict[str, Any],
        recipient: str
    ) -> Dict[str, Any]:
        """Test template rendering with sample data."""
        try:
            rendered = await self.render_template(template_id, variables)
            
            return {
                "success": True,
                "rendered_content": rendered.get("content"),
                "rendered_subject": rendered.get("subject"),
                "variables_used": list(variables.keys()),
                "recipient": recipient
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "variables_used": list(variables.keys()),
                "recipient": recipient
            }
    
    async def get_template_variables(self, template_id: str) -> List[str]:
        """Extract variables from template."""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        return await self._extract_variables_from_template(template.content_template)
    
    async def _validate_template_syntax(self, content_template: str) -> None:
        """Validate template syntax."""
        try:
            self.jinja_env.from_string(content_template)
        except TemplateError as e:
            raise ValueError(f"Invalid template syntax: {str(e)}")
    
    async def _validate_template_variables(
        self,
        content_template: str,
        variables: Dict[str, str]
    ) -> None:
        """Validate template variables consistency."""
        template_variables = await self._extract_variables_from_template(content_template)
        
        # Check if all template variables are defined in variables dict
        for var in template_variables:
            if var not in variables:
                raise ValueError(f"Template variable '{var}' not defined in variables")
        
        # Check if all variables in dict are used in template
        for var in variables:
            if var not in template_variables:
                raise ValueError(f"Variable '{var}' defined but not used in template")
    
    async def _extract_variables_from_template(self, content_template: str) -> List[str]:
        """Extract variables from template content."""
        # Simple regex to extract Jinja2 variables
        # This matches {{ variable_name }} and {{ variable_name | filter }}
        variable_pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\|[^}]*)?\}\}'
        matches = re.findall(variable_pattern, content_template)
        
        # Remove duplicates and return
        return list(set(matches))
    
    async def get_template_analytics(self, template_id: str) -> Dict[str, Any]:
        """Get template usage analytics."""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Get notifications using this template
        notifications, total = await self.database_service.get_notifications(
            template_id=template_id
        )
        
        # Calculate success rate
        successful = sum(1 for n in notifications if n.status == "delivered")
        failed = sum(1 for n in notifications if n.status == "failed")
        total_sent = successful + failed
        
        success_rate = (successful / total_sent * 100) if total_sent > 0 else 0
        
        return {
            "template_id": template_id,
            "template_name": template.name,
            "total_uses": total,
            "successful_deliveries": successful,
            "failed_deliveries": failed,
            "success_rate": round(success_rate, 2),
            "last_used": max([n.created_at for n in notifications]) if notifications else None
        }
    
    async def duplicate_template(
        self,
        template_id: str,
        new_name: str,
        new_language: Optional[str] = None
    ) -> Template:
        """Duplicate an existing template."""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Create new template data
        template_data = TemplateCreate(
            name=new_name,
            description=f"Copy of {template.name}",
            channel=NotificationChannel(template.channel),
            subject_template=template.subject_template,
            content_template=template.content_template,
            variables=template.variables,
            language=new_language or template.language,
            version=1,
            is_active=False  # Start as inactive for review
        )
        
        return await self.create_template(template_data)
    
    async def get_template_by_name(
        self,
        name: str,
        channel: NotificationChannel,
        language: str = "en"
    ) -> Optional[Template]:
        """Get template by name, channel, and language."""
        templates, _ = await self.get_templates(
            channel=channel,
            language=language,
            is_active=True
        )
        
        for template in templates:
            if template.name == name:
                return template
        
        return None 