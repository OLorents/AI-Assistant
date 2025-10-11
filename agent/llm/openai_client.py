"""OpenAI client implementation (test-friendly)."""

import asyncio
import os
from typing import List, Dict, Optional, Any
from importlib import import_module


def OpenAI(*args, **kwargs):  # <-- patch target for tests
    """Late-resolve openai.OpenAI so patches on openai.OpenAI are honored."""
    cls = getattr(import_module("openai"), "OpenAI")
    return cls(*args, **kwargs)


class OpenAIClient:
    def __init__(self, model: str, api_key: Optional[str]) -> None:
        self._model = model
        self._client = None
        try:
            if not api_key:
                raise ImportError("missing key")
            base = os.getenv("OPENAI_BASE") or None
            # Call our patchable shim; tests can patch either:
            # - agent.llm.openai_client.OpenAI
            # - openai.OpenAI (picked up via import_module above)
            self._client = OpenAI(api_key=api_key, base_url=base)
        except Exception:
            self._client = None  # complete() will return a stub

    async def complete(
        self,
        prompt: str,
        system_prompt: str,
    ) -> str:
        if not self._client:
            return "(OpenAI unavailable)"

        def _call() -> str:
            messages: List[Dict[str, str]] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            resp = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.2,
            )
            content = getattr(resp.choices[0].message, "content", "") or ""
            return content.strip() or ""

        return await asyncio.to_thread(_call)
    
    async def complete_with_history(
        self,
        prompt: str,
        system_prompt: str,
        history: List[Dict[str, Any]]
    ) -> str:
        if not self._client:
            return "(OpenAI unavailable)"

        def _call() -> str:
            messages: List[Dict[str, str]] = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history
            for msg in history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current user prompt
            messages.append({"role": "user", "content": prompt})

            resp = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.2,
            )
            content = getattr(resp.choices[0].message, "content", "") or ""
            return content.strip() or ""

        return await asyncio.to_thread(_call)
