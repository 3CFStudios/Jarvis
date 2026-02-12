from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import logging

from jarviso.config import AppConfig
from jarviso.brain.memory import MemoryStore


@dataclass(slots=True)
class Context:
    config: AppConfig
    memory: MemoryStore
    logger: logging.Logger
    last_status: str = "IDLE"
    confirm_state: str | None = None


@dataclass(slots=True)
class ActionResult:
    spoken_text: str
    ui_text: str
    success: bool
    metadata: dict[str, Any] | None = None
