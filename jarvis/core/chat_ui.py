from __future__ import annotations

import queue
import tkinter as tk
from tkinter import scrolledtext
from typing import Callable


class ChatUI:
    """Thread-safe Tkinter chat UI with dark theme and watermark."""

    def __init__(self, title: str = "Jarvis", watermark_text: str = "Arya VL") -> None:
        self._title = title
        self._watermark_text = watermark_text
        self._append_queue: queue.Queue[tuple[str, str]] = queue.Queue()
        self._status_queue: queue.Queue[str] = queue.Queue()
        self._on_send: Callable[[str], None] | None = None

        self._root = tk.Tk()
        self._root.title(self._title)
        self._root.geometry("900x620+30+30")
        self._root.configure(bg="#0b0b0b")

        self._build_widgets()
        self._root.after(50, self._flush_ui_queues)

    def _build_widgets(self) -> None:
        container = tk.Frame(self._root, bg="#0b0b0b")
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self._conversation = scrolledtext.ScrolledText(
            container,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="#111111",
            fg="#f5f5f5",
            insertbackground="#f5f5f5",
            font=("Consolas", 11),
            relief=tk.FLAT,
        )
        self._conversation.pack(fill=tk.BOTH, expand=True)

        self._status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            container,
            textvariable=self._status_var,
            anchor="w",
            bg="#0b0b0b",
            fg="#8a8a8a",
            font=("Segoe UI", 9),
        )
        status_label.pack(fill=tk.X, pady=(6, 2))

        input_row = tk.Frame(container, bg="#0b0b0b")
        input_row.pack(fill=tk.X, pady=(6, 0))

        self._input_box = tk.Entry(
            input_row,
            bg="#171717",
            fg="#f5f5f5",
            insertbackground="#f5f5f5",
            relief=tk.FLAT,
            font=("Segoe UI", 11),
        )
        self._input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self._input_box.bind("<Return>", self._on_enter)

        send_button = tk.Button(
            input_row,
            text="Send",
            command=self._handle_send,
            bg="#212121",
            fg="#f5f5f5",
            activebackground="#2c2c2c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=8,
        )
        send_button.pack(side=tk.LEFT, padx=(8, 0))

        watermark = tk.Label(
            self._root,
            text=self._watermark_text,
            bg="#0b0b0b",
            fg="#2e2e2e",
            font=("Segoe UI", 9),
        )
        watermark.place(relx=0.995, rely=0.995, anchor="se")

    def set_on_send(self, callback: Callable[[str], None]) -> None:
        self._on_send = callback

    def append_message(self, speaker: str, message: str) -> None:
        self._append_queue.put((speaker, message))

    def set_status(self, status: str) -> None:
        self._status_queue.put(status)

    def _flush_ui_queues(self) -> None:
        while True:
            try:
                speaker, message = self._append_queue.get_nowait()
            except queue.Empty:
                break
            self._conversation.config(state=tk.NORMAL)
            self._conversation.insert(tk.END, f"{speaker}: {message}\n")
            self._conversation.config(state=tk.DISABLED)
            self._conversation.see(tk.END)

        while True:
            try:
                status = self._status_queue.get_nowait()
            except queue.Empty:
                break
            self._status_var.set(status)

        self._root.after(50, self._flush_ui_queues)

    def _on_enter(self, _: tk.Event[tk.Misc]) -> str:
        self._handle_send()
        return "break"

    def _handle_send(self) -> None:
        if self._on_send is None:
            return
        text = self._input_box.get().strip()
        if not text:
            return
        self._input_box.delete(0, tk.END)
        self._on_send(text)

    def run(self) -> None:
        self._input_box.focus_set()
        self._root.mainloop()
