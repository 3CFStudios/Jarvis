from __future__ import annotations

import math
import threading
import tkinter as tk
from dataclasses import dataclass


@dataclass
class WatermarkConfig:
    text: str
    pattern_enabled: bool
    corner_enabled: bool
    angle_deg: int
    spacing_px: int


class HUD:
    def __init__(self, watermark: WatermarkConfig) -> None:
        self._watermark = watermark
        self._status = "Idle"
        self._root: tk.Tk | None = None
        self._canvas: tk.Canvas | None = None
        self._status_var: tk.StringVar | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self) -> None:
        self._root = tk.Tk()
        self._root.title("Jarvis HUD")
        self._root.geometry("640x200+20+20")
        self._root.attributes("-topmost", True)
        self._root.configure(bg="#111111")

        self._canvas = tk.Canvas(self._root, bg="#111111", highlightthickness=0)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self._status_var = tk.StringVar(value=self._status)
        status_label = tk.Label(
            self._root,
            textvariable=self._status_var,
            fg="#00f5d4",
            bg="#111111",
            font=("Segoe UI", 18, "bold"),
        )
        status_label.place(relx=0.03, rely=0.35)

        self._root.after(100, self._draw_watermarks)
        self._root.mainloop()

    def set_status(self, status: str) -> None:
        with self._lock:
            self._status = status
            if self._status_var is not None:
                self._status_var.set(status)

    def _draw_watermarks(self) -> None:
        if self._canvas is None or self._root is None:
            return

        self._canvas.delete("watermark")
        width = self._root.winfo_width()
        height = self._root.winfo_height()

        if self._watermark.pattern_enabled:
            spacing = max(80, self._watermark.spacing_px)
            angle = math.radians(self._watermark.angle_deg)
            for y in range(-height, height * 2, spacing):
                for x in range(-width, width * 2, spacing):
                    dx = int(30 * math.cos(angle))
                    dy = int(30 * math.sin(angle))
                    self._canvas.create_text(
                        x + dx,
                        y + dy,
                        text=self._watermark.text,
                        fill="#2b2b2b",
                        angle=self._watermark.angle_deg,
                        tags="watermark",
                    )

        if self._watermark.corner_enabled:
            self._canvas.create_text(
                width - 12,
                height - 12,
                text=self._watermark.text,
                anchor="se",
                fill="#3a3a3a",
                font=("Segoe UI", 10),
                tags="watermark",
            )

        self._root.after(1000, self._draw_watermarks)
