from __future__ import annotations

from pathlib import Path
import os

from jarviso.core.types import ActionResult, Context


def handle(text: str, ctx: Context) -> ActionResult:
    q = text.lower().strip()
    if q.startswith("open folder "):
        folder = Path(q.removeprefix("open folder ").strip()).expanduser()
        if folder.exists() and folder.is_dir():
            os.startfile(str(folder)) if hasattr(os, "startfile") else None
            spoken = f"Opened folder {folder}."
            return ActionResult(spoken_text=spoken, ui_text=spoken, success=True)
        return ActionResult(spoken_text="Folder not found.", ui_text="Folder not found.", success=False)
    return ActionResult(spoken_text="File action not recognized.", ui_text="File action not recognized.", success=False)
