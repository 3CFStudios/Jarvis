from __future__ import annotations

from collections.abc import Callable

from jarviso.actions import browser, files, system, time as time_action
from jarviso.brain.ollama_client import OllamaClient, OllamaError
from jarviso.brain.prompting import build_prompt, try_parse_action_plan
from jarviso.core.router import Router
from jarviso.core.safety import expected_confirmation_phrase, handle_confirmation, needs_confirmation
from jarviso.core.types import ActionResult, Context

StatusCallback = Callable[[str], None]
TranscriptCallback = Callable[[str], None]


class Engine:
    def __init__(
        self,
        ctx: Context,
        router: Router,
        stt,
        tts,
        ollama: OllamaClient,
        on_status: StatusCallback | None = None,
        on_transcript: TranscriptCallback | None = None,
    ) -> None:
        self.ctx = ctx
        self.router = router
        self.stt = stt
        self.tts = tts
        self.ollama = ollama
        self.on_status = on_status
        self.on_transcript = on_transcript

    def set_status(self, status: str) -> None:
        self.ctx.last_status = status
        if self.on_status:
            self.on_status(status)

    def process_once(self, forced_text: str | None = None) -> ActionResult:
        self.set_status("LISTENING")
        text = forced_text or self.stt.listen_once()
        if not text:
            result = ActionResult("I didn't catch that.", "No speech detected.", False)
            self._speak(result.spoken_text)
            return result

        if self.on_transcript:
            self.on_transcript(text)

        confirmed, pending = handle_confirmation(text, self.ctx.confirm_state)
        self.ctx.confirm_state = pending
        if confirmed and pending is None:
            confirmed_intent = text.strip().lower().removeprefix("confirm ").strip()
            return self._dispatch(confirmed_intent, confirmed_intent)

        self.set_status("THINKING")
        route = self.router.route(text)
        if route.intent == "ask_llm":
            return self._ask_llm(text)

        if needs_confirmation(route.intent):
            return self._require_confirmation(route.intent)

        action_text = self._build_action_text(route.intent, route.args, text)
        return self._dispatch(route.intent, action_text)

    def _require_confirmation(self, intent: str, spoken: str | None = None) -> ActionResult:
        phrase = expected_confirmation_phrase(intent)
        self.ctx.confirm_state = intent
        result = ActionResult(
            spoken_text=spoken or f"Please say {phrase} to proceed.",
            ui_text=f"Confirmation required for {intent}: say '{phrase}'.",
            success=False,
        )
        self._speak(result.spoken_text)
        return result

    def _ask_llm(self, text: str) -> ActionResult:
        prompt = build_prompt(text, self.ctx.memory.load(), mode=self.ctx.config.prompt_mode)
        try:
            response = self.ollama.generate(prompt)
        except OllamaError:
            result = ActionResult(
                spoken_text="Ollama is not running. Start Ollama and try again.",
                ui_text="Ollama is not running. Start Ollama and try again.",
                success=False,
            )
            self._speak(result.spoken_text)
            return result

        self.ctx.memory.append("user", text)
        self.ctx.memory.append("assistant", response)

        action_plan = try_parse_action_plan(response)
        if action_plan:
            intent = str(action_plan["intent"])
            args = dict(action_plan["args"])
            spoken = str(action_plan["spoken"])
            needs_confirm = bool(action_plan["needs_confirmation"])
            confirmation_phrase = str(action_plan["confirmation_phrase"])

            if needs_confirm or needs_confirmation(intent):
                prompt_spoken = spoken if spoken else f"Please say {confirmation_phrase or expected_confirmation_phrase(intent)} to proceed."
                return self._require_confirmation(intent, prompt_spoken)

            action_text = self._build_action_text(intent, args, spoken)
            result = self._dispatch(intent, action_text)
            if spoken and spoken != result.spoken_text:
                result.ui_text = f"{spoken} ({result.ui_text})"
            return result

        result = ActionResult(spoken_text=response, ui_text=response, success=True)
        self._speak(result.spoken_text)
        return result

    def _build_action_text(self, intent: str, args: dict[str, object], fallback_text: str) -> str:
        if intent == "open_app":
            app = str(args.get("app", "")).strip()
            return f"open {app}" if app else fallback_text
        if intent == "open_url":
            url = str(args.get("url", "")).strip()
            return f"open {url}" if url else fallback_text
        if intent == "web_search":
            query = str(args.get("query", "")).strip()
            return f"search {query}" if query else fallback_text
        if intent in {"open_folder", "search_file", "shutdown", "restart", "logoff"}:
            return fallback_text
        return fallback_text

    def _dispatch(self, intent: str, text: str) -> ActionResult:
        self.set_status("ACTING")
        if intent in {"time", "date"}:
            result = time_action.handle(text, self.ctx)
        elif intent in {"open_url", "web_search"}:
            result = browser.handle(text, self.ctx)
        elif intent in {"open_folder", "search_file"}:
            result = files.handle(text, self.ctx)
        elif intent in {"shutdown", "open_app", "restart", "logoff"}:
            result = system.handle(text, self.ctx)
        else:
            result = ActionResult("I cannot do that yet.", "Unknown intent", False)
        self._speak(result.spoken_text)
        return result

    def _speak(self, text: str) -> None:
        self.set_status("SPEAKING")
        self.tts.speak(text)
        self.set_status("IDLE")
