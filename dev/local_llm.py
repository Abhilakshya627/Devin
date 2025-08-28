import json
import os
from dataclasses import dataclass
import importlib
from typing import Optional, List, Dict, Any, Tuple


@dataclass
class LocalLLMConfig:
    backend: str
    model_path: str
    n_ctx: int = 4096
    n_threads: int = 4
    n_gpu_layers: int = 0
    temperature: float = 0.2
    top_p: float = 0.95


class LocalLLM:
    """Minimal offline LLM wrapper.

    Supports llama.cpp Python bindings when backend == 'llama_cpp'.
    Intentionally avoids any network calls. Model files must exist locally.
    """

    def __init__(self, config: LocalLLMConfig):
        self.config = config
        self._impl = None

        backend = (config.backend or "").lower()
        if backend == "llama_cpp":
            self._init_llamacpp()
        elif backend == "gpt4all":
            self._init_gpt4all()
        elif backend == "ngram":
            self._init_ngram()
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _init_llamacpp(self):
        try:
            llama_mod = importlib.import_module("llama_cpp")
            Llama = getattr(llama_mod, "Llama")
        except Exception as e:
            raise RuntimeError("llama-cpp-python not installed. Install it offline and retry.") from e

        model_file = self._resolve_model_file(self.config.model_path)
        if not os.path.exists(model_file):
            raise FileNotFoundError(f"LLM model not found at {model_file}")

        self._impl = Llama(
            model_path=model_file,
            n_ctx=self.config.n_ctx,
            n_threads=self.config.n_threads,
            n_gpu_layers=self.config.n_gpu_layers,
            logits_all=False,
            verbose=False,
        )

    def _init_gpt4all(self):
        try:
            gpt4all_mod = importlib.import_module("gpt4all")
            GPT4All = getattr(gpt4all_mod, "GPT4All")
        except Exception as e:
            raise RuntimeError("gpt4all not installed. Install it offline and retry.") from e

        model_file = self._resolve_model_file(self.config.model_path)
        if not os.path.exists(model_file):
            raise FileNotFoundError(f"GPT4All model not found at {model_file}")

        model_dir, model_name = os.path.split(model_file)
        # Disallow downloads to keep fully offline
        self._impl = GPT4All(model_name, model_path=model_dir, allow_download=False)

    def _init_ngram(self):
        try:
            from dev.toy_ngram import NGramLM
        except Exception as e:
            raise RuntimeError("Failed to import local n-gram model") from e
        # If model_path points to a .json, load; if it points to a folder, train from text files
        path = self.config.model_path
        if os.path.isdir(path):
            lm = NGramLM(n=3)
            # Train from any .txt files in path
            lm.train_from_files(path)
            # Save to a default file for reuse
            out_json = os.path.join(path, "ngram_model.json")
            try:
                lm.save(out_json)
            except Exception:
                pass
            self._impl = ("ngram", lm)
        elif os.path.isfile(path):
            # If a JSON model exists, load it; else try to train from text file
            if path.lower().endswith(".json"):
                lm = NGramLM.load(path)
                self._impl = ("ngram", lm)
            elif path.lower().endswith(".txt"):
                lm = NGramLM(n=3)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lm.train(f.read())
                self._impl = ("ngram", lm)
            else:
                raise FileNotFoundError(f"Unsupported n-gram source: {path}")
        else:
            raise FileNotFoundError(f"N-gram path not found: {path}")

    def _resolve_model_file(self, path: str) -> str:
        """Accept a file path or a directory and pick a plausible model file.
        Supports .gguf, .bin, .ggml extensions.
        """
        if os.path.isfile(path):
            return path
        if os.path.isdir(path):
            exts = (".gguf", ".bin", ".ggml")
            for name in os.listdir(path):
                if name.lower().endswith(exts):
                    return os.path.join(path, name)
        return path

    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 512) -> str:
        """Simple chat completion.
        messages: [{role: 'system'|'user'|'assistant', content: str}, ...]
        """
        if self._impl is None:
            raise RuntimeError("LLM backend not initialized")

        # Convert to llama.cpp chat_format or simple prompt
        system = "\n".join([m["content"] for m in messages if m["role"] == "system"]) or ""
        history = []
        for m in messages:
            if m["role"] == "user":
                history.append(f"User: {m['content']}")
            elif m["role"] == "assistant":
                history.append(f"Assistant: {m['content']}")
        prompt = (system + "\n\n" if system else "") + "\n".join(history) + "\nAssistant:"

        if isinstance(self._impl, tuple) and self._impl and self._impl[0] == "ngram":
            # toy n-gram backend
            lm = self._impl[1]
            return lm.generate(prompt, max_tokens=max_tokens, temperature=self.config.temperature)
        if hasattr(self._impl, "__call__"):
            # llama.cpp path
            out = self._impl(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                stop=["\nUser:", "</s>"]
            )
            text = out.get("choices", [{}])[0].get("text", "").strip()
            return text
        else:
            # gpt4all path
            try:
                return self._impl.generate(
                    prompt,
                    max_tokens=max_tokens,
                    temp=self.config.temperature,
                    top_p=self.config.top_p
                ).strip()
            except TypeError:
                # Fallback if param names differ by version
                return self._impl.generate(prompt, max_tokens=max_tokens).strip()


def load_config(config_path: str) -> LocalLLMConfig:
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    llm = data.get("llm", {})
    return LocalLLMConfig(
        backend=llm.get("backend", "llama_cpp"),
        model_path=llm.get("model_path", "dev/models/llm/model.gguf"),
        n_ctx=llm.get("n_ctx", 4096),
        n_threads=llm.get("n_threads", 4),
        n_gpu_layers=llm.get("n_gpu_layers", 0),
        temperature=llm.get("temperature", 0.2),
        top_p=llm.get("top_p", 0.95),
    )
