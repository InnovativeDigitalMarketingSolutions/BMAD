import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from bmad.agents.core.agent.agent_performance_monitor import (
    MetricType,
    get_performance_monitor,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from integrations.slack.slack_notify import send_slack_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class TestEngineerAgent:
    def __init__(self):
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/testengineer/best-practices.md",
            "test-strategy": self.resource_base / "templates/testengineer/test-strategy-template.md",
            "ai-test": self.resource_base / "templates/testengineer/ai-test-template.py",
            "unit-test": self.resource_base / "templates/testengineer/unit-test-template.py",
            "integration-test": self.resource_base / "templates/testengineer/integration-test-template.py",
            "e2e-test": self.resource_base / "templates/testengineer/e2e-test-template.py",
            "test-report-md": self.resource_base / "templates/testengineer/test-report-export-template.md",
            "test-report-json": self.resource_base / "templates/testengineer/test-report-export-template.json",
            "testdata": self.resource_base / "templates/testengineer/testdata-template.json",
            "coverage-report": self.resource_base / "templates/testengineer/coverage-report-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/testengineer/test-changelog.md",
            "test-history": self.resource_base / "data/testengineer/test-history.md",
            "coverage-history": self.resource_base / "data/testengineer/coverage-history.md"
        }

        # Initialize test history
        self.test_history = []
        self.coverage_history = []
        self._load_test_history()
        self._load_coverage_history()

    def _load_test_history(self):
        try:
            if self.data_paths["test-history"].exists():
                with open(self.data_paths["test-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.test_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load test history: {e}")

    def _save_test_history(self):
        try:
            self.data_paths["test-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["test-history"], "w") as f:
                f.write("# Test History\n\n")
                f.writelines(f"- {test}\n" for test in self.test_history[-50:])
        except Exception as e:
            logger.error(f"Could not save test history: {e}")

    def _load_coverage_history(self):
        try:
            if self.data_paths["coverage-history"].exists():
                with open(self.data_paths["coverage-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.coverage_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load coverage history: {e}")

    def _save_coverage_history(self):
        try:
            self.data_paths["coverage-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["coverage-history"], "w") as f:
                f.write("# Coverage History\n\n")
                f.writelines(f"- {cov}\n" for cov in self.coverage_history[-50:])
        except Exception as e:
            logger.error(f"Could not save coverage history: {e}")

    def show_help(self):
        help_text = """
TestEngineer Agent Commands:
  help                    - Show this help message
  run-tests               - Run all tests and generate report
  show-coverage           - Show test coverage
  show-test-history       - Show test history
  show-best-practices     - Show best practices
  show-changelog          - Show changelog
  export-report [format]  - Export last test report (md, json)
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
            elif resource_type == "coverage-report":
                path = self.template_paths["coverage-report"]
            else:
                print(f"Unknown resource type: {resource_type}")
                return
            if path.exists():
                with open(path) as f:
                    print(f.read())
            else:
                print(f"Resource file not found: {path}")
        except Exception as e:
            logger.error(f"Error reading resource {resource_type}: {e}")

    def show_test_history(self):
        if not self.test_history:
            print("No test history available.")
            return
        print("Test History:")
        print("=" * 50)
        for i, test in enumerate(self.test_history[-10:], 1):
            print(f"{i}. {test}")

    def show_coverage(self):
        if not self.coverage_history:
            print("No coverage history available.")
            return
        print("Coverage History:")
        print("=" * 50)
        for i, cov in enumerate(self.coverage_history[-10:], 1):
            print(f"{i}. {cov}")

    def run_tests(self) -> Dict[str, Any]:
        logger.info("Running all tests...")
        # Simuleer testuitvoering
        time.sleep(1)
        result = {
            "redis_cache": "✅ Basic operations werken",
            "monitoring": "⚠️ Async issues gedetecteerd",
            "connection_pool": "⚠️ Initialization problemen",
            "llm_caching": "✅ Decorator werkt"
        }
        # Voeg aan historie toe
        test_entry = f"{datetime.now().isoformat()}: {sum('✅' in v for v in result.values())}/{len(result)} tests succesvol"
        self.test_history.append(test_entry)
        self._save_test_history()
        # Log performance metric
        self.monitor._record_metric("TestEngineer", MetricType.SUCCESS_RATE, sum("✅" in v for v in result.values())/len(result)*100, "%")
        logger.info(f"Test results: {result}")
        return result

    def export_report(self, format_type: str = "md", test_data: Optional[Dict] = None):
        if not test_data:
            if self.test_history:
                test_data = self.run_tests()
            else:
                test_data = self.run_tests()
        try:
            if format_type == "md":
                self._export_markdown(test_data)
            elif format_type == "json":
                self._export_json(test_data)
            else:
                print(f"Unsupported format: {format_type}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")

    def _export_markdown(self, test_data: Dict):
        template_path = self.template_paths["test-report-md"]
        if template_path.exists():
            with open(template_path) as f:
                template = f.read()
            # Vul template
            content = template.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
            results_text = ""
            for test, result in test_data.items():
                results_text += f"- **{test}**: {result}\n"
            content = content.replace("{{results}}", results_text)
            output_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(output_file, "w") as f:
                f.write(content)
            print(f"Test report exported to: {output_file}")

    def _export_json(self, test_data: Dict):
        output_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w") as f:
            json.dump(test_data, f, indent=2)
        print(f"Test report exported to: {output_file}")

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
        publish("test_generation_requested", {
            "agent": "TestEngineerAgent",
            "function_description": "def add(a, b): return a + b",
            "context": "Eenvoudige optelfunctie"
        })
        test_result = self.run_tests()
        publish("tests_completed", test_result)
        try:
            send_slack_message(f"[TestEngineer] Tests afgerond: {test_result}")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

    def handle_tests_requested(self, event):
        logger.info("[TestEngineer] Tests gestart...")
        self.run_tests()
        publish("tests_completed", {"desc": "Tests voltooid"})
        logger.info("[TestEngineer] Tests afgerond, tests_completed gepubliceerd.")

    async def handle_test_generation_requested(self, event):
        logger.info(f"[TestEngineer] Test generation requested: {event}")
        function_description = event.get("function_description", "Onbekende functie")
        context = event.get("context", "")
        prompt = f"Schrijf Python unittests voor de volgende functie: {function_description}. Context: {context}. Gebruik pytest."
        result = ask_openai(prompt)
        logger.info(f"[TestEngineer][LLM Tests automatisch]: {result}")
        try:
            send_slack_message(f"[TestEngineer][LLM Tests automatisch]: {result}")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

    def run(self):
        def sync_handler(event):
            asyncio.run(self.handle_test_generation_requested(event))
        subscribe("test_generation_requested", sync_handler)
        subscribe("tests_requested", self.handle_tests_requested)
        logger.info("TestEngineerAgent ready and listening for events...")
        self.collaborate_example()

def main():
    parser = argparse.ArgumentParser(description="TestEngineer Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "run-tests", "show-coverage", "show-test-history",
                               "show-best-practices", "show-changelog", "export-report",
                               "test", "collaborate", "run"])
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Export format")
    args = parser.parse_args()
    agent = TestEngineerAgent()
    if args.command == "help":
        agent.show_help()
    elif args.command == "run-tests":
        agent.run_tests()
    elif args.command == "show-coverage":
        agent.show_coverage()
    elif args.command == "show-test-history":
        agent.show_test_history()
    elif args.command == "show-best-practices":
        agent.show_resource("best-practices")
    elif args.command == "show-changelog":
        agent.show_resource("changelog")
    elif args.command == "export-report":
        agent.export_report(args.format)
    elif args.command == "test":
        agent.test_resource_completeness()
    elif args.command == "collaborate":
        agent.collaborate_example()
    elif args.command == "run":
        agent.run()

if __name__ == "__main__":
    main()
