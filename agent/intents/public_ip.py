"""Public IP intent handler."""

import re
from .base import IntentContext
from ..utils.os_utils import OS


class PublicIpHandler:
    _PATTERN = re.compile(r"\b(my|public|external)\s+ip\b|^ip$|what is my ip", re.I)

    def matches(self, user_input: str) -> bool:
        return bool(self._PATTERN.search(user_input))

    async def handle(self, user_input: str, ctx: IntentContext) -> bool:
        cmd = "powershell -Command \"(Invoke-RestMethod 'https://ifconfig.me/ip')\"" if OS.is_windows() else "curl -s https://ifconfig.me"
        await ctx.commands.maybe_run(cmd)
        return True
