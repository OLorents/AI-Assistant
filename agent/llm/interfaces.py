"""LLM client interfaces."""

from typing import Protocol


class LLMClient(Protocol):
    async def complete(self, prompt: str, system_prompt: str) -> str:
        ...
