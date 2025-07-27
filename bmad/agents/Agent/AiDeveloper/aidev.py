#!/usr/bin/env python3
"""
AI Developer Agent voor CoPilot AI Business Suite
Implementeert en integreert AI/ML-functionaliteit. Output in prompt templates, code snippets, evaluatierapporten en experiment logs.
"""

import argparse
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import textwrap

from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import save_context, get_context
from bmad.agents.core.ai.llm_client import ask_openai


class AiDeveloperAgent:
    def __init__(self):
        pass

    def build_pipeline(self):
        print(
            textwrap.dedent(
                """
        from langchain.chains import LLMChain
        from langchain.llms import OpenAI

        llm = OpenAI(model_name="gpt-4")
        chain = LLMChain(llm=llm, prompt="{input}")
        result = chain.run(input="Leg uit wat vector search is.")
        """
            )
        )

    def prompt_template(self):
        print(
            textwrap.dedent(
                """
        **Prompt:**
        Je bent een behulpzame AI-assistent. Beantwoord de vraag zo duidelijk mogelijk.

        **Input:**
        Wat is het verschil tussen supervised en unsupervised learning?

        **Output:**
        Supervised learning gebruikt gelabelde data, unsupervised learning niet.
        """
            )
        )

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
        print(
            textwrap.dedent(
                """
        ### Evaluatie: Sentiment Classifier v2
        - Accuracy: 91%
        - Precision: 0.89
        - Recall: 0.93
        - F1-score: 0.91
        - Drift: geen significante drift waargenomen
        """
            )
        )

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
        # AI Code/Pipeline Review
        - [x] Prompt engineering getest
        - [x] Modelkeuze onderbouwd
        - [ ] Evaluatie met edge cases
        - [ ] Monitoring ingericht
        """
            )
        )

    def blockers(self):
        print(
            textwrap.dedent(
                """
        # Blockers
        - Onvoldoende trainingsdata voor sentiment analyse
        - API key limieten bij OpenAI
        """
            )
        )

    # --- Uitbreidingen hieronder ---
    def build_etl_pipeline(self):
        print(
            textwrap.dedent(
                """
        from prefect import flow, task

        @task
        def extract():
            # Data extractie
            pass

        @task
        def transform(data):
            # Data cleaning/feature engineering
            pass

        @task
        def load(data):
            # Data laden in database
            pass

        @flow
        def etl_flow():
            data = extract()
            clean = transform(data)
            load(clean)
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
        **Retraining:** Elke maand bij nieuwe data
        """
            )
        )

    def prompt_eval(self):
        print(
            textwrap.dedent(
                """
        | Prompt | Output | Score (1-5) |
        |--------|--------|-------------|
        | Wat is AI? | Kunstmatige intelligentie is... | 5 |
        | Leg uit: vector search | Vector search zoekt... | 4 |
        """
            )
        )

    def retrain(self):
        print(
            textwrap.dedent(
                """
        # Retraining Trigger
        - Data drift gedetecteerd: retraining gestart
        - Nieuwe data toegevoegd aan trainingset
        - Model opnieuw gevalideerd en gedeployed
        """
            )
        )

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        publish("ai_pipeline_ready", {"status": "success", "agent": "AiDeveloper"})
        save_context("AiDeveloper", {"pipeline_status": "ready"})
        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("AiDeveloper")
        print(f"Opgehaalde context: {context}")

    def show_help(self):
        print(
            """
Beschikbare commando's:
- build-pipeline
- prompt-template
- vector-search
- ai-endpoint
- evaluate
- experiment-log
- monitoring
- doc
- review
- blockers
- build-etl-pipeline
- deploy-model
- version-model
- auto-evaluate
- bias-check
- explain
- model-card
- prompt-eval
- retrain
- collaborate-example
- help
        """
        )

    def run(self, command):
        commands = {
            "build-pipeline": self.build_pipeline,
            "prompt-template": self.prompt_template,
            "vector-search": self.vector_search,
            "ai-endpoint": self.ai_endpoint,
            "evaluate": self.evaluate,
            "experiment-log": self.experiment_log,
            "monitoring": self.monitoring,
            "doc": self.doc,
            "review": self.review,
            "blockers": self.blockers,
            "build-etl-pipeline": self.build_etl_pipeline,
            "deploy-model": self.deploy_model,
            "version-model": self.version_model,
            "auto-evaluate": self.auto_evaluate,
            "bias-check": self.bias_check,
            "explain": self.explain,
            "model-card": self.model_card,
            "prompt-eval": self.prompt_eval,
            "retrain": self.retrain,
            "collaborate-example": self.collaborate_example,
            "help": self.show_help,
        }
        func = commands.get(command)
        if func:
            func()
        else:
            print(f"❌ Onbekend commando: {command}")
            self.show_help()

    def ask_llm(self, prompt):
        """Stuur een prompt naar de LLM (OpenAI) en print het antwoord."""
        result = ask_openai(prompt)
        print(f"[LLM Antwoord]: {result}")


def main():
    parser = argparse.ArgumentParser(description="AI Developer Agent")
    parser.add_argument("command", help="Commando om uit te voeren")
    args = parser.parse_args()
    agent = AiDeveloperAgent()
    agent.run(args.command)


if __name__ == "__main__":
    main()
