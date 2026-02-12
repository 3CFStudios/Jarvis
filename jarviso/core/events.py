from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SpeechHeard:
    text: str


@dataclass(slots=True)
class ResponseReady:
    spoken_text: str
    ui_text: str


@dataclass(slots=True)
class StatusChanged:
    status: str
