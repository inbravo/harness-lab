"""
ollama_client.py — OpenAI-compatible client factory pointed at a local Ollama instance.

Reads connection settings from environment variables so examples can be run
against any Ollama host without code changes.

Usage:
    from _shared.ollama_client import get_llm, DEFAULT_MODEL
    client = get_llm()
    response = client.chat.completions.create(model=DEFAULT_MODEL, messages=[...])
"""
# ─────────────────────────────────────────────────────
# Author   : Amit Dixit
# GitHub   : https://github.com/inbravo
# Web      : https://inbravo.github.io
# LinkedIn : https://www.linkedin.com/in/inbravo/
# ─────────────────────────────────────────────────────

from __future__ import annotations

import os
from openai import OpenAI

# ── connection defaults ───────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
DEFAULT_MODEL   = os.getenv("OLLAMA_MODEL",       "llama3.1:8b")
JUDGE_MODEL     = os.getenv("OLLAMA_JUDGE_MODEL",  "qwen2.5:3b")
EMBED_MODEL     = os.getenv("OLLAMA_EMBED_MODEL",  "nomic-embed-text")


# ── public API ────────────────────────────────────────

def get_llm() -> OpenAI:
    """Return an OpenAI client wired to the local Ollama endpoint.

    Returns:
        Configured OpenAI client instance.
    """
    return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
