"""Environment diagnostics for Jarvis CLI."""

from __future__ import annotations

import os
import platform
import sys


def collect_diagnostics() -> dict[str, str]:
    """Collect basic diagnostics for the current runtime environment."""
    return {
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "windows_comspec": os.environ.get("COMSPEC", "not set"),
    }


def format_diagnostics() -> str:
    """Format diagnostics as human-readable text."""
    diagnostics = collect_diagnostics()
    lines = ["Jarvis Doctor", "============="]
    lines.extend(f"{key}: {value}" for key, value in diagnostics.items())
    return "\n".join(lines)
