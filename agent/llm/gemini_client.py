"""Gemini client implementation (test-friendly)."""

import asyncio
from typing import Optional
from importlib import import_module


def genai():  # <-- patch target for tests
    """
    Late-resolve google.generativeai so patches on either:
      - agent.llm.gemini_client.genai (side_effect/return_value), or
      - google.generativeai
    are honored.
    """
    return import_module("google.generativeai")


class GeminiClient:
    def __init__(self, model: str, api_key: Optional[str]) -> None:
        self._model = None
        try:
            if not api_key:
                raise ImportError("missing key")

            g = genai()  # triggers side_effect if the test patched this callable
            g.configure(api_key=api_key)
            self._model = g.GenerativeModel(model)
        except Exception:
            # Degrade gracefully; complete() will return a stub string
            self._model = None

    async def complete(
        self,
        prompt: str,
        system_prompt: str,
    ) -> str:
        if not self._model:
            return "(Gemini unavailable)"

        def _build_full_prompt() -> str:
            return f"{system_prompt}\n\nUser: {prompt}"

        def _call() -> str:
            full_prompt = _build_full_prompt()
            resp = self._model.generate_content(full_prompt)
            text = getattr(resp, "text", "") or ""
            return text.strip() or "(empty)"

        return await asyncio.to_thread(_call)
