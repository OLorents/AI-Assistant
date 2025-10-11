"""Stub client implementation for testing."""



class StubClient:
    def __init__(self, model: str) -> None:
        self._model = model

    async def complete(self, prompt: str, system_prompt: str) -> str:
        return f"[stub:{self._model}] You said: {prompt}"
