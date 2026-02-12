from __future__ import annotations

import logging

from jarviso.branding import BRAND_LINE


def setup_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s | [Arya Build] | %(levelname)s | %(name)s | %(message)s",
    )
    logger = logging.getLogger("jarviso")
    logger.info("%s logging initialized", BRAND_LINE)
    return logger
