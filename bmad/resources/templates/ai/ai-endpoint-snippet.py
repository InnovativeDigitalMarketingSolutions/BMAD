# AI Endpoint Snippet (FastAPI)

from fastapi import FastAPI

app = FastAPI()

@app.post("/ai/answer")
def ai_answer(query: str):
    return {"answer": llm_chain.run(input=query)}
