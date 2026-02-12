from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

import keyboard
import yaml

from core.audio import AudioEngine
from core.chat_ui import ChatUI
from core.confirmation import ConfirmationGate
from core.executor import Executor, ExecutorError, action_click, action_press_keys, action_scroll
from core.llm_client import LLMClient
from core.logging_utils import setup_logger
from core.memory import MemoryStore
from core.persona import PersonaManager
from core.planner import Planner
from core.tts import TTS
from skills import help as help_skill
from skills import instagram_prepare, open_app, remember_alias, set_folder, type_text, whatsapp_prepare

MODE_COMMANDS = {
    "Activate Dark Mode": "DARK",
    "Activate Prime Mode": "PRIME",
    "Activate Lock-In": "LOCKIN",
    "Activate Unhinged Mode": "UNHINGED_MAX",
}


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def run() -> None:
    root = Path(__file__).parent
    config = load_yaml(root / "config.yaml")
    personas = load_yaml(root / "personas.yaml")

    logger = setup_logger(config)
    stop_event = threading.Event()

    memory = MemoryStore(
        backend=config.get("memory", {}).get("backend", "sqlite"),
        sqlite_path=config.get("memory", {}).get("sqlite_path", "jarvis_memory.db"),
    )
    initial_mode = str(memory.get("persona_mode", config["persona"]["mode"]))
    persona_manager = PersonaManager(personas=personas, current_mode=initial_mode)

    llm = LLMClient(config["llm"])
    planner = Planner(llm, persona_manager)
    confirmation_gate = ConfirmationGate()
    tts = TTS()
    audio = AudioEngine(config["assistant"])

    chat_ui = ChatUI(title="Jarvis Chat", watermark_text=config["watermark"]["text"])
    chat_ui.set_status(f"Mode: {planner.get_mode()}")

    def speak_async(text: str) -> None:
        if not text.strip():
            return
        threading.Thread(target=tts.speak, args=(text,), daemon=True).start()

    def kill_switch() -> None:
        stop_event.set()
        confirmation_gate.cancel()
        chat_ui.set_status("ABORTED")
        speak_async("Stopped.")
        logger.warning("Kill switch activated")

    keyboard.add_hotkey(config["assistant"]["kill_hotkey"], kill_switch)

    action_registry = {
        "open_app": open_app.run,
        "type_text": type_text.run,
        "press_keys": action_press_keys,
        "click": action_click,
        "scroll": action_scroll,
        "help": help_skill.run,
        "remember_alias": lambda args: remember_alias.run({**args, "memory": memory}),
        "set_exports_folder": lambda args: set_folder.run({**args, "memory": memory}),
        "set_template": lambda args: memory.set("template", args.get("value", "")),
        "whatsapp_open": whatsapp_prepare.whatsapp_open,
        "whatsapp_search_chat": whatsapp_prepare.whatsapp_search_chat,
        "whatsapp_verify_chat_header": whatsapp_prepare.whatsapp_verify_chat_header,
        "whatsapp_prepare_message": whatsapp_prepare.whatsapp_prepare_message,
        "whatsapp_prepare_attachment": whatsapp_prepare.whatsapp_prepare_attachment,
        "whatsapp_finalize_send": whatsapp_prepare.whatsapp_finalize_send,
        "instagram_open": instagram_prepare.instagram_open,
        "instagram_prepare_upload": instagram_prepare.instagram_prepare_upload,
        "instagram_verify_destination": instagram_prepare.instagram_verify_destination,
        "instagram_finalize_post": instagram_prepare.instagram_finalize_post,
    }
    executor = Executor(confirmation_gate, stop_event, logger, action_registry)

    def execute_plan_background(plan: Any) -> None:
        try:
            executor.execute(plan)
            chat_ui.set_status("Done")
        except ExecutorError as exc:
            logger.error("Execution error: %s", exc)
            chat_ui.set_status("ABORTED")
            speak_async("Stopped.")
        except Exception as exc:
            logger.exception("Unhandled executor error: %s", exc)
            chat_ui.set_status("Error")
            speak_async("I hit a safe failure and stopped.")

    def handle_user_text(text: str) -> None:
        if stop_event.is_set():
            stop_event.clear()

        mode = MODE_COMMANDS.get(text)
        if mode is not None:
            planner.set_mode(mode)
            memory.set("persona_mode", mode)
            message = f"Mode set to {mode}"
            chat_ui.append_message("Jarvis", message)
            chat_ui.set_status(f"Mode: {mode}")
            speak_async(message)
            return

        chat_ui.set_status("Planning...")
        try:
            plan = planner.plan(text)
            if plan.say.strip():
                chat_ui.append_message("Jarvis", plan.say)
                speak_async(plan.say)
            chat_ui.set_status("Executing...")
            threading.Thread(target=execute_plan_background, args=(plan,), daemon=True).start()
        except Exception as exc:
            logger.exception("Planner error: %s", exc)
            chat_ui.append_message("Jarvis", "I could not build a safe plan.")
            chat_ui.set_status("Error")

    def on_send(text: str) -> None:
        chat_ui.append_message("You", text)
        threading.Thread(target=handle_user_text, args=(text,), daemon=True).start()

    chat_ui.set_on_send(on_send)

    def capture_ptt() -> None:
        chat_ui.set_status("Listening...")
        audio.beep()
        clip = audio.record_clip(config["assistant"]["max_record_seconds"], root / "last_input.wav")
        spoken_text = audio.transcribe(clip).strip()
        if spoken_text:
            on_send(spoken_text)
        else:
            chat_ui.set_status("Ready")

    keyboard.add_hotkey(
        config["assistant"]["ptt_hotkey"],
        lambda: threading.Thread(target=capture_ptt, daemon=True).start(),
    )

    logger.info("Jarvis started with mode=%s", planner.get_mode())
    chat_ui.run()


if __name__ == "__main__":
    run()
