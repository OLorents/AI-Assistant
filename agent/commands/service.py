"""Command service for high-level command execution."""

from .runner import CommandRunner
from .confirm import UserConfirmation


class CommandService:
    """High-level API for confirming and running commands."""

    def __init__(self, runner: CommandRunner, confirmation: UserConfirmation) -> None:
        self._runner = runner
        self._confirmation = confirmation

    async def maybe_run(self, command: str) -> None:
        if not await self._confirmation.confirm(command):
            print("Skipping execution.")
            return
        print("\n> Running the command...")
        code, stdout, stderr = await self._runner.run(command)
        print("\n---------------- Command output ----------------")
        if stdout.strip():
            print(stdout.rstrip())
        if stderr.strip():
            print(f"\n[stderr]\n{stderr.rstrip()}")
        print(f"(exit {code})")
