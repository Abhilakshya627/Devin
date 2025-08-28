import os
import asyncio
from typing import List, Dict

# Reuse tools via existing decorators; offline mode will route LLM to local
from tools import (
    initialize_devin,
    devin_command_center,
)
from gemini_client import get_gemini_client


async def chat_once(prompt: str) -> str:
    client = get_gemini_client()
    return await client.generate_content(prompt)


async def run_demo():
    print(await initialize_devin(None))
    out = await chat_once("Introduce yourself briefly as a local offline Devin.")
    print("\nAI:", out)
    plan = await devin_command_center("Take a screenshot and explain what you see.", None)
    print("\nPlan:\n", plan)


def main():
    os.environ.setdefault("OFFLINE_LLM", "1")
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
