# AiDeveloper Agent

> **Let op:** Deze agent werkt actief samen met andere agents via een centrale message bus en gedeelde context in Supabase. Zie de sectie 'Samenwerking & Contextdeling' hieronder voor details.

# AI Developer Output & Best Practices

## Voorbeeld Prompt Template

```markdown
**Prompt:**  
Je bent een behulpzame AI-assistent. Beantwoord de vraag zo duidelijk mogelijk.

**Input:**  
Wat is het verschil tussen supervised en unsupervised learning?

**Output:**  
Supervised learning gebruikt gelabelde data, unsupervised learning niet.
```

---

## Voorbeeld Langchain Pipeline

```python
from langchain.chains import LLMChain
from langchain.llms import OpenAI

llm = OpenAI(model_name="gpt-4")
chain = LLMChain(llm=llm, prompt="{input}")
result = chain.run(input="Leg uit wat vector search is.")
```

---

## Voorbeeld Vector Search (pgvector)

```python
import psycopg2
conn = psycopg2.connect(...)
cur = conn.cursor()
cur.execute("SELECT * FROM documents ORDER BY embedding <-> %s LIMIT 5", (query_embedding,))
```

---

## Voorbeeld AI Endpoint (FastAPI)

```python
@app.post("/ai/answer")
def ai_answer(query: str):
    return {"answer": llm_chain.run(input=query)}
```

---

## Voorbeeld Evaluatie Rapport

```markdown
### Evaluatie: Sentiment Classifier v2

- Accuracy: 91%
- Precision: 0.89
- Recall: 0.93
- F1-score: 0.91
- Drift: geen significante drift waargenomen
```

---

## Voorbeeld Model Card

```markdown
**Model:** Sentiment Classifier v2  
**Doel:** Sentimentanalyse op support tickets  
**Data:** 10k gelabelde tickets (2023)  
**Performance:** Accuracy 91%, F1-score 0.91  
**Beperkingen:** Bias richting positieve tickets, matig op sarcasme  
**Retraining:** Elke maand bij nieuwe data
```

---

## Voorbeeld Prompt Evaluatie Matrix

| Prompt | Output | Score (1-5) |
|--------|--------|-------------|
| Wat is AI? | Kunstmatige intelligentie is... | 5 |
| Leg uit: vector search | Vector search zoekt... | 4 |

---

## Voorbeeld ETL Pipeline (Prefect)

```python
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
```

---

## Voorbeeld Explainability Output (SHAP)

```python
import shap
explainer = shap.Explainer(model)
shap_values = explainer(X_test)
shap.summary_plot(shap_values, X_test)
```

---

## Voorbeeld Bias/Fairness Checklist

- [x] Dataset gecontroleerd op class imbalance
- [ ] Fairness metrics (demographic parity, equal opportunity) berekend
- [ ] Bias mitigatie toegepast indien nodig

---

## Best Practices
- Gebruik experiment tracking (MLflow/W&B) voor alle runs
- Automatiseer model evaluatie en retraining waar mogelijk
- Documenteer alle modelkeuzes, prompt iteraties en experimenten
- Monitor AI endpoints op latency, errors én drift
- Werk samen met Data, Dev, Security voor end-to-end kwaliteit

## Samenwerking & Contextdeling

Deze agent werkt samen met andere agents via een centrale message bus en gedeelde context in Supabase.

- **Events publiceren:** De agent kan events publiceren via de message_bus, bijvoorbeeld als een AI pipeline gereed is.
- **Context delen:** Status en relevante data worden gedeeld via Supabase, zodat andere agents deze kunnen inzien.

**Voorbeeld:**
```python
self.collaborate_example()
```
Dit publiceert een event en slaat context op. Andere agents kunnen deze context ophalen of op het event reageren.

---

## Changelog & Opschoning
- [2024-07-22] Duplicaten aideveloper.md, aideveloper.py, aideveloper.yaml verwijderd. Documentatie, code en configuratie nu centraal in aidev.md, aidev.py, aidev.yaml.
