import os
import importlib
from typing import Optional


class OfflineSTT:
    """Offline speech-to-text using Vosk.

    Requires a local Vosk model directory. No network calls.
    """
    def __init__(self, model_path: str):
        self.model_path = model_path
        self._rec = None
        self._model = None

    def initialize(self):
        if self._rec is not None:
            return
        try:
            vosk_mod = importlib.import_module("vosk")
            Model = getattr(vosk_mod, "Model")
            KaldiRecognizer = getattr(vosk_mod, "KaldiRecognizer")
        except Exception as e:
            raise RuntimeError("vosk not installed. Install it offline and retry.") from e

        if not os.path.isdir(self.model_path):
            raise FileNotFoundError(f"Vosk model directory not found: {self.model_path}")

        self._model = Model(self.model_path)
        self._KaldiRecognizer = KaldiRecognizer

    def recognize_wav_file(self, wav_path: str) -> Optional[str]:
        """Transcribe a local WAV file path (16kHz mono recommended)."""
        if self._model is None:
            self.initialize()
        try:
            import wave
        except ImportError as e:
            raise RuntimeError("wave module required") from e

        with wave.open(wav_path, "rb") as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in (8000, 16000, 32000, 44100):
                # For simplicity, assume input is already suitable. For robust usage, resample offline.
                pass

            rec = self._KaldiRecognizer(self._model, wf.getframerate())
            text = None
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    pass
            final = rec.FinalResult()
            # final is a JSON string like {"text": "..."}
            try:
                import json
                j = json.loads(final)
                text = j.get("text", "").strip()
            except Exception:
                text = ""
            return text or None
