"""
BMAD Confidence Scoring Utility

Dit module biedt utilities voor agents om confidence scores te berekenen
en review requirements te bepalen voor hun output.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .llm_client import calculate_confidence, assess_complexity, assess_security_risk

logger = logging.getLogger(__name__)

class ConfidenceScoring:
    """
    Utility class voor confidence scoring en review management.
    """
    
    def __init__(self):
        self.review_thresholds = {
            "low": 0.5,      # Vereist volledige review
            "medium": 0.8,   # Notificeer maar ga door
            "high": 1.0      # Auto-approve
        }
    
    def enhance_agent_output(
        self, 
        output: str, 
        agent_name: str, 
        task_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enhance agent output met confidence scoring en review requirements.
        
        :param output: Agent output
        :param agent_name: Naam van de agent
        :param task_type: Type van de taak
        :param context: Extra context informatie
        :return: Enhanced output met confidence en review info
        """
        if context is None:
            context = {}
        
        # Voeg agent en task info toe aan context
        context.update({
            "agent": agent_name,
            "task": task_type,
            "timestamp": datetime.now().isoformat()
        })
        
        # Bereken confidence score
        confidence = calculate_confidence(output, context)
        
        # Bepaal review requirement
        review_required = self._determine_review_requirement(confidence, context)
        
        # Bepaal review level
        review_level = self._get_review_level(confidence)
        
        # Maak enhanced output
        enhanced_output = {
            "output": output,
            "confidence": confidence,
            "review_required": review_required,
            "review_level": review_level,
            "metadata": {
                "agent": agent_name,
                "task_type": task_type,
                "timestamp": context["timestamp"],
                "context": context
            }
        }
        
        # Log confidence info
        logger.info(f"[CONFIDENCE] {agent_name} - {task_type}: {confidence:.2f} ({review_level})")
        
        return enhanced_output
    
    def _determine_review_requirement(self, confidence: float, context: Dict[str, Any]) -> bool:
        """
        Bepaal of menselijke review vereist is.
        
        :param confidence: Confidence score
        :param context: Context informatie
        :return: True als review vereist is
        """
        # Low confidence = altijd review
        if confidence < self.review_thresholds["low"]:
            return True
        
        # Security-critical changes = altijd review
        if self._is_security_critical(context):
            return True
        
        # High complexity tasks = review bij medium confidence
        if self._is_high_complexity(context) and confidence < self.review_thresholds["medium"]:
            return True
        
        # Production deployments = altijd review
        if self._is_production_deployment(context):
            return True
        
        return False
    
    def _get_review_level(self, confidence: float) -> str:
        """
        Bepaal review level op basis van confidence score.
        
        :param confidence: Confidence score
        :return: Review level (low/medium/high)
        """
        if confidence < self.review_thresholds["low"]:
            return "low"
        elif confidence < self.review_thresholds["medium"]:
            return "medium"
        else:
            return "high"
    
    def _is_security_critical(self, context: Dict[str, Any]) -> bool:
        """
        Check of de taak security-critical is.
        
        :param context: Context informatie
        :return: True als security-critical
        """
        task_type = context.get("task", "").lower()
        agent_name = context.get("agent", "").lower()
        
        security_keywords = [
            "auth", "authentication", "security", "encryption", "password", 
            "token", "key", "secret", "admin", "root", "permission"
        ]
        
        # Check task type
        if any(keyword in task_type for keyword in security_keywords):
            return True
        
        # Check agent type
        if "security" in agent_name:
            return True
        
        return False
    
    def _is_high_complexity(self, context: Dict[str, Any]) -> bool:
        """
        Check of de taak high complexity is.
        
        :param context: Context informatie
        :return: True als high complexity
        """
        task_type = context.get("task", "").lower()
        
        complexity_keywords = [
            "architect", "design", "infrastructure", "deployment", 
            "database", "api", "integration", "migration"
        ]
        
        return any(keyword in task_type for keyword in complexity_keywords)
    
    def _is_production_deployment(self, context: Dict[str, Any]) -> bool:
        """
        Check of het een production deployment is.
        
        :param context: Context informatie
        :return: True als production deployment
        """
        task_type = context.get("task", "").lower()
        output = context.get("output", "").lower()
        
        deployment_keywords = ["deploy", "production", "live", "release"]
        
        return any(keyword in task_type or keyword in output for keyword in deployment_keywords)

def create_review_request(enhanced_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maak een review request voor Slack of andere kanalen.
    
    :param enhanced_output: Enhanced agent output
    :return: Review request dict
    """
    metadata = enhanced_output["metadata"]
    
    review_request = {
        "type": "review_request",
        "agent": metadata["agent"],
        "task_type": metadata["task_type"],
        "confidence": enhanced_output["confidence"],
        "review_level": enhanced_output["review_level"],
        "output_preview": enhanced_output["output"][:200] + "..." if len(enhanced_output["output"]) > 200 else enhanced_output["output"],
        "timestamp": metadata["timestamp"],
        "actions": [
            {"name": "approve", "text": "✅ Approve", "type": "button", "style": "primary"},
            {"name": "reject", "text": "❌ Reject", "type": "button", "style": "danger"},
            {"name": "modify", "text": "✏️ Modify", "type": "button", "style": "default"}
        ]
    }
    
    return review_request

def format_confidence_message(enhanced_output: Dict[str, Any]) -> str:
    """
    Format een bericht voor Slack met confidence informatie.
    
    :param enhanced_output: Enhanced agent output
    :return: Geformatteerd bericht
    """
    metadata = enhanced_output["metadata"]
    confidence = enhanced_output["confidence"]
    review_level = enhanced_output["review_level"]
    
    # Emoji voor confidence level
    if confidence >= 0.8:
        confidence_emoji = "🟢"
    elif confidence >= 0.5:
        confidence_emoji = "🟡"
    else:
        confidence_emoji = "🔴"
    
    # Emoji voor review level
    if review_level == "high":
        review_emoji = "✅"
    elif review_level == "medium":
        review_emoji = "⚠️"
    else:
        review_emoji = "🔍"
    
    message = f"""
{confidence_emoji} **Confidence Score: {confidence:.2f}**
{review_emoji} **Review Level: {review_level.upper()}**

**Agent:** {metadata['agent']}
**Task:** {metadata['task_type']}
**Time:** {metadata['timestamp']}

**Output Preview:**
```
{enhanced_output['output_preview']}
```
"""
    
    return message.strip()

# Global instance voor easy access
confidence_scoring = ConfidenceScoring() 