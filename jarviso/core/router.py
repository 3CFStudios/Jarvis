from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RouteResult:
    intent: str
    args: dict[str, str]
    from_llm: bool = False


class Router:
    def route(self, text: str) -> RouteResult:
        t = text.lower().strip()
        if any(p in t for p in ("what time", "time is it", "current time")):
            return RouteResult(intent="time", args={})
        if any(p in t for p in ("what date", "today's date", "current date")):
            return RouteResult(intent="date", args={})
        if t.startswith("open "):
            target = t.removeprefix("open ").strip()
            if target.startswith("http") or "." in target:
                return RouteResult(intent="open_url", args={"url": target})
            return RouteResult(intent="open_app", args={"app": target})
        if t.startswith("search "):
            return RouteResult(intent="web_search", args={"query": t.removeprefix("search ").strip()})
        if "shutdown" in t:
            return RouteResult(intent="shutdown", args={})
        return RouteResult(intent="ask_llm", args={"query": text})
