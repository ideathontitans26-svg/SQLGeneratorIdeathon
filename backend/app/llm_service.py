"""Multi-LLM integration for SQL query generation."""
import time
from typing import Optional, Tuple

import google.generativeai as genai

from .config import settings


SYSTEM_PROMPT = """You are an expert SQL developer. Your task is to output ONLY a single SQL query—nothing else.

RULES:
- Output exactly one SQL statement. No explanations, no step-by-step instructions, no tool names (e.g. no "SQLite Builder"), no markdown except optional code fences around the SQL.
- Use only standard SQL and the table/column names from the schema if provided.
- Do not describe how to run the query or which application to use. Output only the SQL."""


async def generate_sql_openai(prompt: str, schema_info: Optional[str] = None) -> Tuple[str, float]:
    """Generate SQL using OpenAI GPT-4."""
    if not settings.OPENAI_API_KEY:
        raise ValueError("OpenAI API key not configured")
    
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    user_content = prompt
    if schema_info:
        user_content = f"Schema:\n{schema_info}\n\nUser request: {prompt}"
    
    start = time.perf_counter()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.2
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    sql = response.choices[0].message.content.strip()
    # Extract SQL from markdown code blocks if present
    if sql.startswith("```"):
        lines = sql.split("\n")
        sql = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    
    return sql, elapsed_ms


def _parse_sql_from_response(text: str) -> str:
    sql = (text or "").strip()
    if sql.startswith("```"):
        lines = sql.split("\n")
        sql = "\n".join(lines[1:-1] if len(lines) > 2 and lines[-1].strip() == "```" else lines[1:])
    return sql


async def generate_sql_gemini(prompt: str, schema_info: Optional[str] = None) -> Tuple[str, float]:
    """Generate SQL using Google Gemini."""
    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API key not configured")

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    user_content = prompt
    if schema_info:
        user_content = f"Schema:\n{schema_info}\n\nUser request: {prompt}"

    start = time.perf_counter()
    resp = await model.generate_content_async(
        [
            SYSTEM_PROMPT,
            user_content,
        ]
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    text = (resp.text or "").strip()
    sql = _parse_sql_from_response(text)
    return sql, elapsed_ms


async def generate_sql_ollama(prompt: str, schema_info: Optional[str] = None) -> Tuple[str, float]:
    """Generate SQL using Ollama (local LLM - no API key required). Tries /api/generate, then /api/chat if 404."""
    import httpx
    base = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = getattr(settings, "OLLAMA_MODEL", "tinyllama")
    user_content = prompt
    if schema_info:
        user_content = f"Schema:\n{schema_info}\n\nUser request: {prompt}"
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_content}"
    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Try /api/generate first (standard completion API)
        response = await client.post(
            f"{base}/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False,
            },
        )
        # If 404 or 500, try /api/chat (some Ollama versions have issues with /api/generate)
        if response.status_code in (404, 500):
            response = await client.post(
                f"{base}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    "stream": False,
                },
            )
        if response.status_code == 404:
            raise ValueError(
                f"Ollama returned 404 for model '{model}'. "
                f"Ensure the model is pulled: run `ollama pull {model}` in a terminal."
            )
        if not response.is_success:
            try:
                err_body = response.json()
                err_msg = err_body.get("error", err_body.get("message", response.text))
            except Exception:
                err_msg = response.text or response.reason_phrase
            raise ValueError(
                f"Ollama returned {response.status_code}: {err_msg}"
            )
        data = response.json()
    elapsed_ms = (time.perf_counter() - start) * 1000
    # /api/generate returns "response"; /api/chat returns "message": {"content": "..."}
    if "response" in data:
        sql = _parse_sql_from_response(data["response"])
    elif "message" in data and isinstance(data["message"], dict):
        sql = _parse_sql_from_response(data["message"].get("content", ""))
    else:
        sql = ""
    return sql, elapsed_ms


async def generate_sql_anthropic(prompt: str, schema_info: Optional[str] = None) -> Tuple[str, float]:
    """Generate SQL using Anthropic Claude."""
    if not settings.ANTHROPIC_API_KEY:
        raise ValueError("Anthropic API key not configured")
    
    from anthropic import AsyncAnthropic
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    user_content = prompt
    if schema_info:
        user_content = f"Schema:\n{schema_info}\n\nUser request: {prompt}"
    
    start = time.perf_counter()
    response = await client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}]
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    sql = response.content[0].text.strip()
    if sql.startswith("```"):
        lines = sql.split("\n")
        sql = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    
    return sql, elapsed_ms


async def generate_sql(prompt: str, model: str, schema_info: Optional[str] = None) -> Tuple[str, str, float]:
    """Route to appropriate LLM based on model selection."""
    model_map = {
        "ollama": ("ollama", generate_sql_ollama),
        "openai-gpt4": ("openai-gpt4", generate_sql_openai),
        "anthropic-claude": ("anthropic-claude", generate_sql_anthropic),
        "google-gemini": ("google-gemini", generate_sql_gemini),
    }
    
    if model not in model_map:
        model = "ollama"
    
    model_key, fn = model_map[model]
    sql, elapsed = await fn(prompt, schema_info)
    return sql, model_key, elapsed
