from __future__ import annotations

import time
import requests


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, endpoint: str, model: str, timeout_s: float = 25.0, retries: int = 2) -> None:
        self.endpoint = endpoint
        self.model = model
        self.timeout_s = timeout_s
        self.retries = retries

    def generate(self, prompt: str) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        attempt = 0
        while True:
            try:
                resp = requests.post(self.endpoint, json=payload, timeout=self.timeout_s)
                resp.raise_for_status()
                data = resp.json()
                return str(data.get("response", "")).strip()
            except requests.RequestException as exc:
                if attempt >= self.retries:
                    raise OllamaError(str(exc)) from exc
                attempt += 1
                time.sleep(0.35)
