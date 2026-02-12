from __future__ import annotations

import json
import os
from typing import Any

import requests


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.backend = config.get("backend", "ollama")
        self.model = config.get("model", "mistral")
        self.timeout = int(config.get("timeout_seconds", 30))

    def chat(self, messages: list[dict[str, str]]) -> str:
        if self.backend == "ollama":
            return self._chat_ollama(messages)
        if self.backend == "mistral_cloud":
            return self._chat_mistral_cloud(messages)
        raise LLMError(f"Unsupported LLM backend: {self.backend}")

    def _chat_ollama(self, messages: list[dict[str, str]]) -> str:
        url = self.config.get("ollama_url", "http://localhost:11434/api/chat")
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json",
        }
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        try:
            return data["message"]["content"]
        except KeyError as exc:
            raise LLMError(f"Unexpected Ollama response: {json.dumps(data)}") from exc

    def _chat_mistral_cloud(self, messages: list[dict[str, str]]) -> str:
        key_env = self.config.get("mistral_api_key_env", "MISTRAL_API_KEY")
        api_key = os.getenv(key_env)
        if not api_key:
            raise LLMError(f"Missing Mistral API key in env var: {key_env}")

        url = self.config.get("mistral_api_url", "https://api.mistral.ai/v1/chat/completions")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0,
        }
        response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected Mistral response: {json.dumps(data)}") from exc
