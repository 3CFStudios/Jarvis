from unittest.mock import Mock, patch

import pytest

from jarviso.brain.ollama_client import OllamaClient, OllamaError


def test_generate_success() -> None:
    fake_resp = Mock()
    fake_resp.json.return_value = {"response": "hello"}
    fake_resp.raise_for_status.return_value = None
    with patch("jarviso.brain.ollama_client.requests.post", return_value=fake_resp):
        client = OllamaClient("http://localhost:11434/api/generate", "mistral")
        assert client.generate("ping") == "hello"


def test_generate_retries_and_fails() -> None:
    with patch("jarviso.brain.ollama_client.requests.post", side_effect=__import__("requests").RequestException("boom")):
        client = OllamaClient("http://localhost:11434/api/generate", "mistral", retries=0)
        with pytest.raises(OllamaError):
            client.generate("ping")
