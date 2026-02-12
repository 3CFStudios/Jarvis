from __future__ import annotations

APP_NAME = "JARVIS-O"
BRAND_LINE = "JARVIS-O • Arya Build"
COPYRIGHT_LINE = "© Arya"
STARTUP_BANNER = f"""
=====================================
      {BRAND_LINE}
            {COPYRIGHT_LINE}
=====================================
""".strip("\n")
UI_WATERMARK_TEXT = f"{BRAND_LINE}  {COPYRIGHT_LINE}"
STATUSBAR_TEXT = f"{BRAND_LINE} | {COPYRIGHT_LINE}"
ABOUT_TEXT = (
    f"{BRAND_LINE}\n"
    "Offline-first assistant powered by deterministic actions and Ollama.\n"
    "License and credits are included in LICENSE / CREDITS.md.\n"
    f"{COPYRIGHT_LINE}"
)


def banner() -> str:
    return STARTUP_BANNER


def watermark_text() -> str:
    return UI_WATERMARK_TEXT


def status_text() -> str:
    return STATUSBAR_TEXT
