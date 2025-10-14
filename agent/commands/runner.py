"""Command execution interfaces and implementations."""

import asyncio
from typing import Protocol, Tuple
from ..utils.os_utils import OS


class CommandRunner(Protocol):
    async def run(self, command: str) -> Tuple[int, str, str]:
        ...


class SubprocessRunner:
    async def run(self, command: str) -> Tuple[int, str, str]:
        # For PowerShell commands, run them directly
        if command.startswith("powershell -Command"):
            # Extract the actual PowerShell command
            ps_command = command[20:].strip('"')  # Remove "powershell -Command " prefix and quotes
            proc = await asyncio.create_subprocess_exec(
                "powershell", "-Command", ps_command,
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
        else:
            args = OS.shell_and_args(command)
            proc = await asyncio.create_subprocess_exec(
                *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
        stdout, stderr = await proc.communicate()
        return proc.returncode, (stdout or b"").decode(), (stderr or b"").decode()
