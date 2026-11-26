"""Groq's OpenAI-compatible chat API, one model per call. The caller decides what to do when a model
is rate limited, gives a bad answer, or is gone.

Free tier as checked on 2026-11-26: each model has its own budget of 8,000 tokens a minute, so a plan
that can't get one model tries the next.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx

log = logging.getLogger("dimafit.groq")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
TIMEOUT_S = 90.0


@dataclass(frozen=True)
class Model:
    id: str
    reasoning_effort: str | None = None
    hide_reasoning: bool = False


GPT_OSS_120B = Model("openai/gpt-oss-120b", "low", hide_reasoning=True)
GPT_OSS_20B = Model("openai/gpt-oss-20b", "low", hide_reasoning=True)
QWEN = Model("qwen/qwen3.8-27b", "none")

COACHES = [GPT_OSS_120B, QWEN, GPT_OSS_20B]  # in order of quality


class AIUnavailable(Exception):
    """No key, or Groq refuses the key: no model will work."""


class RateLimited(Exception):
    def __init__(self, wait: float | None):
        super().__init__(f"rate limited (retry after {wait})")
        self.wait = wait


class BadReply(Exception):
    """This answer is unusable (cut off, not JSON, too big a request): retry, maybe with less text."""


class ModelDown(Exception):
    """This model is retired, overloaded or unreachable: use another one."""


_client: httpx.AsyncClient | None = None
_client_loop: asyncio.AbstractEventLoop | None = None


def _http() -> httpx.AsyncClient:
    """One shared connection pool per event loop (tests and scripts may run several loops)."""
    global _client, _client_loop
    loop = asyncio.get_running_loop()
    if _client is None or _client_loop is not loop:
        _client_loop = loop
        # Groq's firewall rejects some default client names, so send our own.
        _client = httpx.AsyncClient(timeout=TIMEOUT_S, headers={"User-Agent": "dimafit/0.1"})
    return _client


def available() -> bool:
    return bool(os.environ.get("GROQ_API_KEY"))


async def call(model: Model, messages: list[dict], schema: dict, max_tokens: int, user: str = "") -> dict:
    """The model's JSON answer, which follows `schema` (strict structured output)."""
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise AIUnavailable("GROQ_API_KEY is not set")
    body: dict[str, Any] = {
        "model": model.id,
        "messages": messages,
        "temperature": 0.2,
        "max_completion_tokens": max_tokens,
        "stream": False,
        "response_format": {"type": "json_schema", "json_schema": {**schema, "strict": True}},
    }
    if user:
        body["user"] = user
    if model.reasoning_effort:
        body["reasoning_effort"] = model.reasoning_effort
    if model.hide_reasoning:
        body["include_reasoning"] = False
    try:
        response = await _http().post(GROQ_URL, headers={"Authorization": f"Bearer {key}"}, json=body)
    except httpx.HTTPError as error:
        raise ModelDown(f"{model.id}: no response ({type(error).__name__})") from error

    status = response.status_code
    if status == 200:
        data = response.json()
        usage = data.get("usage") or {}
        log.info("%s: %s in + %s out tokens", model.id, usage.get("prompt_tokens"), usage.get("completion_tokens"))
        choice = (data.get("choices") or [{}])[0]
        content = (choice.get("message") or {}).get("content")
        if choice.get("finish_reason") == "length" or not isinstance(content, str):
            raise BadReply(f"{model.id}: answer cut off")
        try:
            return json.loads(content)
        except json.JSONDecodeError as error:
            raise BadReply(f"{model.id}: answer is not JSON") from error

    code = _error_code(response)
    log.warning("%s: HTTP %s %s", model.id, status, code or "")
    if status == 429:
        raise RateLimited(_retry_after(response))
    if status in (401, 403):
        raise AIUnavailable(f"Groq refused the key (HTTP {status})")
    if status in (404, 410) or status >= 500 or code in ("model_decommissioned", "model_not_found"):
        raise ModelDown(f"{model.id}: HTTP {status}")
    # 400 (e.g. the answer broke the schema), 413 (request too large): try again with less text.
    raise BadReply(f"{model.id}: HTTP {status} {code or ''}")


def _retry_after(response: httpx.Response) -> float | None:
    try:
        return float(response.headers.get("retry-after", ""))
    except ValueError:
        return None


def _error_code(response: httpx.Response) -> str | None:
    try:
        return response.json().get("error", {}).get("code")
    except ValueError:
        return None

