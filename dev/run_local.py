import os
import json
from dev.local_llm import load_config, LocalLLM


def main():
    cfg = load_config("dev/local_config.json")
    llm = LocalLLM(cfg)

    system = "You are Devin, a helpful local assistant that can plan and use tools. Keep answers concise."
    print("Local LLM ready. Type your message (or 'exit'):")
    while True:
        try:
            user = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user or user.lower() in {"exit", "quit"}:
            break
        msg = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        out = llm.chat(msg, max_tokens=512)
        print("Assistant>", out)


if __name__ == "__main__":
    main()
