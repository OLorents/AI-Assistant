"""User confirmation interfaces and implementations."""

from typing import Protocol


class UserConfirmation(Protocol):
    async def confirm(self, command: str) -> bool:
        ...


class StdInConfirmation:
    async def confirm(self, command: str) -> bool:
        print("\nIn order to do that, you need to run:")
        print(command)
        try:
            reply = input("Would you like to run this command? [y/N] ").strip().lower()
            return reply == "y"
        except (EOFError, KeyboardInterrupt):
            return False
