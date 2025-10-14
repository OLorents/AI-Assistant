"""Time-only intent handler."""

import re
from .base import IntentContext
from ..utils.os_utils import OS


class TimeHandler:
    _PATTERN = re.compile(r"\b(what'?s\s+the\s+time|current\s+time|local\s+time|time\s+(now|right\s*now))\b", re.I)

    def matches(self, user_input: str) -> bool:
        return bool(self._PATTERN.search(user_input))

    async def handle(self, user_input: str, ctx: IntentContext) -> bool:
        cmd = "powershell -Command \"Get-Date -Format HH:mm:ss\"" if OS.is_windows() else "date '+%T'"
        await ctx.commands.maybe_run(cmd)
        return True
