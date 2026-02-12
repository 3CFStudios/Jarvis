from __future__ import annotations

import json
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"
BASE_PROMPT_PATH = PROMPTS_DIR / "system_base.txt"
TRAITS_PROMPT_PATH = PROMPTS_DIR / "traits" / "arya_traits.txt"
MODES_DIR = PROMPTS_DIR / "modes"


def _read_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_system_prompt(mode: str | None = None) -> str:
    parts = [_read_prompt(BASE_PROMPT_PATH), _read_prompt(TRAITS_PROMPT_PATH)]

    if mode:
        mode_path = MODES_DIR / f"{mode}.txt"
        if mode_path.exists():
            parts.append(_read_prompt(mode_path))

    return "\n\n".join(parts)


SYSTEM_PROMPT = build_system_prompt()


def build_prompt(user_text: str, memory: list[dict[str, str]], mode: str | None = None) -> str:
    system_prompt = build_system_prompt(mode=mode)
    memory_lines = "\n".join(f"{m['role']}: {m['content']}" for m in memory[-10:])
    return f"{system_prompt}\n\nConversation:\n{memory_lines}\n\nUser: {user_text}\nAssistant:"


def try_parse_action_plan(text: str) -> dict[str, object] | None:
    stripped = text.strip()
    if not stripped.startswith("{"):
        return None

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return None

    required = {"intent", "args", "spoken", "needs_confirmation", "confirmation_phrase"}
    if not required.issubset(parsed.keys()):
        return None

    if not isinstance(parsed["intent"], str):
        return None
    if not isinstance(parsed["args"], dict):
        return None
    if not isinstance(parsed["spoken"], str):
        return None
    if not isinstance(parsed["needs_confirmation"], bool):
        return None
    if not isinstance(parsed["confirmation_phrase"], str):
        return None

    return parsed
