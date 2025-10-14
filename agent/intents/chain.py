"""Intent chain for processing user intents."""

from typing import Iterable
from .base import IntentHandler, IntentContext


class IntentChain:
    def __init__(self, handlers: Iterable[IntentHandler]) -> None:
        self._handlers = list(handlers)

    async def try_handle(self, user_input: str, ctx: IntentContext) -> bool:
        for h in self._handlers:
            if h.matches(user_input):
                return await h.handle(user_input, ctx)
        return False
