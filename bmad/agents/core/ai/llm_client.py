import os, requests, hashlib, json, logging, time
from typing import Dict, Any, Optional
from copy import deepcopy
from bmad.agents.core.data.redis_cache import cache_llm_response

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
CACHE_DIR = os.getenv("LLM_CACHE_DIR", ".llm_cache")

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
os.makedirs(CACHE_DIR, exist_ok=True)

# --- Helper: file-cache fallback ---
def _file_cache_get(key: str) -> Optional[dict]:
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"[LLM][FILECACHE] Fout bij lezen: {e}")
    return None

def _file_cache_set(key: str, value: dict):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(value, f, indent=2)
    except Exception as e:
        logging.warning(f"[LLM][FILECACHE] Fout bij schrijven: {e}")

# --- Einde file-cache helpers ---

def _cache_key(prompt: str, model: str, temperature: float, max_tokens: int, logprobs: bool) -> str:
    key = json.dumps({
        "prompt": prompt, 
        "model": model, 
        "temperature": temperature, 
        "max_tokens": max_tokens,
        "logprobs": logprobs
    }, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()

def calculate_confidence_from_logprobs(logprobs_data: dict) -> float:
    if not logprobs_data:
        return 0.5
    try:
        total_logprob = 0
        token_count = 0
        for choice in logprobs_data.get("choices", []):
            for token in choice.get("logprobs", {}).get("content", []):
                if "logprob" in token:
                    total_logprob += token["logprob"]
                    token_count += 1
        if token_count == 0:
            return 0.5
        avg_logprob = total_logprob / token_count
        confidence = min(1.0, max(0.0, (avg_logprob + 2.0) / 2.0))
        return confidence
    except Exception as e:
        logging.warning(f"Error calculating confidence from logprobs: {e}")
        return 0.5

def assess_complexity(task_description: str) -> float:
    complexity_keywords = {
        "high": ["architect", "design", "security", "authentication", "deployment", "infrastructure", "database", "api"],
        "medium": ["integration", "testing", "optimization", "refactoring", "documentation"],
        "low": ["simple", "basic", "update", "fix", "minor", "small"]
    }
    task_lower = task_description.lower()
    complexity_score = 0.5
    high_count = sum(1 for keyword in complexity_keywords["high"] if keyword in task_lower)
    medium_count = sum(1 for keyword in complexity_keywords["medium"] if keyword in task_lower)
    low_count = sum(1 for keyword in complexity_keywords["low"] if keyword in task_lower)
    if high_count > 0:
        complexity_score = 0.8 + (high_count * 0.1)
    elif medium_count > 0:
        complexity_score = 0.5 + (medium_count * 0.1)
    elif low_count > 0:
        complexity_score = 0.2 + (low_count * 0.1)
    return min(1.0, complexity_score)

def assess_security_risk(output: str, context: Dict[str, Any]) -> float:
    security_keywords = [
        "password", "token", "key", "secret", "auth", "login", "admin", "root",
        "delete", "drop", "remove", "update", "modify", "change", "deploy"
    ]
    output_lower = output.lower()
    context_lower = str(context).lower()
    security_count = sum(1 for keyword in security_keywords if keyword in output_lower)
    context_security_count = sum(1 for keyword in security_keywords if keyword in context_lower)
    risk_score = min(1.0, (security_count + context_security_count) * 0.1)
    agent_type = context.get("agent", "").lower()
    if "security" in agent_type or "admin" in agent_type:
        risk_score = min(1.0, risk_score + 0.2)
    return risk_score

def get_agent_success_rate(agent_name: str) -> float:
    default_rates = {
        "ProductOwner": 0.92,
        "Architect": 0.89,
        "BackendDeveloper": 0.85,
        "FrontendDeveloper": 0.87,
        "FullstackDeveloper": 0.83,
        "TestEngineer": 0.90,
        "SecurityDeveloper": 0.88,
        "DevOpsInfra": 0.86
    }
    return default_rates.get(agent_name, 0.8)

def calculate_confidence(output: str, context: Dict[str, Any]) -> float:
    confidence = 0.0
    llm_confidence = context.get("llm_confidence", 0.5)
    confidence += llm_confidence * 0.3
    if "code" in output.lower() or "function" in output.lower():
        code_quality = 0.8 if "def " in output or "class " in output else 0.6
        confidence += code_quality * 0.2
    else:
        confidence += 0.7 * 0.2
    task_description = context.get("task", "")
    complexity = assess_complexity(task_description)
    confidence += (1 - complexity) * 0.2
    security_risk = assess_security_risk(output, context)
    confidence += (1 - security_risk) * 0.15
    agent_name = context.get("agent", "")
    agent_success_rate = get_agent_success_rate(agent_name)
    confidence += agent_success_rate * 0.15
    return min(confidence, 1.0)

@cache_llm_response
def ask_openai_with_confidence(
    prompt: str, 
    context: Optional[Dict[str, Any]] = None,
    model: Optional[str] = None, 
    temperature: float = 0.7, 
    max_tokens: int = 512, 
    structured_output: Optional[str] = None,
    include_logprobs: bool = True
) -> Dict[str, Any]:
    """
    Stuur een prompt naar OpenAI en ontvang antwoord met confidence scoring.
    Probeert Redis cache, valt terug op file-cache als Redis niet beschikbaar is.
    """
    # --- Extra validatie ---
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY niet gezet in environment!")
    if not isinstance(prompt, str) or not prompt:
        raise ValueError("Prompt moet een niet-lege string zijn.")
    if context is None:
        context = {}
    else:
        context = deepcopy(context)
    # --- Einde validatie ---
    if structured_output:
        prompt += f"\nGeef het antwoord als geldige JSON volgens dit voorbeeld:\n{structured_output}"
    model = model or OPENAI_MODEL
    cache_key = _cache_key(prompt, model, temperature, max_tokens, include_logprobs)
    # --- Redis cache proberen ---
    try:
        # De decorator cache_llm_response regelt Redis cache
        # Maar we checken ook handmatig voor fallback
        pass  # Decorator doet het werk
    except Exception as e:
        logging.warning(f"[LLM][REDIS] Redis cache niet beschikbaar: {e}")
    # --- File-cache fallback ---
    cached = _file_cache_get(cache_key)
    if cached:
        logging.info(f"[LLM][FILECACHE] Cache hit: {cache_key}")
        confidence = calculate_confidence(cached["answer"], context)
        return {
            "answer": cached["answer"],
            "confidence": confidence,
            "cached": True,
            "model": model,
            "timestamp": time.time(),
            "llm_confidence": cached.get("llm_confidence", 0.5)
        }
    # --- LLM call ---
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if include_logprobs and model in ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]:
        data["logprobs"] = True
        data["top_logprobs"] = 1
    logging.info(f"[LLM][REQUEST] {prompt[:60]}... [model={model}]")
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        answer = response_data["choices"][0]["message"]["content"]
        llm_confidence = 0.5
        if include_logprobs and "logprobs" in response_data:
            llm_confidence = calculate_confidence_from_logprobs(response_data)
        context["llm_confidence"] = llm_confidence
        confidence = calculate_confidence(answer, context)
        logging.info(f"[LLM][RESPONSE] {answer[:60]}... [confidence={confidence:.2f}]")
        # --- Cache in file fallback ---
        _file_cache_set(cache_key, {
            "answer": answer,
            "llm_confidence": llm_confidence
        })
        if structured_output:
            try:
                parsed_answer = json.loads(answer)
                return {
                    "answer": parsed_answer,
                    "confidence": confidence,
                    "cached": False,
                    "model": model,
                    "timestamp": time.time(),
                    "llm_confidence": llm_confidence
                }
            except Exception:
                pass
        return {
            "answer": answer,
            "confidence": confidence,
            "cached": False,
            "model": model,
            "timestamp": time.time(),
            "llm_confidence": llm_confidence
        }
    except Exception as e:
        logging.error(f"[LLM][ERROR] {e}")
        raise

def ask_openai(prompt: str, context: Optional[Dict[str, Any]] = None, model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 512, structured_output: Optional[str] = None) -> Any:
    """
    Backward compatible wrapper voor ask_openai_with_confidence.
    """
    if context is None:
        context = {"task": "general", "agent": "unknown"}
    result = ask_openai_with_confidence(prompt, context, model, temperature, max_tokens, structured_output)
    return result["answer"] 