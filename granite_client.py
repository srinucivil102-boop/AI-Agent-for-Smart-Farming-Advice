"""
IBM Granite LLM client using ibm-watsonx-ai SDK.
Provides a unified interface for text generation and chat.
"""
import os
import json
import time
import requests
from typing import Optional

import config


def _get_iam_token() -> str:
    """Fetch an IAM bearer token from IBM Cloud."""
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": config.IBM_API_KEY,
    }
    resp = requests.post(url, headers=headers, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


# --------------------------------------------------------------------------- #
#  Token cache (simple in-process cache; token lives ~3600 s)                  #
# --------------------------------------------------------------------------- #
_token_cache: dict = {"token": None, "expires_at": 0}


def _get_cached_token() -> str:
    now = time.time()
    if _token_cache["token"] is None or now >= _token_cache["expires_at"]:
        _token_cache["token"] = _get_iam_token()
        _token_cache["expires_at"] = now + 3000  # refresh 10 min before expiry
    return _token_cache["token"]


# --------------------------------------------------------------------------- #
#  Core generation function                                                     #
# --------------------------------------------------------------------------- #
def generate_text(
    prompt: str,
    model_id: str = config.GRANITE_CHAT_MODEL,
    max_new_tokens: int = config.MAX_NEW_TOKENS,
    temperature: float = 0.7,
    stop_sequences: Optional[list] = None,
) -> str:
    """
    Call the IBM watsonx.ai chat endpoint (granite-4 requires /ml/v1/text/chat).
    Wraps the plain prompt as a single user message.
    Returns the generated text string.
    """
    messages = [{"role": "user", "content": prompt}]
    return chat_completion(messages, model_id, max_new_tokens, temperature)


def chat_completion(
    messages: list[dict],
    model_id: str = config.GRANITE_CHAT_MODEL,
    max_new_tokens: int = config.MAX_NEW_TOKENS,
    temperature: float = 0.7,
) -> str:
    """
    Multi-turn chat via the watsonx.ai chat endpoint.
    `messages` is a list of {"role": "user"|"assistant"|"system", "content": "..."}.
    """
    token = _get_cached_token()
    url = f"{config.IBM_WATSONX_URL}/ml/v1/text/chat?version=2024-03-14"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body = {
        "model_id": model_id,
        "messages": messages,
        "project_id": config.IBM_PROJECT_ID,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "repetition_penalty": 1.1,
        },
    }

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        # Chat endpoint returns choices[0].message.content
        return result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as e:
        # Fall back to text generation with formatted prompt
        return _fallback_chat(messages, model_id, max_new_tokens, temperature)
    except Exception as e:
        return f"[Chat Error] {str(e)}"


def _fallback_chat(messages, model_id, max_new_tokens, temperature) -> str:
    """Convert chat messages to a flat prompt and call generate_text."""
    prompt_parts = []
    for m in messages:
        role = m["role"].capitalize()
        prompt_parts.append(f"{role}: {m['content']}")
    prompt_parts.append("Assistant:")
    prompt = "\n".join(prompt_parts)
    return generate_text(prompt, model_id, max_new_tokens, temperature)
