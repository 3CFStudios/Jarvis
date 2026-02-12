from __future__ import annotations

import queue


def capture_pcm_queue(sample_rate: int = 16000, channels: int = 1):
    import sounddevice as sd

    q: queue.Queue[bytes] = queue.Queue()

    def callback(indata, frames, time, status):  # type: ignore[no-untyped-def]
        if status:
            return
        q.put(bytes(indata))

    stream = sd.RawInputStream(
        samplerate=sample_rate,
        blocksize=8000,
        dtype="int16",
        channels=channels,
        callback=callback,
    )
    return q, stream
