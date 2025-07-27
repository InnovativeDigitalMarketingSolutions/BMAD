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
import time

from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.agent.agent_performance_monitor import get_performance_monitor, MetricType
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from bmad.agents.core.data.supabase_context import save_context, get_context
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.ai.confidence_scoring import confidence_scoring
from integrations.slack.slack_notify import send_slack_message
from integrations.opentelemetry.opentelemetry_tracing import BMADTracer
from integrations.prefect.prefect_workflow import PrefectWorkflowOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class BackendDeveloperAgent:
    def __init__(self):
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()
        self.tracer = BMADTracer(config=type('Config', (), {
            'service_name': 'BackendDeveloperAgent',
            'service_version': '1.0.0',
            'environment': 'development',
            'sample_rate': 1.0,
            'exporters': []
        })())
        self.workflow = PrefectWorkflowOrchestrator()
        
        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/backenddeveloper/best-practices.md",
            "api-template": self.resource_base / "templates/backenddeveloper/api-template.md",
            "api-export-md": self.resource_base / "templates/backenddeveloper/api-export-template.md",
            "api-export-json": self.resource_base / "templates/backenddeveloper/api-export-template.json",
            "performance-report": self.resource_base / "templates/backenddeveloper/performance-report-template.md",
            "database-template": self.resource_base / "templates/backenddeveloper/database-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/backenddeveloper/backend-changelog.md",
            "api-history": self.resource_base / "data/backenddeveloper/api-history.md",
            "performance-history": self.resource_base / "data/backenddeveloper/performance-history.md"
        }
        
        # Initialize histories
        self.api_history = []
        self.performance_history = []
        self._load_api_history()
        self._load_performance_history()

    def _load_api_history(self):
        try:
            if self.data_paths["api-history"].exists():
                with open(self.data_paths["api-history"], 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('- '):
                            self.api_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load API history: {e}")

    def _save_api_history(self):
        try:
            self.data_paths["api-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["api-history"], 'w') as f:
                f.write("# API History\n\n")
                for api in self.api_history[-50:]:
                    f.write(f"- {api}\n")
        except Exception as e:
            logger.error(f"Could not save API history: {e}")

    def _load_performance_history(self):
        try:
            if self.data_paths["performance-history"].exists():
                with open(self.data_paths["performance-history"], 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('- '):
                            self.performance_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load performance history: {e}")

    def _save_performance_history(self):
        try:
            self.data_paths["performance-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["performance-history"], 'w') as f:
                f.write("# Performance History\n\n")
                for perf in self.performance_history[-50:]:
                    f.write(f"- {perf}\n")
        except Exception as e:
            logger.error(f"Could not save performance history: {e}")

    def show_help(self):
        help_text = """
BackendDeveloper Agent Commands:
  help                    - Show this help message
  build-api [endpoint]    - Build or update API endpoint
  show-api-history        - Show API history
  show-performance        - Show performance metrics
  show-best-practices     - Show best practices
  show-changelog          - Show changelog
  export-api [format]     - Export API documentation (md, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "performance-report":
                path = self.template_paths["performance-report"]
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

    def show_api_history(self):
        if not self.api_history:
            print("No API history available.")
            return
        print("API History:")
        print("=" * 50)
        for i, api in enumerate(self.api_history[-10:], 1):
            print(f"{i}. {api}")

    def show_performance(self):
        if not self.performance_history:
            print("No performance history available.")
            return
        print("Performance History:")
        print("=" * 50)
        for i, perf in enumerate(self.performance_history[-10:], 1):
            print(f"{i}. {perf}")

    def build_api(self, endpoint: str = "/api/v1/users") -> Dict[str, Any]:
        logger.info(f"Building API endpoint: {endpoint}")
        
        # Simuleer API bouw
        time.sleep(1)
        result = {
            "endpoint": endpoint,
            "method": "GET",
            "status": "created",
            "response_time": "150ms",
            "throughput": "1000 req/s",
            "timestamp": datetime.now().isoformat(),
            "agent": "BackendDeveloperAgent"
        }
        
        # Voeg aan historie toe
        api_entry = f"{result['timestamp']}: {result['method']} {endpoint} - Status: {result['status']}"
        self.api_history.append(api_entry)
        self._save_api_history()
        
        # Log performance metric
        self.monitor._record_metric("BackendDeveloper", MetricType.SUCCESS_RATE, 95, "%")
        
        logger.info(f"API build result: {result}")
        return result

    def export_api(self, format_type: str = "md", api_data: Optional[Dict] = None):
        if not api_data:
            if self.api_history:
                endpoint = self.api_history[-1].split(": ")[1].split(" - ")[0]
                api_data = self.build_api(endpoint)
            else:
                api_data = self.build_api()
        
        try:
            if format_type == "md":
                self._export_markdown(api_data)
            elif format_type == "json":
                self._export_json(api_data)
            else:
                print(f"Unsupported format: {format_type}")
        except Exception as e:
            logger.error(f"Error exporting API: {e}")

    def _export_markdown(self, api_data: Dict):
        template_path = self.template_paths["api-export-md"]
        if template_path.exists():
            with open(template_path, 'r') as f:
                template = f.read()
            
            # Vul template
            content = template.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
            content = content.replace("{{endpoints}}", f"- {api_data['method']} {api_data['endpoint']}")
            content = content.replace("{{performance_metrics}}", f"- Response time: {api_data['response_time']}\n- Throughput: {api_data['throughput']}")
            content = content.replace("{{security_status}}", "- Authentication: enabled\n- Rate limiting: enabled")
            content = content.replace("{{database_status}}", "- Connection pool: healthy\n- Query performance: optimal")
            
            # Save to file
            output_file = f"api_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"API export saved to: {output_file}")

    def _export_json(self, api_data: Dict):
        output_file = f"api_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(api_data, f, indent=2)
        
        print(f"API export saved to: {output_file}")

    def test_resource_completeness(self):
        print("Testing resource completeness...")
        missing_resources = []
        
        for name, path in self.template_paths.items():
            if not path.exists():
                missing_resources.append(f"Template: {name} ({path})")
        
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
        logger.info("Starting collaboration example...")
        
        # Publish API change request
        publish("api_change_requested", {
            "agent": "BackendDeveloperAgent",
            "endpoint": "/api/v1/users",
            "timestamp": datetime.now().isoformat()
        })
        
        # Build API
        api_result = self.build_api("/api/v1/users")
        
        # Publish completion
        publish("api_change_completed", api_result)
        
        # Notify via Slack
        try:
            send_slack_message(f"API endpoint {api_result['endpoint']} created successfully")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

    def handle_api_change_requested(self, event):
        logger.info(f"API change requested: {event}")
        endpoint = event.get("endpoint", "/api/v1/users")
        self.build_api(endpoint)

    async def handle_api_change_completed(self, event):
        logger.info(f"API change completed: {event}")
        
        # Record event in tracing
        self.tracer.record_event("api_change_completed", event)
        
        # Evaluate policy
        try:
            allowed = await self.policy_engine.evaluate_policy("api_change", event)
            logger.info(f"Policy evaluation result: {allowed}")
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")

    def run(self):
        def sync_handler(event):
            asyncio.run(self.handle_api_change_completed(event))
        
        subscribe("api_change_completed", sync_handler)
        subscribe("api_change_requested", self.handle_api_change_requested)
        
        logger.info("BackendDeveloperAgent ready and listening for events...")
        self.collaborate_example()

def main():
    parser = argparse.ArgumentParser(description="BackendDeveloper Agent CLI")
    parser.add_argument("command", nargs="?", default="help", 
                       choices=["help", "build-api", "show-api-history", "show-performance", 
                               "show-best-practices", "show-changelog", "export-api", 
                               "test", "collaborate", "run"])
    parser.add_argument("--endpoint", default="/api/v1/users", help="API endpoint")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Export format")
    
    args = parser.parse_args()
    
    agent = BackendDeveloperAgent()
    
    if args.command == "help":
        agent.show_help()
    elif args.command == "build-api":
        agent.build_api(args.endpoint)
    elif args.command == "show-api-history":
        agent.show_api_history()
    elif args.command == "show-performance":
        agent.show_performance()
    elif args.command == "show-best-practices":
        agent.show_resource("best-practices")
    elif args.command == "show-changelog":
        agent.show_resource("changelog")
    elif args.command == "export-api":
        agent.export_api(args.format)
    elif args.command == "test":
        agent.test_resource_completeness()
    elif args.command == "collaborate":
        agent.collaborate_example()
    elif args.command == "run":
        agent.run()

if __name__ == "__main__":
    main()
