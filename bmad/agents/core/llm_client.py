import os
import requests
import hashlib
import json
import logging

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
CACHE_DIR = os.getenv("LLM_CACHE_DIR", ".llm_cache")

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_key(prompt, model, temperature, max_tokens):
    key = json.dumps({"prompt": prompt, "model": model, "temperature": temperature, "max_tokens": max_tokens}, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()

def ask_openai(prompt, model=None, temperature=0.7, max_tokens=512, structured_output=None):
    """
    Stuur een prompt naar OpenAI en ontvang het antwoord. Optioneel structured_output (JSON schema/voorbeeld).
    :param prompt: De prompttekst (str)
    :param model: Modelnaam (str, default uit .env of 'gpt-4.1-nano')
    :param temperature: Creativiteit (float)
    :param max_tokens: Maximaal aantal tokens in antwoord (int)
    :param structured_output: Optioneel, string met JSON schema/voorbeeld
    :return: Antwoord van de LLM (str of dict)
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY niet gezet in environment!")
    if structured_output:
        prompt += f"\nGeef het antwoord als geldige JSON volgens dit voorbeeld:\n{structured_output}"
    model = model or OPENAI_MODEL
    cache_key = _cache_key(prompt, model, temperature, max_tokens)
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            cached = json.load(f)
        logging.info(f"[LLM][CACHE HIT] {prompt[:60]}...")
        return cached["answer"]
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    logging.info(f"[LLM][REQUEST] {prompt[:60]}... [model={model}]")
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"]
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump({"prompt": prompt, "answer": answer}, f)
    logging.info(f"[LLM][RESPONSE] {answer[:60]}...")
    # Probeer JSON te parsen als structured_output is opgegeven
    if structured_output:
        try:
            return json.loads(answer)
        except Exception:
            return answer
    return answer 