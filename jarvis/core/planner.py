from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from .llm_client import LLMClient
from .persona import PersonaManager


class Step(BaseModel):
    action: str
    args: dict[str, Any] = Field(default_factory=dict)


class Preview(BaseModel):
    target: str
    channel: str
    message: str
    attachments: list[str] = Field(default_factory=list)
    final_action: Literal["none", "send", "post", "upload", "submit"]


class OnError(BaseModel):
    say: str
    safe_fallback_steps: list[dict[str, Any]] = Field(default_factory=list)


class Plan(BaseModel):
    say: str
    risk: Literal["LOCAL", "EXTERNAL"]
    preview: Preview
    steps: list[Step]
    on_error: OnError


class Planner:
    def __init__(self, llm_client: LLMClient, persona_manager: PersonaManager) -> None:
        self.llm_client = llm_client
        self.persona_manager = persona_manager

    def set_mode(self, mode: str) -> None:
        self.persona_manager.set_mode(mode)

    def get_mode(self) -> str:
        return self.persona_manager.get_mode()

    def plan(self, user_input: str) -> Plan:
        persona_mode = self.persona_manager.get_mode()
        persona_description = self.persona_manager.get_description()
        messages = [
            {"role": "system", "content": self._system_prompt(persona_mode, persona_description)},
            {"role": "user", "content": user_input},
        ]
        raw = self.llm_client.chat(messages)
        try:
            return Plan.model_validate(json.loads(raw))
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
            "Allowed final action values: none|send|post|upload|submit. "
            f"Persona mode is {persona_mode}: {persona_description}. "
            "Persona only affects the tone of say and on_error.say; safety rules never change."
        )
