from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any


@dataclass
class ConfirmationResult:
    confirmed: bool
    reason: str


class ConfirmationGate:
    def __init__(self) -> None:
        self._event = threading.Event()
        self._confirmed: bool = False

    def request_confirmation(self, preview: dict[str, Any], stop_event: threading.Event) -> ConfirmationResult:
        self._event.clear()
        self._confirmed = False

        print("\n=== CONFIRMATION REQUIRED ===")
        print(preview)
        print("Type 'confirm' to proceed or anything else to cancel.")
        while not self._event.is_set():
            if stop_event.is_set():
                return ConfirmationResult(False, "aborted_by_kill_switch")
            response = input("> ").strip().lower()
            self._confirmed = response == "confirm"
            self._event.set()

        if self._confirmed:
            return ConfirmationResult(True, "confirmed")
        return ConfirmationResult(False, "rejected")

    def cancel(self) -> None:
        self._event.set()
        self._confirmed = False
