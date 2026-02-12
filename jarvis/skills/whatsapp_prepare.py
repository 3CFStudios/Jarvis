from __future__ import annotations

from typing import Any

from playwright.sync_api import Playwright



def whatsapp_open(args: dict[str, Any]) -> None:
    playwright: Playwright = args["playwright"]
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://web.whatsapp.com")
    args["_page"] = page



def _not_configured(step: str) -> None:
    raise NotImplementedError(
        f"{step} requires authenticated session-specific selectors. "
        "Implement selectors for your local WhatsApp Web layout before production use."
    )



def whatsapp_search_chat(args: dict[str, Any]) -> None:
    _ = args
    _not_configured("whatsapp_search_chat")



def whatsapp_verify_chat_header(args: dict[str, Any]) -> None:
    _ = args
    _not_configured("whatsapp_verify_chat_header")



def whatsapp_prepare_message(args: dict[str, Any]) -> None:
    _ = args
    _not_configured("whatsapp_prepare_message")



def whatsapp_prepare_attachment(args: dict[str, Any]) -> None:
    _ = args
    _not_configured("whatsapp_prepare_attachment")



def whatsapp_finalize_send(args: dict[str, Any]) -> None:
    _ = args
    _not_configured("whatsapp_finalize_send")
