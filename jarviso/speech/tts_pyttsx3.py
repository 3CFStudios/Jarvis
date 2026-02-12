from __future__ import annotations

import pyttsx3


class Speaker:
    def __init__(self, rate: int = 180):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)

    def speak(self, text: str) -> None:
        self.engine.say(text)
        self.engine.runAndWait()
