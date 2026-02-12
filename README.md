# JARVIS-O

Modular offline-first desktop voice assistant using Vosk + pyttsx3 + Ollama/Mistral.

## Features
- Deterministic local command routing for time/date/open/search/shutdown confirmation.
- Ollama (`mistral`) fallback for conversational queries.
- Safety confirmation flow for destructive actions (`confirm shutdown`).
- Minimal PyQt6 GUI with status, transcript, and listening toggle.

## Requirements
- Python 3.11+
- Ollama installed locally and running (`ollama serve`)
- Mistral model pulled (`ollama pull mistral`)
- A local Vosk model path configured in `config.json`

## Install
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m jarviso
```

## Ollama setup
```bash
ollama serve
ollama pull mistral
```

## Arya Branding
- Startup console prints the Arya build banner once.
- Logs include an `[Arya Build]` prefix and startup header.
- GUI includes an always-visible bottom-right watermark.
- Status bar permanently shows Arya branding.
- `Help -> About` displays branding, credits note, and LICENSE opener.

## Troubleshooting
- **Ollama not running**: Assistant responds with: "Ollama is not running. Start Ollama and try again."
- **Model missing**: run `ollama pull mistral`.
- **Microphone permissions**: Allow mic access in OS privacy settings.
- **No Vosk model found**: download a model and set `vosk_model_path` in `config.json`.

## Tests
```bash
pytest -q
```
