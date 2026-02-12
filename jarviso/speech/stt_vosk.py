from __future__ import annotations

from pathlib import Path

from jarviso.speech.mic import capture_pcm_queue


class VoskSTT:
    def __init__(self, model_path: Path, sample_rate: int = 16000):
        self.model_path = model_path
        self.sample_rate = sample_rate

    def listen_once(self, timeout_s: float = 6.0) -> str | None:
        try:
            from vosk import KaldiRecognizer, Model
        except ImportError:
            return None

        if not self.model_path.exists():
            return None

        model = Model(str(self.model_path))
        rec = KaldiRecognizer(model, self.sample_rate)
        q, stream = capture_pcm_queue(sample_rate=self.sample_rate)
        with stream:
            import time

            start = time.time()
            while time.time() - start < timeout_s:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = rec.Result()
                    import json

                    text = json.loads(result).get("text", "").strip()
                    return text or None
        return None
