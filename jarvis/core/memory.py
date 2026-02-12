from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Optional


class MemoryStore:
    def __init__(self, backend: str = "sqlite", sqlite_path: str = "jarvis_memory.db") -> None:
        self.backend = backend
        self.sqlite_path = Path(sqlite_path)
        self.json_path = Path("memory.json")

        if self.backend == "sqlite":
            self._init_sqlite()
        else:
            self._init_json()

    def _init_sqlite(self) -> None:
        with sqlite3.connect(self.sqlite_path) as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

    def _init_json(self) -> None:
        if not self.json_path.exists():
            self.json_path.write_text("{}", encoding="utf-8")

    def set(self, key: str, value: Any) -> None:
        payload = json.dumps(value)
        if self.backend == "sqlite":
            with sqlite3.connect(self.sqlite_path) as con:
                con.execute(
                    "INSERT INTO memory(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (key, payload),
                )
        else:
            data = json.loads(self.json_path.read_text(encoding="utf-8"))
            data[key] = value
            self.json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        if self.backend == "sqlite":
            with sqlite3.connect(self.sqlite_path) as con:
                row = con.execute("SELECT value FROM memory WHERE key=?", (key,)).fetchone()
            if not row:
                return default
            return json.loads(row[0])

        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        return data.get(key, default)
