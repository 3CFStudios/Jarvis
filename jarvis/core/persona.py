from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PersonaManager:
    personas: dict[str, Any]
    current_mode: str

    def set_mode(self, mode: str) -> None:
        if mode not in self.personas:
            raise ValueError(f"Unknown persona mode: {mode}")
        self.current_mode = mode

    def get_mode(self) -> str:
        return self.current_mode

    def get_description(self) -> str:
        info = self.personas.get(self.current_mode, {})
        return str(info.get("description", ""))
