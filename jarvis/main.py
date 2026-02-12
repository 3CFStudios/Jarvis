from __future__ import annotations

import threading
<<<<<<< codex/build-advanced-local-voice-assistant-jarvis-jbsk9b
=======
import time
>>>>>>> main
from pathlib import Path
from typing import Any

import keyboard
import yaml

from core.audio import AudioEngine
<<<<<<< codex/build-advanced-local-voice-assistant-jarvis-jbsk9b
from core.chat_ui import ChatUI
from core.confirmation import ConfirmationGate
from core.executor import Executor, ExecutorError, action_click, action_press_keys, action_scroll
from core.llm_client import LLMClient
from core.logging_utils import setup_logger
from core.memory import MemoryStore
from core.persona import PersonaManager
=======
from core.confirmation import ConfirmationGate
from core.executor import Executor, ExecutorError, action_click, action_press_keys, action_scroll
from core.hud import HUD, WatermarkConfig
from core.llm_client import LLMClient
from core.logging_utils import setup_logger
from core.memory import MemoryStore
>>>>>>> main
from core.planner import Planner
from core.tts import TTS
from skills import help as help_skill
from skills import instagram_prepare, open_app, remember_alias, set_folder, type_text, whatsapp_prepare

<<<<<<< codex/build-advanced-local-voice-assistant-jarvis-jbsk9b
MODE_COMMANDS = {
    "Activate Dark Mode": "DARK",
    "Activate Prime Mode": "PRIME",
    "Activate Lock-In": "LOCKIN",
    "Activate Unhinged Mode": "UNHINGED_MAX",
=======
PERSONA_COMMANDS = {
    "activate dark mode": "DARK",
    "activate prime mode": "PRIME",
    "activate lock-in": "LOCKIN",
    "activate lock in": "LOCKIN",
    "activate unhinged mode": "UNHINGED_MAX",
>>>>>>> main
}


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


<<<<<<< codex/build-advanced-local-voice-assistant-jarvis-jbsk9b
=======
def resolve_persona_command(text: str) -> str | None:
    lowered = text.strip().lower()
    return PERSONA_COMMANDS.get(lowered)


>>>>>>> main
def run() -> None:
    root = Path(__file__).parent
    config = load_yaml(root / "config.yaml")
    personas = load_yaml(root / "personas.yaml")

    logger = setup_logger(config)
    stop_event = threading.Event()

<<<<<<< codex/build-advanced-local-voice-assistant-jarvis-jbsk9b
=======
    hud_cfg = config["watermark"]
    hud = HUD(
        WatermarkConfig(
            text=hud_cfg["text"],
            pattern_enabled=bool(hud_cfg["pattern_enabled"]),
            corner_enabled=bool(hud_cfg["corner_enabled"]),
            angle_deg=int(hud_cfg["angle_deg"]),
            spacing_px=int(hud_cfg["spacing_px"]),
        )
    )
    hud.start()

>>>>>>> main
    memory = MemoryStore(
        backend=config.get("memory", {}).get("backend", "sqlite"),
        sqlite_path=config.get("memory", {}).get("sqlite_path", "jarvis_memory.db"),
    )
<<<<<<< codex/build-advanced-local-voice-assistant-jarvis-jbsk9b
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
=======
    current_mode = str(memory.get("persona_mode", config["persona"]["mode"]))

    tts = TTS()
    audio = AudioEngine(config["assistant"])
    llm = LLMClient(config["llm"])
    planner = Planner(llm)
    confirmation_gate = ConfirmationGate()
>>>>>>> main

    def kill_switch() -> None:
        stop_event.set()
        confirmation_gate.cancel()
<<<<<<< codex/build-advanced-local-voice-assistant-jarvis-jbsk9b
        chat_ui.set_status("ABORTED")
        speak_async("Stopped.")
=======
        hud.set_status("ABORTED")
        tts.speak("Stopped.")
>>>>>>> main
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
<<<<<<< codex/build-advanced-local-voice-assistant-jarvis-jbsk9b
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
=======

    executor = Executor(confirmation_gate, stop_event, logger, action_registry)

    def capture_text_input() -> str:
        hud.set_status("Listening...")
        audio.beep()
        clip_path = audio.record_clip(config["assistant"]["max_record_seconds"], root / "last_input.wav")
        text = audio.transcribe(clip_path)
        hud.set_status("Processing...")
        return text

    keyboard.add_hotkey(config["assistant"]["ptt_hotkey"], lambda: None)

    logger.info("Jarvis started with persona=%s", current_mode)

    while True:
        if stop_event.is_set():
            stop_event.clear()

        if keyboard.is_pressed(config["assistant"]["ptt_hotkey"]):
            user_text = capture_text_input()
        else:
            time.sleep(0.2)
            continue

        if not user_text.strip():
            hud.set_status("Idle")
            continue

        persona_target = resolve_persona_command(user_text)
        if persona_target:
            current_mode = persona_target
            memory.set("persona_mode", current_mode)
            hud.set_status(f"Persona: {current_mode}")
            tts.speak(f"Persona switched to {current_mode}.")
            continue

        persona_description = personas.get(current_mode, {}).get("description", "")

        try:
            plan = planner.build_plan(user_text, current_mode, persona_description)
            tts.speak(plan.say)
            executor.execute_plan(plan)
            hud.set_status("Done")
        except ExecutorError as exc:
            logger.error("Execution error: %s", exc)
            hud.set_status("ABORTED")
            tts.speak("Stopped.")
        except Exception as exc:
            logger.exception("Unhandled error: %s", exc)
            hud.set_status("Error")
            tts.speak("I hit a safe failure and stopped.")
>>>>>>> main


if __name__ == "__main__":
    run()
