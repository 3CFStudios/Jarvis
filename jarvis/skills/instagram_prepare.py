from __future__ import annotations

from typing import Any

from playwright.sync_api import Playwright



def instagram_open(args: dict[str, Any]) -> None:
    playwright: Playwright = args["playwright"]
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.instagram.com")
    args["_page"] = page



def _not_configured(step: str) -> None:
    raise NotImplementedError(
        f"{step} requires authenticated session-specific selectors. "
        "Implement selectors for your local Instagram Web layout before production use."
    )



def instagram_prepare_upload(args: dict[str, Any]) -> None:
    _ = args
    _not_configured("instagram_prepare_upload")



def instagram_verify_destination(args: dict[str, Any]) -> None:
    _ = args
    _not_configured("instagram_verify_destination")



def instagram_finalize_post(args: dict[str, Any]) -> None:
    _ = args
    _not_configured("instagram_finalize_post")
