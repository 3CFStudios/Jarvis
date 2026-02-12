from __future__ import annotations

from typing import Any

import pyautogui


def run(args: dict[str, Any]) -> None:
    pyautogui.write(args.get("text", ""), interval=0.01)
