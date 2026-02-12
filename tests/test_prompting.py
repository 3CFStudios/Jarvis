from jarviso.brain.prompting import (
    BASE_PROMPT_PATH,
    TRAITS_PROMPT_PATH,
    SYSTEM_PROMPT,
    build_system_prompt,
    try_parse_action_plan,
)


def test_base_prompt_contains_action_json_schema() -> None:
    text = BASE_PROMPT_PATH.read_text(encoding="utf-8")
    assert '"intent"' in text
    assert '"args"' in text
    assert '"needs_confirmation"' in text


def test_traits_prompt_contains_arya_mode() -> None:
    text = TRAITS_PROMPT_PATH.read_text(encoding="utf-8")
    assert "Arya-mode" in text


def test_composed_prompt_includes_base_and_traits() -> None:
    composed = build_system_prompt()
    assert "ACTION OUTPUT FORMAT (STRICT JSON ONLY)" in composed
    assert "Arya-mode" in composed
    assert SYSTEM_PROMPT == composed


def test_parse_action_plan_requires_confirmation_phrase() -> None:
    bad = '{"intent":"open_app","args":{"app":"chrome"},"spoken":"Opening.","needs_confirmation":false}'
    assert try_parse_action_plan(bad) is None


def test_parse_action_plan_valid_schema() -> None:
    good = '{"intent":"open_app","args":{"app":"chrome"},"spoken":"Opening Chrome.","needs_confirmation":false,"confirmation_phrase":""}'
    parsed = try_parse_action_plan(good)
    assert parsed is not None
    assert parsed["intent"] == "open_app"



def test_stark_mode_prompt_contains_stark_header() -> None:
    composed = build_system_prompt(mode="stark_default")
    assert "SYSTEM: JARVIS-O (STARK-STYLE DEFAULT, COMBINED)" in composed
    assert "ACTION OUTPUT FORMAT (STRICT JSON ONLY)" in composed
