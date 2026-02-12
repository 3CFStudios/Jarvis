from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(slots=True)
class MemoryStore:
    path: Path

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def append(self, role: str, content: str) -> None:
        data = self.load()
        data.append({"role": role, "content": content})
        self.path.write_text(json.dumps(data[-20:], indent=2), encoding="utf-8")

    def load(self) -> list[dict[str, str]]:
        return json.loads(self.path.read_text(encoding="utf-8"))
