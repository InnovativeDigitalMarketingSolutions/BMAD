#!/usr/bin/env python3
"""
AI Developer Agent voor CoPilot AI Business Suite
Implementeert en integreert AI/ML-functionaliteit met geavanceerde monitoring en policy management.
Output in prompt templates, code snippets, evaluatierapporten en experiment logs.
"""

import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import asyncio
import json
import logging
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from bmad.agents.core.agent.agent_performance_monitor import (
    MetricType,
    get_performance_monitor,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from integrations.slack.slack_notify import send_slack_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class AiDevelopmentError(Exception):
    """Custom exception for AI development-related errors."""
    pass

class AiValidationError(AiDevelopmentError):
    """Exception for AI development validation failures."""
    pass

class AiDeveloperAgent:
    def __init__(self):
        # Set agent name
        self.agent_name = "AiDeveloper"
        # Initialize core services
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/ai/best-practices.md",
            "prompt-template": self.resource_base / "templates/ai/prompt-template.md",
            "ai-endpoint": self.resource_base / "templates/ai/ai-endpoint-snippet.py",
            "model-card": self.resource_base / "templates/ai/model-card-template.md",
            "evaluation-report": self.resource_base / "templates/ai/evaluation-report-template.md",
            "experiment-log": self.resource_base / "templates/ai/experiment-log-template.md",
            "bias-check": self.resource_base / "templates/ai/bias-check-template.md",
            "explainability": self.resource_base / "templates/ai/explainability-template.md",
            "ai-review": self.resource_base / "templates/ai/ai-review-checklist.md",
            "ai-doc": self.resource_base / "templates/ai/ai-doc-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/ai/ai-changelog.md",
            "experiment-history": self.resource_base / "data/ai/experiment-history.md",
            "model-history": self.resource_base / "data/ai/model-history.md"
        }

        # Initialize histories
        self.experiment_history = []
        self.model_history = []
        self._load_experiment_history()
        self._load_model_history()

        # AI-specific attributes
        self.ai_models = {}
        self.experiment_configs = {}
        self.model_performance_metrics = {}

    def _validate_input(self, value: Any, expected_type: type, param_name: str) -> None:
        """Validate input parameters with type checking."""
        if not isinstance(value, expected_type):
            raise AiValidationError(
                f"Invalid type for {param_name}: expected {expected_type.__name__}, got {type(value).__name__}"
            )

    def _validate_model_name(self, model_name: str) -> None:
        """Validate AI model name parameter."""
        self._validate_input(model_name, str, "model_name")
        if not model_name.strip():
            raise AiValidationError("Model name cannot be empty")
        if len(model_name) > 100:
            raise AiValidationError("Model name cannot exceed 100 characters")
        if not model_name.replace("_", "").replace("-", "").isalnum():
            raise AiValidationError("Model name can only contain alphanumeric characters, underscores, and hyphens")

    def _validate_prompt(self, prompt: str) -> None:
        """Validate AI prompt parameter."""
        self._validate_input(prompt, str, "prompt")
        if not prompt.strip():
            raise AiValidationError("Prompt cannot be empty")
        if len(prompt) > 10000:
            raise AiValidationError("Prompt cannot exceed 10,000 characters")

    def _validate_experiment_data(self, experiment_data: Dict[str, Any]) -> None:
        """Validate experiment data parameter."""
        self._validate_input(experiment_data, dict, "experiment_data")
        
        required_fields = ["name", "model", "dataset"]
        for field in required_fields:
            if field not in experiment_data:
                raise AiValidationError(f"Missing required field: {field}")
        
        # Validate experiment name
        if not experiment_data.get("name", "").strip():
            raise AiValidationError("Experiment name cannot be empty")

    def _record_ai_metric(self, metric_name: str, value: float, unit: str = "%") -> None:
        """Record AI-specific metrics."""
        try:
            self.monitor._record_metric("AiDeveloper", MetricType.SUCCESS_RATE, value, unit)
            logger.info(f"AI metric recorded: {metric_name} = {value}{unit}")
        except Exception as e:
            logger.error(f"Failed to record AI metric: {e}")

    def _assess_model_performance(self, metrics: Dict[str, Any]) -> str:
        """Assess model performance based on metrics."""
        if not metrics:
            return "unknown"
        
        accuracy = metrics.get("accuracy", 0)
        latency = metrics.get("latency", float('inf'))
        
        if accuracy >= 0.95 and latency < 100:
            return "excellent"
        elif accuracy >= 0.90 and latency < 500:
            return "good"
        elif accuracy >= 0.80 and latency < 1000:
            return "fair"
        elif accuracy >= 0.70:
            return "poor"
        else:
            return "critical"

    def _generate_ai_recommendations(self, performance_data: Dict[str, Any]) -> list:
        """Generate AI development recommendations based on performance data."""
        recommendations = [
            "Implement comprehensive model monitoring",
            "Add automated retraining pipelines",
            "Establish model versioning strategy",
            "Implement A/B testing framework",
            "Add bias detection and fairness monitoring"
        ]
        
        performance_level = performance_data.get("performance_level", "unknown")
        if performance_level == "critical":
            recommendations.extend([
                "Immediate model retraining required",
                "Review data quality and preprocessing",
                "Consider alternative model architectures"
            ])
        elif performance_level == "poor":
            recommendations.extend([
                "Optimize model hyperparameters",
                "Increase training data quality",
                "Implement feature engineering improvements"
            ])
        elif performance_level == "excellent":
            recommendations.extend([
                "Maintain current model performance",
                "Consider model compression for deployment",
                "Implement advanced monitoring for edge cases"
            ])
        
        return list(set(recommendations))  # Remove duplicates

    def _load_experiment_history(self):
        try:
            if self.data_paths["experiment-history"].exists():
                with open(self.data_paths["experiment-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.experiment_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load experiment history: {e}")

    def _save_experiment_history(self):
        try:
            self.data_paths["experiment-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["experiment-history"], "w") as f:
                f.write("# Experiment History\n\n")
                f.writelines(f"- {exp}\n" for exp in self.experiment_history[-50:])
        except Exception as e:
            logger.error(f"Could not save experiment history: {e}")

    def _load_model_history(self):
        try:
            if self.data_paths["model-history"].exists():
                with open(self.data_paths["model-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.model_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load model history: {e}")

    def _save_model_history(self):
        try:
            self.data_paths["model-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["model-history"], "w") as f:
                f.write("# Model History\n\n")
                f.writelines(f"- {model}\n" for model in self.model_history[-50:])
        except Exception as e:
            logger.error(f"Could not save model history: {e}")

    def show_help(self):
        help_text = """
AiDeveloper Agent Commands:
  help                    - Show this help message
  build-pipeline          - Build or update AI/LLM pipeline
  prompt-template         - Design or test prompt template
  vector-search           - Implement or tune vector search
  ai-endpoint             - Build AI inference endpoint
  evaluate                - Test and evaluate AI component
  experiment-log          - Log experiments and model choices
  monitoring              - Set up monitoring and drift detection
  doc                     - Generate AI architecture documentation
  review                  - Review AI code or pipeline
  blockers                - Report blockers or dependencies
  build-etl-pipeline      - Build or update ETL/ELT pipeline
  deploy-model            - Deploy AI model as API endpoint
  version-model           - Version control of models
  auto-evaluate           - Perform automatic evaluation
  bias-check              - Analyze bias and fairness
  explain                 - Generate explainability output
  model-card              - Generate model card
  prompt-eval             - Evaluate prompts in matrix form
  retrain                 - Trigger automatic retraining
  show-experiment-history - Show experiment history
  show-model-history      - Show model history
  show-best-practices     - Show best practices
  show-changelog          - Show changelog
  export-report [format]  - Export report (md, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "prompt-template":
                path = self.template_paths["prompt-template"]
            elif resource_type == "ai-endpoint":
                path = self.template_paths["ai-endpoint"]
            elif resource_type == "model-card":
                path = self.template_paths["model-card"]
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

    def show_experiment_history(self):
        if not self.experiment_history:
            print("No experiment history available.")
            return
        print("Experiment History:")
        print("=" * 50)
        for i, exp in enumerate(self.experiment_history[-10:], 1):
            print(f"{i}. {exp}")

    def show_model_history(self):
        if not self.model_history:
            print("No model history available.")
            return
        print("Model History:")
        print("=" * 50)
        for i, model in enumerate(self.model_history[-10:], 1):
            print(f"{i}. {model}")

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        if not report_data:
            report_data = {
                "model": "Sentiment Classifier v2",
                "accuracy": 91.0,
                "precision": 0.89,
                "recall": 0.93,
                "f1_score": 0.91,
                "experiments_run": 15,
                "models_deployed": 3,
                "timestamp": datetime.now().isoformat(),
                "agent": "AiDeveloperAgent"
            }

        try:
            if format_type == "md":
                self._export_markdown(report_data)
            elif format_type == "json":
                self._export_json(report_data)
            else:
                print(f"Unsupported format: {format_type}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")

    def _export_markdown(self, report_data: Dict):
        output_file = f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# AI Developer Report

## Summary
- **Model**: {report_data.get('model', 'N/A')}
- **Accuracy**: {report_data.get('accuracy', 0)}%
- **Precision**: {report_data.get('precision', 0)}
- **Recall**: {report_data.get('recall', 0)}
- **F1-Score**: {report_data.get('f1_score', 0)}
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Activity
- Experiments Run: {report_data.get('experiments_run', 0)}
- Models Deployed: {report_data.get('models_deployed', 0)}

## Performance Metrics
- Model Performance: {report_data.get('accuracy', 0)}%
- Training Time: {report_data.get('training_time', 'N/A')}
- Inference Latency: {report_data.get('inference_latency', 'N/A')}ms
"""

        with open(output_file, "w") as f:
            f.write(content)
        print(f"Report export saved to: {output_file}")

    def _export_json(self, report_data: Dict):
        output_file = f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"Report export saved to: {output_file}")

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
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        logger.info("Starting AI collaboration example...")

        # Publish AI development request
        publish("ai_development_requested", {
            "agent": "AiDeveloperAgent",
            "task": "Sentiment Analysis Model",
            "timestamp": datetime.now().isoformat()
        })

        # Build pipeline
        self.build_pipeline()

        # Evaluate model
        self.evaluate()

        # Publish completion
        publish("ai_development_completed", {
            "status": "success",
            "agent": "AiDeveloperAgent",
            "accuracy": 91.0
        })

        # Save context
        save_context("AiDeveloper", "status", {"model_status": "deployed"})

        # Notify via Slack
        try:
            send_slack_message("AI development completed with 91% accuracy")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("AiDeveloper")
        print(f"Opgehaalde context: {context}")

    def handle_ai_development_requested(self, event):
        logger.info(f"AI development requested: {event}")
        event.get("task", "Sentiment Analysis Model")
        self.build_pipeline()

    async def handle_ai_development_completed(self, event):
        logger.info(f"AI development completed: {event}")

        # Evaluate policy
        try:
            allowed = await self.policy_engine.evaluate_policy("ai_development", event)
            logger.info(f"Policy evaluation result: {allowed}")
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")

    def run(self):
        def sync_handler(event):
            asyncio.run(self.handle_ai_development_completed(event))

        subscribe("ai_development_completed", sync_handler)
        subscribe("ai_development_requested", self.handle_ai_development_requested)

        logger.info("AiDeveloperAgent ready and listening for events...")
        self.collaborate_example()

    # --- ORIGINELE FUNCTIONALITEIT BEHOUDEN ---
    def build_pipeline(self):
        """Build AI/ML pipeline with enhanced validation and intelligence."""
        try:
            logger.info("Building AI/ML pipeline")
            
            # Record start time for performance monitoring
            start_time = datetime.now()
            
            # Simulate pipeline building
            pipeline_result = {
                "pipeline_type": "AI/ML Pipeline",
                "status": "built",
                "components": [
                    "Data Preprocessing",
                    "Feature Engineering", 
                    "Model Training",
                    "Model Evaluation",
                    "Model Deployment"
                ],
                "configuration": {
                    "framework": "TensorFlow/PyTorch",
                    "compute": "GPU/CPU",
                    "scaling": "Auto-scaling enabled"
                },
                "performance_metrics": {
                    "build_time": "2.5 minutes",
                    "resource_usage": "Optimized",
                    "scalability": "High"
                },
                "recommendations": [],
                "timestamp": datetime.now().isoformat(),
                "agent": "AiDeveloper"
            }
            
            # Assess pipeline performance
            performance_level = self._assess_model_performance(pipeline_result["performance_metrics"])
            pipeline_result["performance_level"] = performance_level
            
            # Generate recommendations
            recommendations = self._generate_ai_recommendations(pipeline_result)
            pipeline_result["recommendations"] = recommendations
            
            # Record performance
            end_time = datetime.now()
            build_duration = (end_time - start_time).total_seconds()
            
            # Log performance metric
            self._record_ai_metric("pipeline_build_time", build_duration, "s")
            
            # Add to experiment history
            experiment_entry = f"{datetime.now().isoformat()}: AI/ML pipeline built successfully - Performance: {performance_level}"
            self.experiment_history.append(experiment_entry)
            self._save_experiment_history()
            
            logger.info(f"AI/ML pipeline built successfully: {pipeline_result}")
            
            return pipeline_result
            
        except Exception as e:
            logger.error(f"Error building AI/ML pipeline: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def prompt_template(self):
        """Generate AI prompt template with enhanced validation."""
        try:
            logger.info("Generating AI prompt template")
            
            # Simulate prompt template generation
            template_result = {
                "template_type": "AI Prompt Template",
                "status": "generated",
                "template": {
                    "system_prompt": "You are an AI assistant specialized in {domain}.",
                    "user_prompt": "Please {task} with the following context: {context}",
                    "examples": [
                        "Domain: Healthcare, Task: Diagnose symptoms",
                        "Domain: Finance, Task: Analyze market trends",
                        "Domain: Education, Task: Explain concepts"
                    ]
                },
                "best_practices": [
                    "Use clear and specific instructions",
                    "Include relevant context",
                    "Provide examples when possible",
                    "Set appropriate constraints"
                ],
                "validation_rules": [
                    "Prompt length: 50-1000 characters",
                    "Context inclusion: Required",
                    "Example count: 1-5 examples"
                ],
                "performance_metrics": {
                    "clarity_score": 95,
                    "specificity_score": 88,
                    "usability_score": 92
                },
                "recommendations": [],
                "timestamp": datetime.now().isoformat(),
                "agent": "AiDeveloper"
            }
            
            # Assess template performance
            performance_level = self._assess_model_performance(template_result["performance_metrics"])
            template_result["performance_level"] = performance_level
            
            # Generate recommendations
            recommendations = self._generate_ai_recommendations(template_result)
            template_result["recommendations"] = recommendations
            
            # Log performance metric
            self._record_ai_metric("prompt_template_quality", template_result["performance_metrics"]["clarity_score"], "%")
            
            logger.info(f"AI prompt template generated: {template_result}")
            
            return template_result
            
        except Exception as e:
            logger.error(f"Error generating prompt template: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def vector_search(self):
        print(
            textwrap.dedent(
                """
        import psycopg2
        conn = psycopg2.connect(...)
        cur = conn.cursor()
        cur.execute("SELECT * FROM documents ORDER BY embedding <-> %s LIMIT 5", (query_embedding,))
        """
            )
        )

    def ai_endpoint(self):
        print(
            textwrap.dedent(
                """
        @app.post("/ai/answer")
        def ai_answer(query: str):
            return {"answer": llm_chain.run(input=query)}
        """
            )
        )

    def evaluate(self):
        """Evaluate AI model with enhanced validation and intelligence."""
        try:
            logger.info("Evaluating AI model")
            
            # Simulate model evaluation
            evaluation_result = {
                "evaluation_type": "AI Model Evaluation",
                "status": "completed",
                "metrics": {
                    "accuracy": 0.92,
                    "precision": 0.89,
                    "recall": 0.94,
                    "f1_score": 0.91,
                    "latency": 150,
                    "throughput": 1000
                },
                "performance_analysis": {
                    "overall_score": 91,
                    "strengths": ["High accuracy", "Good recall", "Low latency"],
                    "weaknesses": ["Moderate precision", "Room for optimization"]
                },
                "recommendations": [],
                "timestamp": datetime.now().isoformat(),
                "agent": "AiDeveloper"
            }
            
            # Assess model performance
            performance_level = self._assess_model_performance(evaluation_result["metrics"])
            evaluation_result["performance_level"] = performance_level
            
            # Generate recommendations
            recommendations = self._generate_ai_recommendations(evaluation_result)
            evaluation_result["recommendations"] = recommendations
            
            # Log performance metric
            self._record_ai_metric("model_evaluation_score", evaluation_result["performance_analysis"]["overall_score"], "%")
            
            # Add to model history
            model_entry = f"{datetime.now().isoformat()}: Model evaluation completed - Score: {evaluation_result['performance_analysis']['overall_score']}%"
            self.model_history.append(model_entry)
            self._save_model_history()
            
            logger.info(f"AI model evaluation completed: {evaluation_result}")
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error evaluating AI model: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def experiment_log(self):
        print(
            textwrap.dedent(
                """
        ### Experiment Log
        - Model: gpt-4
        - Prompt: "Leg uit wat vector search is."
        - Resultaat: "Vector search zoekt op basis van semantische gelijkenis."
        - Opmerkingen: Werkt goed voor korte vragen, minder voor lange contexten.
        """
            )
        )

    def monitoring(self):
        print(
            textwrap.dedent(
                """
        # Monitoring & Drift Detectie
        - Log inference requests en responses
        - Monitor latency en foutpercentages
        - Detecteer concept drift met periodieke evaluatie
        """
            )
        )

    def doc(self):
        print(
            textwrap.dedent(
                """
        # AI Architectuur Documentatie
        - LLM pipeline: Langchain + OpenAI
        - Vector search: pgvector in Supabase
        - Endpoints: FastAPI
        - Monitoring: Prometheus, custom logs
        """
            )
        )

    def review(self):
        print(
            textwrap.dedent(
                """
        # AI Code Review
        - [x] Prompt engineering best practices
        - [x] Model performance monitoring
        - [ ] Bias detection geïmplementeerd
        - [ ] Explainability tools toegevoegd
        """
            )
        )

    def blockers(self):
        print(
            textwrap.dedent(
                """
        # Blockers
        - GPU resources beperkt voor training
        - Data labeling pipeline niet geautomatiseerd
        """
            )
        )

    def build_etl_pipeline(self):
        print(
            textwrap.dedent(
                """
        # ETL Pipeline voor AI Data
        from prefect import task, flow
        
        @task
        def extract_data():
            # Extract data from sources
            pass
            
        @task
        def transform_data():
            # Transform and clean data
            pass
            
        @task
        def load_data():
            # Load to vector database
            pass
            
        @flow
        def etl_pipeline():
            raw_data = extract_data()
            clean_data = transform_data()
            load_data(clean_data)
        """
            )
        )

    def deploy_model(self):
        print(
            textwrap.dedent(
                """
        # Model deployment (FastAPI + MLflow/BentoML)
        @app.post("/predict")
        def predict(input: InputData):
            prediction = model.predict(input)
            return {"prediction": prediction}
        """
            )
        )

    def version_model(self):
        print(
            textwrap.dedent(
                """
        # Model versioning (MLflow)
        import mlflow
        mlflow.set_experiment("sentiment-analysis")
        with mlflow.start_run():
            mlflow.log_param("model_type", "bert")
            mlflow.log_metric("accuracy", 0.91)
            mlflow.sklearn.log_model(model, "model")
        """
            )
        )

    def auto_evaluate(self):
        print(
            textwrap.dedent(
                """
        # Automatische evaluatie
        def evaluate(model, X_test, y_test):
            preds = model.predict(X_test)
            acc = accuracy_score(y_test, preds)
            print(f"Accuracy: {acc:.2f}")
        """
            )
        )

    def bias_check(self):
        print(
            textwrap.dedent(
                """
        # Bias/Fairness check
        - [x] Dataset gecontroleerd op class imbalance
        - [ ] Fairness metrics (demographic parity, equal opportunity) berekend
        - [ ] Bias mitigatie toegepast indien nodig
        """
            )
        )

    def explain(self):
        print(
            textwrap.dedent(
                """
        # Explainability (SHAP)
        import shap
        explainer = shap.Explainer(model)
        shap_values = explainer(X_test)
        shap.summary_plot(shap_values, X_test)
        """
            )
        )

    def model_card(self):
        print(
            textwrap.dedent(
                """
        **Model:** Sentiment Classifier v2  
        **Doel:** Sentimentanalyse op support tickets  
        **Data:** 10k gelabelde tickets (2023)  
        **Performance:** Accuracy 91%, F1-score 0.91  
        **Beperkingen:** Bias richting positieve tickets, matig op sarcasme  
        **Retraining:** Elke maand
        """
            )
        )

    def prompt_eval(self):
        print(
            textwrap.dedent(
                """
        # Prompt Evaluatie Matrix
        | Prompt | Accuracy | Latency | Cost |
        |--------|----------|---------|------|
        | GPT-4  | 91%      | 2.3s    | $0.03|
        | GPT-3.5| 87%      | 1.8s    | $0.01|
        """
            )
        )

    def retrain(self):
        print(
            textwrap.dedent(
                """
        # Automatische Retraining
        - Trigger: Elke maand of bij drift detectie
        - Data: Nieuwe gelabelde tickets
        - Evaluation: A/B test met huidige model
        - Deployment: Gradual rollout
        """
            )
        )

def main():
    parser = argparse.ArgumentParser(description="AiDeveloper Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "build-pipeline", "prompt-template", "vector-search", "ai-endpoint",
                               "evaluate", "experiment-log", "monitoring", "doc", "review", "blockers",
                               "build-etl-pipeline", "deploy-model", "version-model", "auto-evaluate",
                               "bias-check", "explain", "model-card", "prompt-eval", "retrain",
                               "show-experiment-history", "show-model-history", "show-best-practices",
                               "show-changelog", "export-report", "test", "collaborate", "run"])
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Export format")

    args = parser.parse_args()

    agent = AiDeveloperAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "build-pipeline":
        agent.build_pipeline()
    elif args.command == "prompt-template":
        agent.prompt_template()
    elif args.command == "vector-search":
        agent.vector_search()
    elif args.command == "ai-endpoint":
        agent.ai_endpoint()
    elif args.command == "evaluate":
        agent.evaluate()
    elif args.command == "experiment-log":
        agent.experiment_log()
    elif args.command == "monitoring":
        agent.monitoring()
    elif args.command == "doc":
        agent.doc()
    elif args.command == "review":
        agent.review()
    elif args.command == "blockers":
        agent.blockers()
    elif args.command == "build-etl-pipeline":
        agent.build_etl_pipeline()
    elif args.command == "deploy-model":
        agent.deploy_model()
    elif args.command == "version-model":
        agent.version_model()
    elif args.command == "auto-evaluate":
        agent.auto_evaluate()
    elif args.command == "bias-check":
        agent.bias_check()
    elif args.command == "explain":
        agent.explain()
    elif args.command == "model-card":
        agent.model_card()
    elif args.command == "prompt-eval":
        agent.prompt_eval()
    elif args.command == "retrain":
        agent.retrain()
    elif args.command == "show-experiment-history":
        agent.show_experiment_history()
    elif args.command == "show-model-history":
        agent.show_model_history()
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
