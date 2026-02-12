from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

import keyboard
import yaml

from core.audio import AudioEngine
from core.confirmation import ConfirmationGate
from core.executor import Executor, ExecutorError, action_click, action_press_keys, action_scroll
from core.hud import HUD, WatermarkConfig
from core.llm_client import LLMClient
from core.logging_utils import setup_logger
from core.memory import MemoryStore
from core.planner import Planner
from core.tts import TTS
from skills import help as help_skill
from skills import instagram_prepare, open_app, remember_alias, set_folder, type_text, whatsapp_prepare

PERSONA_COMMANDS = {
    "activate dark mode": "DARK",
    "activate prime mode": "PRIME",
    "activate lock-in": "LOCKIN",
    "activate lock in": "LOCKIN",
    "activate unhinged mode": "UNHINGED_MAX",
}


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def resolve_persona_command(text: str) -> str | None:
    lowered = text.strip().lower()
    return PERSONA_COMMANDS.get(lowered)


def run() -> None:
    root = Path(__file__).parent
    config = load_yaml(root / "config.yaml")
    personas = load_yaml(root / "personas.yaml")

    logger = setup_logger(config)
    stop_event = threading.Event()

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

    memory = MemoryStore(
        backend=config.get("memory", {}).get("backend", "sqlite"),
        sqlite_path=config.get("memory", {}).get("sqlite_path", "jarvis_memory.db"),
    )
    current_mode = str(memory.get("persona_mode", config["persona"]["mode"]))

    tts = TTS()
    audio = AudioEngine(config["assistant"])
    llm = LLMClient(config["llm"])
    planner = Planner(llm)
    confirmation_gate = ConfirmationGate()

    def kill_switch() -> None:
        stop_event.set()
        confirmation_gate.cancel()
        hud.set_status("ABORTED")
        tts.speak("Stopped.")
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


if __name__ == "__main__":
    run()
