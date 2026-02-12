from __future__ import annotations

import threading

from PyQt6.QtCore import QObject, pyqtSignal

from jarviso.branding import BRAND_LINE
from jarviso.core.engine import Engine
from jarviso.ui.app import MainWindow


class UIController(QObject):
    status_signal = pyqtSignal(str)
    transcript_signal = pyqtSignal(str)
    assistant_signal = pyqtSignal(str)

    def __init__(self, window: MainWindow, engine: Engine) -> None:
        super().__init__()
        self.window = window
        self.engine = engine
        self._running = False
        self._thread: threading.Thread | None = None
        self._greeted = False

        self.window.toggle_button.clicked.connect(self.toggle_listening)
        self.engine.on_status = self.update_status
        self.engine.on_transcript = self.update_transcript

        self.status_signal.connect(self._set_status_label)
        self.transcript_signal.connect(self._append_user_text)
        self.assistant_signal.connect(self._append_assistant_text)

    def toggle_listening(self) -> None:
        self._running = not self._running
        self.window.toggle_button.setText("Stop Listening" if self._running else "Start Listening")

        if not self._greeted:
            self._greeted = True
            self.engine.tts.speak(f"{BRAND_LINE} ready.")

        if self._running and (self._thread is None or not self._thread.is_alive()):
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def _loop(self) -> None:
        while self._running:
            result = self.engine.process_once()
            self.assistant_signal.emit(result.ui_text)

    def update_status(self, status: str) -> None:
        self.status_signal.emit(status)

    def update_transcript(self, text: str) -> None:
        self.transcript_signal.emit(text)

    def _set_status_label(self, status: str) -> None:
        self.window.status_label.setText(f"Status: {status}")

    def _append_user_text(self, text: str) -> None:
        self.window.transcript_box.append(f"You: {text}")

    def _append_assistant_text(self, text: str) -> None:
        self.window.transcript_box.append(f"Assistant: {text}")
