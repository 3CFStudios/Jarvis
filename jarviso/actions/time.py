from __future__ import annotations

from datetime import datetime

from jarviso.core.types import ActionResult, Context


def handle(text: str, ctx: Context) -> ActionResult:
    now = datetime.now()
    if "date" in text.lower():
        spoken = f"Today's date is {now:%B %d, %Y}."
    else:
        spoken = f"The time is {now:%I:%M %p}."
    return ActionResult(spoken_text=spoken, ui_text=spoken, success=True)
