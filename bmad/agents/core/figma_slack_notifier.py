import os
import time
import logging
from typing import Dict, List, Optional
from bmad.agents.core.figma_client import FigmaClient
from bmad.agents.core.slack_notify import send_slack_message
from bmad.agents.core.message_bus import subscribe, publish
from dotenv import load_dotenv

load_dotenv()

# Configuratie
FIGMA_NOTIFICATION_CHANNEL = os.getenv("FIGMA_NOTIFICATION_CHANNEL", "#design-updates")
FIGMA_POLL_INTERVAL = int(os.getenv("FIGMA_POLL_INTERVAL", "300"))  # 5 minuten
FIGMA_FILES_TO_MONITOR = os.getenv("FIGMA_FILES_TO_MONITOR", "").split(",")  # Comma-separated file IDs

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

class FigmaSlackNotifier:
    def __init__(self):
        self.client = FigmaClient()
        self.last_comment_timestamps = {}
        self.last_file_versions = {}
        
    def monitor_figma_files(self):
        """Monitor Figma files voor wijzigingen en comments."""
        try:
            for file_id in FIGMA_FILES_TO_MONITOR:
                if not file_id.strip():
                    continue
                    
                file_id = file_id.strip()
                self._check_file_updates(file_id)
                self._check_new_comments(file_id)
                
        except Exception as e:
            logging.error(f"[FigmaSlackNotifier] Error monitoring files: {str(e)}")
    
    def _check_file_updates(self, file_id: str):
        """Check voor file updates en stuur notificatie."""
        try:
            file_data = self.client.get_file(file_id)
            current_version = file_data.get('version', '')
            file_name = file_data.get('name', 'Unknown')
            
            last_version = self.last_file_versions.get(file_id)
            
            if last_version and last_version != current_version:
                # File is gewijzigd
                self._send_file_update_notification(file_id, file_name, last_version, current_version)
            
            self.last_file_versions[file_id] = current_version
            
        except Exception as e:
            logging.error(f"[FigmaSlackNotifier] Error checking file updates for {file_id}: {str(e)}")
    
    def _check_new_comments(self, file_id: str):
        """Check voor nieuwe comments en stuur notificatie."""
        try:
            comments_data = self.client.get_comments(file_id)
            comments = comments_data.get('comments', [])
            
            last_timestamp = self.last_comment_timestamps.get(file_id, 0)
            new_comments = []
            
            for comment in comments:
                comment_time = comment.get('created_at', 0)
                if comment_time > last_timestamp:
                    new_comments.append(comment)
            
            if new_comments:
                self._send_new_comments_notification(file_id, new_comments)
                # Update timestamp naar meest recente comment
                latest_time = max(comment.get('created_at', 0) for comment in comments)
                self.last_comment_timestamps[file_id] = latest_time
                
        except Exception as e:
            logging.error(f"[FigmaSlackNotifier] Error checking comments for {file_id}: {str(e)}")
    
    def _send_file_update_notification(self, file_id: str, file_name: str, old_version: str, new_version: str):
        """Stuur notificatie voor file update."""
        text = f"🎨 *Figma Design Update*\n\n*{file_name}* is bijgewerkt\n• Van versie: {old_version}\n• Naar versie: {new_version}\n• <https://www.figma.com/file/{file_id}|Bekijk in Figma>"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Bekijk Wijzigingen"
                        },
                        "url": f"https://www.figma.com/file/{file_id}",
                        "action_id": "view_figma_changes"
                    }
                ]
            }
        ]
        
        send_slack_message(
            text=text,
            channel=FIGMA_NOTIFICATION_CHANNEL,
            use_api=True,
            blocks=blocks
        )
        
        logging.info(f"[FigmaSlackNotifier] Sent file update notification for {file_name}")
    
    def _send_new_comments_notification(self, file_id: str, new_comments: List[Dict]):
        """Stuur notificatie voor nieuwe comments."""
        if not new_comments:
            return
            
        file_name = "Unknown"
        try:
            file_data = self.client.get_file(file_id)
            file_name = file_data.get('name', 'Unknown')
        except:
            pass
        
        text = f"💬 *Nieuwe Figma Comments*\n\n*{file_name}* heeft {len(new_comments)} nieuwe comment(s)"
        
        # Voeg comment details toe
        comment_texts = []
        for comment in new_comments[:3]:  # Max 3 comments in notificatie
            user_name = comment.get('user', {}).get('name', 'Unknown')
            message = comment.get('message', '')[:100]  # Truncate lange comments
            comment_texts.append(f"• *{user_name}*: {message}")
        
        if comment_texts:
            text += "\n\n" + "\n".join(comment_texts)
        
        if len(new_comments) > 3:
            text += f"\n\n...en {len(new_comments) - 3} meer comments"
        
        text += f"\n\n<https://www.figma.com/file/{file_id}|Bekijk alle comments>"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Bekijk Comments"
                        },
                        "url": f"https://www.figma.com/file/{file_id}",
                        "action_id": "view_figma_comments"
                    }
                ]
            }
        ]
        
        send_slack_message(
            text=text,
            channel=FIGMA_NOTIFICATION_CHANNEL,
            use_api=True,
            blocks=blocks
        )
        
        logging.info(f"[FigmaSlackNotifier] Sent new comments notification for {file_name}")
    
    def send_design_feedback_notification(self, feedback_data: Dict):
        """Stuur notificatie voor design feedback."""
        text = f"🎯 *Design Feedback Ontvangen*\n\n*{feedback_data.get('design_name', 'Unknown Design')}*\n\n{feedback_data.get('feedback_text', '')}"
        
        if feedback_data.get('user_name'):
            text += f"\n\n— *{feedback_data['user_name']}*"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reageer"
                        },
                        "value": f"feedback_{feedback_data.get('id', 'unknown')}",
                        "action_id": "respond_to_feedback"
                    }
                ]
            }
        ]
        
        send_slack_message(
            text=text,
            channel=FIGMA_NOTIFICATION_CHANNEL,
            use_api=True,
            blocks=blocks
        )
        
        logging.info(f"[FigmaSlackNotifier] Sent design feedback notification")
    
    def send_component_generation_notification(self, generation_result: Dict):
        """Stuur notificatie voor gegenereerde componenten."""
        file_name = generation_result.get('file_name', 'Unknown')
        total_generated = generation_result.get('total_generated', 0)
        
        text = f"⚡ *Componenten Gegenereerd*\n\n*{file_name}*\n• {total_generated} componenten gegenereerd"
        
        if generation_result.get('generated_components'):
            component_names = [comp.get('name', '') for comp in generation_result['generated_components'][:5]]
            text += f"\n• Componenten: {', '.join(component_names)}"
            
            if total_generated > 5:
                text += f" (+{total_generated - 5} meer)"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Bekijk Code"
                        },
                        "value": f"view_components_{generation_result.get('file_id', 'unknown')}",
                        "action_id": "view_generated_components"
                    }
                ]
            }
        ]
        
        send_slack_message(
            text=text,
            channel=FIGMA_NOTIFICATION_CHANNEL,
            use_api=True,
            blocks=blocks
        )
        
        logging.info(f"[FigmaSlackNotifier] Sent component generation notification for {file_name}")

