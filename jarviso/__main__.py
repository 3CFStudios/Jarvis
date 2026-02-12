from __future__ import annotations

from jarviso.branding import BRAND_LINE, banner
from jarviso.brain.memory import MemoryStore
from jarviso.brain.ollama_client import OllamaClient
from jarviso.config import load_config
from jarviso.core.engine import Engine
from jarviso.core.router import Router
from jarviso.core.types import Context
from jarviso.logging_setup import setup_logging
from jarviso.speech.stt_vosk import VoskSTT
from jarviso.speech.tts_pyttsx3 import Speaker
from jarviso.ui.app import MainWindow, create_app
from jarviso.ui.controller import UIController


def main() -> int:
    print(banner())

    config = load_config()
    logger = setup_logging()
    logger.info("%s started", BRAND_LINE)

    memory = MemoryStore(config.memory_path)
    ctx = Context(config=config, memory=memory, logger=logger)

    engine = Engine(
        ctx=ctx,
        router=Router(),
        stt=VoskSTT(config.vosk_model_path),
        tts=Speaker(rate=config.tts_rate),
        ollama=OllamaClient(
            endpoint=config.ollama_url,
            model=config.model,
            timeout_s=config.ollama_timeout_s,
            retries=config.ollama_retries,
        ),
    )

    app = create_app()
    window = MainWindow()
    UIController(window, engine)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
