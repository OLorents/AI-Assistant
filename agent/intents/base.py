"""Intent handling base classes."""

from typing import Protocol
from ..commands.service import CommandService


class IntentHandler(Protocol):
    def matches(self, user_input: str) -> bool:
        ...

    async def handle(self, user_input: str, ctx: "IntentContext") -> bool:
        ...


class IntentContext:
    def __init__(self, command_service: CommandService) -> None:
        self.commands = command_service
