"""LLM client interfaces."""

from typing import Protocol, List, Dict, Any


class LLMClient(Protocol):
    async def complete(self, prompt: str, system_prompt: str) -> str:
        ...
    
    async def complete_with_history(
        self, 
        prompt: str, 
        system_prompt: str, 
        history: List[Dict[str, Any]]
    ) -> str:
        ...
