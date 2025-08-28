# Devin

AI assistant with tools, voice, and screen interaction.

- Cloud path: Google Gemini + LiveKit
- Offline path: see `dev/` for local LLM (llama.cpp) and offline STT (Vosk)

Quick start (offline)
- Place a GGUF model at `dev/models/llm/model.gguf`
- Place a Vosk model directory at `dev/models/vosk`
- Set environment variable `OFFLINE_LLM=1`
- Run: `python dev/run_local.py`

Windows PowerShell example
```
$env:OFFLINE_LLM = "1"
python dev\run_local.py
```
