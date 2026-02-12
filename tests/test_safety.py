from jarviso.core.safety import expected_confirmation_phrase, handle_confirmation, needs_confirmation


def test_confirmation_needed_for_shutdown() -> None:
    assert needs_confirmation("shutdown")


def test_handle_confirmation_success() -> None:
    confirmed, pending = handle_confirmation("confirm shutdown", "shutdown")
    assert confirmed is True
    assert pending is None


def test_handle_confirmation_failure() -> None:
    confirmed, pending = handle_confirmation("shutdown now", "shutdown")
    assert confirmed is False
    assert pending == "shutdown"


def test_expected_phrase_format() -> None:
    assert expected_confirmation_phrase("shutdown") == "confirm shutdown"
