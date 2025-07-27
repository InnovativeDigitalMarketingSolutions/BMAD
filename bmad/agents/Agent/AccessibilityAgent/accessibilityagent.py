import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import logging
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio

from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.agent.agent_performance_monitor import get_performance_monitor, MetricType
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from bmad.agents.core.data.supabase_context import save_context, get_context
from bmad.agents.core.ai.llm_client import ask_openai
from integrations.slack.slack_notify import send_slack_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class AccessibilityAgent:
    def __init__(self):
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()
        
        # Resource paths - corrected path
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/accessibilityagent/best-practices.md",
            "audit-template": self.resource_base / "templates/accessibilityagent/audit-template.md",
            "audit-export": self.resource_base / "templates/accessibilityagent/audit-export-template.md",
            "audit-export-csv": self.resource_base / "templates/accessibilityagent/audit-export-template.csv",
            "checklist": self.resource_base / "templates/accessibilityagent/checklist-template.md",
            "improvement-report": self.resource_base / "templates/accessibilityagent/improvement-report-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/accessibilityagent/accessibility-changelog.md",
            "audit-history": self.resource_base / "data/accessibilityagent/audit-history.md",
            "improvement-history": self.resource_base / "data/accessibilityagent/improvement-history.md"
        }
        
        # Initialize audit history
        self.audit_history = []
        self._load_audit_history()

    def _load_audit_history(self):
        """Load audit history from data file"""
        try:
            if self.data_paths["audit-history"].exists():
                with open(self.data_paths["audit-history"], 'r') as f:
                    content = f.read()
                    # Parse audit history from markdown
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('- '):
                            self.audit_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load audit history: {e}")

    def _save_audit_history(self):
        """Save audit history to data file"""
        try:
            self.data_paths["audit-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["audit-history"], 'w') as f:
                f.write("# Accessibility Audit History\n\n")
                for audit in self.audit_history[-50:]:  # Keep last 50 audits
                    f.write(f"- {audit}\n")
        except Exception as e:
            logger.error(f"Could not save audit history: {e}")

    def show_help(self):
        """Show available commands"""
        help_text = """
Accessibility Agent Commands:
  help                    - Show this help message
  audit [target]          - Run accessibility audit on target (default: /mock/page)
  show-audit-history      - Show audit history
  show-checklist          - Show accessibility checklist
  show-best-practices     - Show accessibility best practices
  show-changelog          - Show accessibility changelog
  export-audit [format]   - Export last audit (format: md, csv, json)
  generate-report         - Generate improvement report
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show resource content"""
        try:
            if resource_type == "checklist":
                path = self.template_paths["checklist"]
            elif resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            else:
                print(f"Unknown resource type: {resource_type}")
                return

            if path.exists():
                with open(path, 'r') as f:
                    print(f.read())
            else:
                print(f"Resource file not found: {path}")
        except Exception as e:
            logger.error(f"Error reading resource {resource_type}: {e}")

    def show_audit_history(self):
        """Show audit history"""
        if not self.audit_history:
            print("No audit history available.")
            return
        
        print("Accessibility Audit History:")
        print("=" * 50)
        for i, audit in enumerate(self.audit_history[-10:], 1):  # Show last 10
            print(f"{i}. {audit}")

    def run_accessibility_audit(self, target: str = "/mock/page") -> Dict[str, Any]:
        """Run accessibility audit on target"""
        logger.info(f"Running accessibility audit on {target}...")
        
        # Mock WCAG/ARIA check (in praktijk: koppel aan echte tool)
        result = {
            "target": target,
            "score": 92,
            "issues": [
                {"type": "contrast", "description": "Insufficient color contrast on button", "severity": "medium"},
                {"type": "alt-text", "description": "Missing alt text on image", "severity": "high"}
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "AccessibilityAgent"
        }
        
        # Add to history
        audit_entry = f"{result['timestamp']}: {target} - Score: {result['score']}%"
        self.audit_history.append(audit_entry)
        self._save_audit_history()
        
        # Log performance metric
        self.monitor._record_metric("AccessibilityAgent", MetricType.SUCCESS_RATE, result["score"], "%")
        
        logger.info(f"Audit result: {result}")
        return result

    def export_audit(self, format_type: str = "md", audit_data: Optional[Dict] = None):
        """Export audit data in specified format"""
        if not audit_data:
            # Use last audit or run new one
            if self.audit_history:
                target = self.audit_history[-1].split(": ")[1].split(" - ")[0]
                audit_data = self.run_accessibility_audit(target)
            else:
                audit_data = self.run_accessibility_audit()
        
        try:
            if format_type == "md":
                self._export_markdown(audit_data)
            elif format_type == "csv":
                self._export_csv(audit_data)
            elif format_type == "json":
                self._export_json(audit_data)
            else:
                print(f"Unsupported format: {format_type}")
        except Exception as e:
            logger.error(f"Error exporting audit: {e}")

    def _export_markdown(self, audit_data: Dict):
        """Export audit as markdown"""
        template_path = self.template_paths["audit-export"]
        if template_path.exists():
            with open(template_path, 'r') as f:
                template = f.read()
            
            # Fill template
            content = template.replace("{{target}}", audit_data["target"])
            content = content.replace("{{score}}", str(audit_data["score"]))
            content = content.replace("{{timestamp}}", audit_data["timestamp"])
            
            # Add issues
            issues_text = ""
            for issue in audit_data["issues"]:
                issues_text += f"- **{issue['type']}** ({issue['severity']}): {issue['description']}\n"
            content = content.replace("{{issues}}", issues_text)
            
            # Save to file
            output_file = f"accessibility_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"Audit exported to: {output_file}")

    def _export_csv(self, audit_data: Dict):
        """Export audit as CSV"""
        output_file = f"accessibility_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Target', 'Score', 'Issue Type', 'Severity', 'Description', 'Timestamp'])
            
            for issue in audit_data["issues"]:
                writer.writerow([
                    audit_data["target"],
                    audit_data["score"],
                    issue["type"],
                    issue["severity"],
                    issue["description"],
                    audit_data["timestamp"]
                ])
        
        print(f"Audit exported to: {output_file}")

    def _export_json(self, audit_data: Dict):
        """Export audit as JSON"""
        output_file = f"accessibility_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(audit_data, f, indent=2)
        
        print(f"Audit exported to: {output_file}")

    def generate_improvement_report(self):
        """Generate improvement report based on audit history"""
        try:
            template_path = self.template_paths["improvement-report"]
            if not template_path.exists():
                print("Improvement report template not found.")
                return
            
            with open(template_path, 'r') as f:
                template = f.read()
            
            # Analyze recent audits for common issues
            common_issues = self._analyze_common_issues()
            
            # Fill template
            content = template.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
            content = content.replace("{{common_issues}}", common_issues)
            
            # Save report
            output_file = f"accessibility_improvement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(output_file, 'w') as f:
                f.write(content)
            
            print(f"Improvement report generated: {output_file}")
            
        except Exception as e:
            logger.error(f"Error generating improvement report: {e}")

    def _analyze_common_issues(self) -> str:
        """Analyze audit history for common issues"""
        # Mock analysis - in practice, analyze real audit data
        return """
- **Contrast Issues**: Found in 60% of audits
- **Missing Alt Text**: Found in 40% of audits  
- **Keyboard Navigation**: Found in 25% of audits
- **Focus Indicators**: Found in 20% of audits
        """

    def test_resource_completeness(self):
        """Test if all required resources are available"""
        print("Testing resource completeness...")
        
        missing_resources = []
        
        # Check templates
        for name, path in self.template_paths.items():
            if not path.exists():
                missing_resources.append(f"Template: {name} ({path})")
        
        # Check data files
        for name, path in self.data_paths.items():
            if not path.exists():
                missing_resources.append(f"Data: {name} ({path})")
        
        if missing_resources:
            print("Missing resources:")
            for resource in missing_resources:
                print(f"  - {resource}")
        else:
            print("All resources are available!")

    def collaborate_example(self):
        """Demonstrate collaboration with other agents"""
        logger.info("Starting collaboration example...")
        
        # Publish audit request
        publish("accessibility_audit_requested", {
            "agent": "AccessibilityAgent",
            "target": "/mock/page",
            "timestamp": datetime.now().isoformat()
        })
        
        # Run audit
        audit_result = self.run_accessibility_audit("/mock/page")
        
        # Publish completion
        publish("accessibility_audit_completed", audit_result)
        
        # Notify via Slack
        try:
            send_slack_message(f"Accessibility audit completed for {audit_result['target']} - Score: {audit_result['score']}%")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

    def handle_audit_requested(self, event):
        """Handle audit request from other agents"""
        target = event.get("target", "/mock/page")
        logger.info(f"Audit requested for: {target}")
        self.run_accessibility_audit(target)

    async def handle_audit_completed(self, event):
        """Handle audit completion"""
        logger.info(f"Audit completed: {event}")
        
        # Log audit score as performance metric
        score = event.get("score", 0)
        if "data" in event and "score" in event["data"]:
            score = event["data"]["score"]
        
        self.monitor._record_metric("AccessibilityAgent", MetricType.SUCCESS_RATE, score, "%")
        
        # Evaluate policy
        try:
            allowed = await self.policy_engine.evaluate_policy("accessibility", event)
            logger.info(f"Policy evaluation result: {allowed}")
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")

    def run(self):
        """Run the agent in event-driven mode"""
        def sync_handler(event):
            asyncio.run(self.handle_audit_completed(event))
        
        subscribe("accessibility_audit_completed", sync_handler)
        subscribe("accessibility_audit_requested", self.handle_audit_requested)
        
        logger.info("AccessibilityAgent ready and listening for events...")
        self.collaborate_example()

def main():
    parser = argparse.ArgumentParser(description="Accessibility Agent CLI")
    parser.add_argument("command", nargs="?", default="help", 
                       choices=["help", "audit", "show-audit-history", "show-checklist", 
                               "show-best-practices", "show-changelog", "export-audit", 
                               "generate-report", "test", "collaborate", "run"])
    parser.add_argument("--target", default="/mock/page", help="Target for audit")
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", 
                       help="Export format")
    
    args = parser.parse_args()
    
    agent = AccessibilityAgent()
    
    if args.command == "help":
        agent.show_help()
    elif args.command == "audit":
        agent.run_accessibility_audit(args.target)
    elif args.command == "show-audit-history":
        agent.show_audit_history()
    elif args.command == "show-checklist":
        agent.show_resource("checklist")
    elif args.command == "show-best-practices":
        agent.show_resource("best-practices")
    elif args.command == "show-changelog":
        agent.show_resource("changelog")
    elif args.command == "export-audit":
        agent.export_audit(args.format)
    elif args.command == "generate-report":
        agent.generate_improvement_report()
    elif args.command == "test":
        agent.test_resource_completeness()
    elif args.command == "collaborate":
        agent.collaborate_example()
    elif args.command == "run":
        agent.run()

if __name__ == "__main__":
    main()
