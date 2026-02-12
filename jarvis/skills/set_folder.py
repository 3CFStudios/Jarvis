from __future__ import annotations

from pathlib import Path
from typing import Any


def run(args: dict[str, Any]) -> None:
    store = args["memory"]
    path = Path(args.get("path", "")).expanduser()
    if not path:
        raise ValueError("set_exports_folder requires path")
    store.set("exports_folder", str(path))
