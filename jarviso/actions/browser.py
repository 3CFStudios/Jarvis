from __future__ import annotations

import urllib.parse
import webbrowser

from jarviso.core.types import ActionResult, Context


def handle(text: str, ctx: Context) -> ActionResult:
    lower = text.lower().strip()
    if lower.startswith("search "):
        query = lower.removeprefix("search ").strip()
        url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
        webbrowser.open(url)
        spoken = f"Searching the web for {query}."
        return ActionResult(spoken_text=spoken, ui_text=spoken, success=True)

    target = lower.removeprefix("open ").strip()
    if not target.startswith("http"):
        target = f"https://{target}"
    webbrowser.open(target)
    spoken = f"Opening {target}."
    return ActionResult(spoken_text=spoken, ui_text=spoken, success=True)
