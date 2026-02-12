from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


def setup_logger(config: dict[str, Any]) -> logging.Logger:
    log_cfg = config.get("logging", {})
    log_path = Path(log_cfg.get("path", "logs/jarvis.log"))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("jarvis")
    logger.setLevel(getattr(logging, log_cfg.get("level", "INFO").upper(), logging.INFO))

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=int(log_cfg.get("max_bytes", 1_048_576)),
        backupCount=int(log_cfg.get("backup_count", 5)),
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger
