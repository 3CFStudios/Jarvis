from __future__ import annotations

DESTRUCTIVE_INTENTS = {
    "shutdown",
    "restart",
    "logoff",
    "delete_file",
    "delete_folder",
    "format_drive",
    "kill_process",
    "factory_reset",
}


def needs_confirmation(intent: str) -> bool:
    return intent in DESTRUCTIVE_INTENTS


def expected_confirmation_phrase(intent: str) -> str:
    return f"confirm {intent}".strip()


def handle_confirmation(text: str, pending_intent: str | None) -> tuple[bool, str | None]:
    if not pending_intent:
        return False, None

    normalized = text.strip().lower()
    expected = expected_confirmation_phrase(pending_intent)
    if normalized == expected:
        return True, None

    return False, pending_intent
