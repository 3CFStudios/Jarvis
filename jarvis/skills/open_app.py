from __future__ import annotations

import subprocess
from typing import Any


def run(args: dict[str, Any]) -> None:
    app = args.get("name")
    if not app:
        raise ValueError("open_app requires 'name'")
    subprocess.Popen([app], shell=True)
