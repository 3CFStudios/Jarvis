from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(slots=True)
class AppConfig:
    ollama_url: str = "http://localhost:11434/api/generate"
    model: str = "mistral"
    ollama_timeout_s: float = 25.0
    ollama_retries: int = 2
    memory_path: Path = Path("data/memory.json")
    stt_engine: str = "vosk"
    vosk_model_path: Path = Path("models/vosk-model-small-en-us-0.15")
    tts_rate: int = 180
    prompt_mode: str = "stark_default"


def _default_config_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config.json"


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or _default_config_path()
    if not config_path.exists():
        return AppConfig()

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    return AppConfig(
        ollama_url=raw.get("ollama_url", "http://localhost:11434/api/generate"),
        model=raw.get("model", "mistral"),
        ollama_timeout_s=float(raw.get("ollama_timeout_s", 25.0)),
        ollama_retries=int(raw.get("ollama_retries", 2)),
        memory_path=Path(raw.get("memory_path", "data/memory.json")),
        stt_engine=raw.get("stt_engine", "vosk"),
        vosk_model_path=Path(raw.get("vosk_model_path", "models/vosk-model-small-en-us-0.15")),
        tts_rate=int(raw.get("tts_rate", 180)),
        prompt_mode=raw.get("prompt_mode", "stark_default"),
    )
