from __future__ import annotations

import wave
from pathlib import Path
from typing import Any

import numpy as np
import sounddevice as sd


class AudioError(RuntimeError):
    pass


class AudioEngine:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.sample_rate = 16_000

    def beep(self) -> None:
        duration = 0.15
        freq = 880
        timeline = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        tone = 0.2 * np.sin(2 * np.pi * freq * timeline)
        sd.play(tone, self.sample_rate)
        sd.wait()

    def record_clip(self, seconds: int, out_path: Path) -> Path:
        frames = sd.rec(int(seconds * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype="int16")
        sd.wait()
        with wave.open(str(out_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(frames.tobytes())
        return out_path

    def transcribe(self, audio_path: Path) -> str:
        try:
            from faster_whisper import WhisperModel

            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(str(audio_path), beam_size=5)
            text = " ".join(segment.text.strip() for segment in segments).strip()
            if text:
                return text
        except Exception:
            pass

        try:
            from vosk import KaldiRecognizer, Model

            model = Model(lang="en-us")
            rec = KaldiRecognizer(model, self.sample_rate)
            with wave.open(str(audio_path), "rb") as wav_file:
                while True:
                    data = wav_file.readframes(4000)
                    if len(data) == 0:
                        break
                    rec.AcceptWaveform(data)
            import json
            result = rec.FinalResult()
            return json.loads(result).get("text", "")
        except Exception as exc:
            raise AudioError("Failed transcription with both faster-whisper and Vosk") from exc

    def wake_word_detected(self) -> bool:
        try:
            from openwakeword.model import Model

            model = Model(wakeword_models=[])
            _ = model
            return False
        except Exception:
            return False
