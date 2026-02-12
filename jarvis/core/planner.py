from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from .llm_client import LLMClient


class Step(BaseModel):
    name: str = ""
    action: str
    instruction: str = ""
    args: dict[str, Any] = Field(default_factory=dict)


class Preview(BaseModel):
    target: str
    channel: str
    message: str
    attachments: list[str] = Field(default_factory=list)
    final_action: Literal[
        "none",
        "send",
        "post",
        "upload",
        "submit",
        "execute",
        "complete",
        "respond",
        "perform",
    ]
    steps: list[str] = Field(default_factory=list)


class OnError(BaseModel):
    say: str
    safe_fallback_steps: list[dict[str, Any]] = Field(default_factory=list)
    require_confirmation: bool = False
    wait_confirmation: bool = False


class Plan(BaseModel):
    say: str
    risk: Literal["LOCAL", "EXTERNAL"]
    preview: Preview
    steps: list[Step]
    on_error: OnError


class Planner:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def build_plan(self, user_input: str, persona_mode: str, persona_description: str) -> Plan:
        messages = [
            {"role": "system", "content": self._system_prompt(persona_mode, persona_description)},
            {"role": "user", "content": user_input},
        ]
        raw = self.llm_client.chat(messages)
        try:
            # Parse the JSON emitted by the planner LLM.
            data = json.loads(raw)

            # 1) Risk: if invalid or missing, default to LOCAL.
            if data.get("risk") not in ("LOCAL", "EXTERNAL"):
                data["risk"] = "LOCAL"

            # 2) Preview: ensure required keys are present.
            preview = data.get("preview", {})
            if not isinstance(preview, dict):
                preview = {}
            final_action = preview.get("final_action", "respond")
            if final_action not in {
                "none", "send", "post", "upload", "submit", "execute", "complete", "respond", "perform"
            }:
                final_action = "respond"
            preview_steps = preview.get("steps", [])
            if not isinstance(preview_steps, list):
                preview_steps = []
            data["preview"] = {
                "target": preview.get("target", "user"),
                "channel": preview.get("channel", "chat"),
                "message": preview.get("message", ""),
                "final_action": final_action,
                "steps": preview_steps,
            }

            # 3) Steps: every step must include an action.
            fixed_steps = []
            raw_steps = data.get("steps", [])
            if not isinstance(raw_steps, list):
                raw_steps = []
            for step in raw_steps:
                if not isinstance(step, dict):
                    continue
                if not step.get("action"):
                    name = step.get("name", "")
                    step["action"] = name.lower().replace(" ", "_") if name else "todo"
                fixed_steps.append(step)
            data["steps"] = fixed_steps

            # 4) on_error: provide default fields and coerce booleans.
            on_error = data.get("on_error", {})
            if not isinstance(on_error, dict):
                on_error = {}
            data["on_error"] = {
                "say": on_error.get("say", "An error occurred."),
                "require_confirmation": bool(on_error.get("require_confirmation", False)),
                "wait_confirmation": bool(on_error.get("wait_confirmation", False)),
            }

            return Plan.model_validate(data)
        except (ValidationError, json.JSONDecodeError) as exc:
            raise ValueError(f"Planner produced invalid JSON plan: {raw}") from exc

    @staticmethod
    def _system_prompt(persona_mode: str, persona_description: str) -> str:
        return (
            "You are Jarvis Planner. Output only a strict JSON object with keys: "
            "say, risk, preview, steps, on_error. No markdown, no prose outside JSON. "
            "You are planner-only and never execute actions. "
            "Use risk=EXTERNAL for irreversible/external actions and include require_confirmation "
            "and WAIT_CONFIRMATION steps before finalize actions. "
            "Allowed final action values: none|send|post|upload|submit|execute|complete|respond|perform. "
            "Each step should include name, action, and instruction; args are optional. "
            f"Persona mode is {persona_mode}: {persona_description}. "
            "Persona only affects the tone of say and on_error.say; safety rules never change."
        )
