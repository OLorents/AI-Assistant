"""Date-only intent handler."""

import re
from .base import IntentContext
from ..utils.os_utils import OS


class DateHandler:
    _PATTERN = re.compile(r"\b((current|today'?s)\s+date|what'?s\s+the\s+date|date\s+(today|now))\b", re.I)

    def matches(self, user_input: str) -> bool:
        return bool(self._PATTERN.search(user_input))

    async def handle(self, user_input: str, ctx: IntentContext) -> bool:
        cmd = "powershell -Command \"Get-Date -Format yyyy-MM-dd\"" if OS.is_windows() else "date '+%Y-%m-%d'"
        await ctx.commands.maybe_run(cmd)
        return True
