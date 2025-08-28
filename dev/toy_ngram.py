import os
import json
import random
from collections import defaultdict, Counter
from typing import Dict, Tuple, List


def _tokenize(text: str) -> List[str]:
    # Simple whitespace tokenization; lowercase to reduce sparsity
    return text.lower().split()


class NGramLM:
    """Minimal word-level n-gram language model.

    - Train from local text.
    - Save/load as JSON.
    - Generate text by sampling next tokens from counts.
    """

    def __init__(self, n: int = 3):
        if n < 2:
            raise ValueError("n must be >= 2")
        self.n = n
        # Mapping from context tuple -> Counter of next tokens
        self.model: Dict[Tuple[str, ...], Counter] = defaultdict(Counter)

    def train(self, text: str):
        tokens = _tokenize(text)
        if len(tokens) < self.n:
            return
        for i in range(len(tokens) - self.n + 1):
            context = tuple(tokens[i : i + self.n - 1])
            nxt = tokens[i + self.n - 1]
            self.model[context][nxt] += 1

    def train_from_files(self, folder: str):
        for root, _, files in os.walk(folder):
            for name in files:
                if name.lower().endswith('.txt'):
                    path = os.path.join(root, name)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            self.train(f.read())
                    except Exception:
                        pass

    def save(self, path: str):
        data = {
            "n": self.n,
            "model": {
                "|".join(ctx): dict(cnt) for ctx, cnt in self.model.items()
            },
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    @classmethod
    def load(cls, path: str) -> "NGramLM":
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        lm = cls(n=int(data.get("n", 3)))
        model_json: Dict[str, Dict[str, int]] = data.get("model", {})
        for ctx_str, cnt_dict in model_json.items():
            ctx = tuple(ctx_str.split("|") ) if ctx_str else tuple()
            lm.model[ctx] = Counter({k: int(v) for k, v in cnt_dict.items()})
        return lm

    def _sample_next(self, context: Tuple[str, ...], temperature: float = 1.0) -> str:
        counts = self.model.get(context)
        if not counts:
            # backoff: drop earliest token
            if len(context) > 0:
                return self._sample_next(context[1:], temperature)
            # as last resort, pick from most frequent next across model
            if not self.model:
                return ""
            all_next = Counter()
            for c in self.model.values():
                all_next.update(c)
            choices, weights = zip(*all_next.items())
        else:
            choices, weights = zip(*counts.items())

        # Apply temperature by scaling weights
        if temperature and temperature > 0 and temperature != 1.0:
            # Convert counts to probabilities then apply temperature via power
            total = float(sum(weights))
            probs = [w / total for w in weights]
            # Temperature scaling: p_i^(1/T) then renormalize
            T = float(temperature)
            scaled = [max(p, 1e-12) ** (1.0 / T) for p in probs]
            s_total = sum(scaled)
            probs = [s / s_total for s in scaled]
        else:
            total = float(sum(weights))
            probs = [w / total for w in weights]

        r = random.random()
        acc = 0.0
        for tok, p in zip(choices, probs):
            acc += p
            if r <= acc:
                return tok
        return choices[-1]

    def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.9) -> str:
        tokens = _tokenize(prompt)
        # Initialize context
        if len(tokens) < self.n - 1:
            # pad with start tokens
            context = tuple((['<s>'] * (self.n - 1 - len(tokens))) + tokens)
        else:
            context = tuple(tokens[-(self.n - 1):])

        generated: List[str] = []
        for _ in range(max_tokens):
            nxt = self._sample_next(context, temperature=temperature)
            if not nxt:
                break
            generated.append(nxt)
            context = tuple((list(context) + [nxt])[1:])

        # Return prompt + generated continuation (keep original prompt casing)
        sep = " " if prompt and not prompt.endswith(" ") else ""
        return (prompt + sep + " ".join(generated)).strip()
