from __future__ import annotations

import threading
from typing import Any, Callable

import pyautogui
from playwright.sync_api import sync_playwright

from .confirmation import ConfirmationGate
from .planner import Plan


class ExecutorError(RuntimeError):
    pass


class Executor:
    LOCAL_ACTIONS = {
        "open_app",
        "focus_window",
        "type_text",
        "move_mouse",
        "click",
        "scroll",
        "press_keys",
        "screenshot",
        "search_files",
        "open_file",
        "set_volume",
        "set_brightness",
        "remember_alias",
        "set_exports_folder",
        "set_template",
        "whatsapp_open",
        "whatsapp_search_chat",
        "whatsapp_verify_chat_header",
        "whatsapp_prepare_message",
        "whatsapp_prepare_attachment",
        "instagram_open",
        "instagram_prepare_upload",
        "instagram_verify_destination",
        "require_confirmation",
        "WAIT_CONFIRMATION",
        "whatsapp_finalize_send",
        "instagram_finalize_post",
    }

    EXTERNAL_FINALIZE_ACTIONS = {
        "whatsapp_finalize_send",
        "instagram_finalize_post",
    }

    def __init__(
        self,
        confirmation_gate: ConfirmationGate,
        stop_event: threading.Event,
        logger: Any,
        action_registry: dict[str, Callable[[dict[str, Any]], None]],
    ) -> None:
        self.confirmation_gate = confirmation_gate
        self.stop_event = stop_event
        self.logger = logger
        self.action_registry = action_registry

    def execute(self, plan: Plan) -> None:
        self.execute_plan(plan)

    def execute_plan(self, plan: Plan) -> None:
        self._validate_plan_permissions(plan)
        with sync_playwright() as playwright:
            runtime = {"playwright": playwright}
            for step in plan.steps:
                self._check_stop("before")
                action = step.action
                args = {**step.args, **runtime}
                self.logger.info("skill=%s args=%s", action, step.args)

                if action == "WAIT_CONFIRMATION":
                    continue

                if action == "require_confirmation":
                    result = self.confirmation_gate.request_confirmation(plan.preview.model_dump(), self.stop_event)
                    self.logger.info("confirmation_event=%s", result.reason)
                    if not result.confirmed:
                        raise ExecutorError(f"Confirmation failed: {result.reason}")
                    self._check_stop("after")
                    continue

                handler = self.action_registry.get(action)
                if handler is None:
                    raise ExecutorError(f"No handler registered for action: {action}")
                handler(args)
                self._check_stop("after")

    def _validate_plan_permissions(self, plan: Plan) -> None:
        for step in plan.steps:
            if step.action not in self.LOCAL_ACTIONS:
                raise ExecutorError(f"Action not allowlisted: {step.action}")

        finalize_actions = [s.action for s in plan.steps if s.action in self.EXTERNAL_FINALIZE_ACTIONS]

        if finalize_actions and plan.risk != "EXTERNAL":
            raise ExecutorError("Finalize external action requires risk=EXTERNAL")

        if plan.risk == "EXTERNAL":
            action_names = [s.action for s in plan.steps]
            if "require_confirmation" not in action_names or "WAIT_CONFIRMATION" not in action_names:
                raise ExecutorError("EXTERNAL plan must include require_confirmation and WAIT_CONFIRMATION")

    def _check_stop(self, when: str) -> None:
        if self.stop_event.is_set():
            raise ExecutorError(f"Execution aborted by kill switch ({when})")


# Generic local wrappers

def action_press_keys(args: dict[str, Any]) -> None:
    keys = args.get("keys", [])
    if isinstance(keys, str):
        keys = [keys]
    for key in keys:
        pyautogui.press(key)


def action_type_text(args: dict[str, Any]) -> None:
    pyautogui.write(args.get("text", ""), interval=0.01)


def action_click(args: dict[str, Any]) -> None:
    x = args.get("x")
    y = args.get("y")
    if x is not None and y is not None:
        pyautogui.click(x=x, y=y)
    else:
        pyautogui.click()


def action_scroll(args: dict[str, Any]) -> None:
    pyautogui.scroll(int(args.get("amount", -300)))
