"""Assistant service for handling user interactions."""

from ..config.params import AiParameters
from ..llm.interfaces import LLMClient


class AssistantService:
    def __init__(self, params: AiParameters, client: LLMClient) -> None:
        self._p = params
        self._client = client

    async def answer(self, user_prompt: str) -> str:
        if not user_prompt.strip():
            return "Please enter a non-empty request."
        system = self._p.system_prompt or f"You are {self._p.agent}, a helpful assistant."
        reply = await self._client.complete(user_prompt, system)
        return reply
