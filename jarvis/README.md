# Jarvis (Windows 11 Local Voice Assistant)

Jarvis is a modular two-layer voice assistant for Python 3.11:
- **Brain (Planner):** Mistral-based JSON-only planner.
- **Executor:** strict validator + allowlisted action runtime with confirmation gates.

## 1) Setup (Python 3.11)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2) Playwright install

```bash
playwright install chromium
```

## 3) Ollama install + model pull (default backend)

1. Install Ollama from official installer.
2. Start Ollama service.
3. Pull Mistral model:

```bash
ollama pull mistral
```

Jarvis default config points to:
`http://localhost:11434/api/chat`

## 4) Mistral Cloud backend

Set `llm.backend: mistral_cloud` in `config.yaml` and export your API key:

```bash
setx MISTRAL_API_KEY "your_key_here"
```

## 5) Run Jarvis

```bash
python main.py
```

## Wake word system

- Wake phrase configurable via `assistant.wake_word_phrase`.
- On detection: beep, HUD `Listening...`, records 3–7s, then STT.
- Wake word can be disabled with `assistant.wake_word_enabled: false`.
- Push-to-talk hotkey (default `F9`) is always available.

## Confirmation system (critical safety)

For EXTERNAL/irreversible actions, plans must include:
- `require_confirmation`
- `WAIT_CONFIRMATION`
- explicit finalize action (`*_finalize_*`)

Executor blocks finalize actions without a confirmation gate.

## Kill switch

- Global hotkey: `F12`
- Immediately sets STOP_EVENT, aborts execution, cancels confirmation wait.
- HUD updates to `ABORTED` and TTS says `Stopped.`

## Watermarking

HUD always includes watermark `Arya VL`:
- bottom-right corner watermark
- repeating diagonal low-contrast pattern
- configurable angle/spacing in `config.yaml`

## Memory

Local persistent memory supports:
- contact aliases
- exports folder
- caption template
- persona mode preference

## Adding skills

1. Add a new file under `skills/` with a callable.
2. Register it in `main.py` `action_registry`.
3. Add action name to executor allowlist in `core/executor.py`.
4. In planner prompt/design, ensure action is only planned when safe.

## Logs

Rotating logs are written to `logs/jarvis.log` with:
- timestamp
- skill/action name
- confirmation events
- errors

No stealth or hidden logging is implemented.
