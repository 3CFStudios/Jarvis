import logging
from pathlib import Path

from jarviso.brain.memory import MemoryStore
from jarviso.brain.ollama_client import OllamaClient
from jarviso.config import AppConfig
from jarviso.core.engine import Engine
from jarviso.core.router import Router
from jarviso.core.types import Context


class DummySTT:
    def listen_once(self):
        return "what time is it"


class DummyTTS:
    def __init__(self):
        self.spoken = []

    def speak(self, text: str) -> None:
        self.spoken.append(text)


class DummyOllama(OllamaClient):
    def __init__(self):
        pass

    def generate(self, prompt: str) -> str:
        return "hello"


def test_engine_dispatches_time_action(tmp_path: Path) -> None:
    memory = MemoryStore(tmp_path / "memory.json")
    ctx = Context(config=AppConfig(memory_path=tmp_path / "memory.json"), memory=memory, logger=logging.getLogger("test"))
    tts = DummyTTS()
    engine = Engine(ctx=ctx, router=Router(), stt=DummySTT(), tts=tts, ollama=DummyOllama())

    result = engine.process_once()

    assert result.success is True
    assert "time" in result.spoken_text.lower()
    assert tts.spoken


class DummyOllamaAction(OllamaClient):
    def __init__(self):
        pass

    def generate(self, prompt: str) -> str:
        return '{"intent":"open_app","args":{"app":"chrome"},"spoken":"Opening Chrome.","needs_confirmation":false,"confirmation_phrase":""}'


def test_engine_llm_action_plan_uses_schema(tmp_path: Path) -> None:
    memory = MemoryStore(tmp_path / "memory.json")
    ctx = Context(config=AppConfig(memory_path=tmp_path / "memory.json"), memory=memory, logger=logging.getLogger("test"))
    tts = DummyTTS()
    engine = Engine(ctx=ctx, router=Router(), stt=DummySTT(), tts=tts, ollama=DummyOllamaAction())

    result = engine.process_once(forced_text="launch browser")

    assert result.success is False
    assert "open app requested" in result.ui_text.lower()
