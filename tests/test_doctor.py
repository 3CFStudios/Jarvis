from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from jarvis.doctor import collect_diagnostics, format_diagnostics


def test_collect_diagnostics_contains_expected_keys() -> None:
    diagnostics = collect_diagnostics()

    assert diagnostics["python_executable"]
    assert diagnostics["python_version"]
    assert diagnostics["platform"]


def test_format_diagnostics_header() -> None:
    output = format_diagnostics()

    assert "Jarvis Doctor" in output
    assert "python_version:" in output


def test_module_cli_doctor() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src)

    result = subprocess.run(
        [sys.executable, "-m", "jarvis", "doctor"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0
    assert "Jarvis Doctor" in result.stdout
