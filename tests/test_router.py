from jarviso.core.router import Router


def test_time_route() -> None:
    route = Router().route("what time is it")
    assert route.intent == "time"


def test_shutdown_route() -> None:
    route = Router().route("shutdown computer")
    assert route.intent == "shutdown"


def test_fallback_llm_route() -> None:
    route = Router().route("tell me a joke")
    assert route.intent == "ask_llm"
