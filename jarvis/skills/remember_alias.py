from __future__ import annotations

from typing import Any


def run(args: dict[str, Any]) -> None:
    store = args["memory"]
    alias = args.get("alias")
    target = args.get("target")
    if not alias or not target:
        raise ValueError("remember_alias requires alias and target")
    aliases = store.get("aliases", {})
    aliases[alias] = target
    store.set("aliases", aliases)
