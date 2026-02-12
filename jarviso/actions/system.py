from __future__ import annotations

import platform
import subprocess

from jarviso.core.types import ActionResult, Context


def handle(text: str, ctx: Context) -> ActionResult:
    lowered = text.lower().strip()
    os_name = platform.system().lower()

    if lowered.startswith("open "):
        app = lowered.removeprefix("open ").strip()
        return ActionResult(
            spoken_text=f"I can't safely open {app} yet.",
            ui_text=f"Open app requested: {app}",
            success=False,
        )

    if "shutdown" in lowered:
        if os_name == "windows":
            subprocess.Popen(["shutdown", "/s", "/t", "30"])
        elif os_name == "linux":
            subprocess.Popen(["shutdown", "-h", "+1"])
        elif os_name == "darwin":
            subprocess.Popen(["sudo", "shutdown", "-h", "+1"])
        return ActionResult("Shutdown initiated.", "Shutdown initiated.", True)

    if "restart" in lowered:
        if os_name == "windows":
            subprocess.Popen(["shutdown", "/r", "/t", "30"])
        elif os_name in {"linux", "darwin"}:
            subprocess.Popen(["shutdown", "-r", "+1"])
        return ActionResult("Restart initiated.", "Restart initiated.", True)

    if "logoff" in lowered or "log off" in lowered:
        if os_name == "windows":
            subprocess.Popen(["shutdown", "/l"])
            return ActionResult("Logging off.", "Logging off.", True)
        return ActionResult("Logoff is not supported on this OS in current build.", "Logoff unsupported", False)

    return ActionResult("System action not recognized.", "System action not recognized.", False)
