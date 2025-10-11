"""Stub client implementation for testing."""

from typing import List, Dict, Any


class StubClient:
    def __init__(self, model: str) -> None:
        self._model = model

    async def complete(self, prompt: str, system_prompt: str) -> str:
        return f"[stub:{self._model}] You said: {prompt}"
    
    async def complete_with_history(
        self,
        prompt: str,
        system_prompt: str,
        history: List[Dict[str, Any]]
    ) -> str:
        history_text = ""
        if history:
            history_text = f" (with {len(history)} previous messages)"
        return f"[stub:{self._model}] You said: {prompt}{history_text}"
