"""OpenAI-compatible client factory pointed at a local Ollama instance."""
__author__ = "Amit Dixit"

import os
from openai import OpenAI

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
JUDGE_MODEL = os.getenv("OLLAMA_JUDGE_MODEL", "qwen2.5:3b")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")


def get_llm() -> OpenAI:
    return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