# Event handlers
def on_figma_design_feedback(event):
    """Event handler voor design feedback."""
    notifier = FigmaSlackNotifier()
    notifier.send_design_feedback_notification(event)

def on_figma_components_generated(event):
    """Event handler voor gegenereerde componenten."""
    notifier = FigmaSlackNotifier()
    notifier.send_component_generation_notification(event)

def on_figma_analysis_completed(event):
    """Event handler voor voltooide Figma analyse."""
    analysis = event.get('analysis', {})
    file_name = analysis.get('file_name', 'Unknown')
    total_components = analysis.get('total_components', 0)
    accessibility_issues = len(analysis.get('accessibility_issues', []))
    
    text = f"🔍 *Figma Analyse Voltooid*\n\n*{file_name}*\n• {total_components} componenten geanalyseerd"
    
    if accessibility_issues > 0:
        text += f"\n• ⚠️ {accessibility_issues} accessibility issues gevonden"
    else:
        text += f"\n• ✅ Geen accessibility issues gevonden"
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
    ]
    
    send_slack_message(
        text=text,
        channel=FIGMA_NOTIFICATION_CHANNEL,
        use_api=True,
        blocks=blocks
    )
    
    logging.info(f"[FigmaSlackNotifier] Sent analysis completion notification for {file_name}")

# Event subscriptions
subscribe("figma_design_feedback", on_figma_design_feedback)
subscribe("figma_components_generated", on_figma_components_generated)
subscribe("figma_analysis_completed", on_figma_analysis_completed)

# Polling functie voor continue monitoring
def start_figma_monitoring():
    """Start continue monitoring van Figma files."""
    notifier = FigmaSlackNotifier()
    
    while True:
        try:
            notifier.monitor_figma_files()
            time.sleep(FIGMA_POLL_INTERVAL)
        except KeyboardInterrupt:
            logging.info("[FigmaSlackNotifier] Monitoring gestopt")
            break
        except Exception as e:
            logging.error(f"[FigmaSlackNotifier] Error in monitoring loop: {str(e)}")
            time.sleep(60)  # Wacht 1 minuut bij error

if __name__ == "__main__":
    logging.info("[FigmaSlackNotifier] Starting Figma monitoring...")
    start_figma_monitoring() 