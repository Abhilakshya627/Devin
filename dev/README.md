# Dev (Offline) Runtime

This directory provides a fully local/offline alternative to the cloud Gemini/LiveKit path used by the rest of the repo. It aims to be drop-in comparable for core capabilities without any API keys or network calls:

- Local LLM inference backends:
  - gpt4all (default, no llama-cpp required)
  - llama.cpp (optional if installed)
- Offline speech-to-text using Vosk.
- Local text-to-speech using pyttsx3 (already used project-wide).
- Simple planning/execution harness compatible with existing tool functions.

Notes
- You must download model files yourself and place them locally. No network fetch is performed by the code.
- By default, we look under `dev/models/` for both LLM and Vosk models. Configure paths via `dev/local_config.json`.

Model placement examples
- GPT4All: put a model file like `mistral-7b-instruct.Q4_0.gguf` or `.bin` into `dev/models/llm/`
- Llama.cpp: put any `.gguf` file into `dev/models/llm/` and set backend to `llama_cpp`
- Vosk: extract a model (e.g., `vosk-model-small-en-us`) into `dev/models/vosk/`

Minimal steps
1) Place a GPT4All or GGUF model in `dev/models/llm/` (directory can contain a single model file).
2) Place a Vosk model in `dev/models/vosk/`.
3) Adjust `dev/local_config.json` if you prefer `llama_cpp` instead of default `gpt4all`.
4) Run the local entrypoint to test chat: `python dev/run_local.py`.

N-gram (no external deps)
- You can run fully offline without any model downloads by training a tiny n-gram model on your own text.
- Prepare a folder with .txt files (your notes, project docs, etc.).
- Train:
```
python dev/train_ngram.py path\to\texts dev\models\llm\ngram_model.json --n 3
```
- Update `dev/local_config.json`:
```
{
  "llm": {
    "backend": "ngram",
    "model_path": "dev/models/llm/ngram_model.json",
    "n_ctx": 2048,
    "n_threads": 2,
    "n_gpu_layers": 0,
    "temperature": 0.9,
    "top_p": 0.95
  },
  "stt": { "engine": "vosk", "model_path": "dev/models/vosk" }
}
```
- Run:
```
$env:OFFLINE_LLM = "1"
python dev\run_local.py
```
