"""Date and time intent handler."""

import re
from .base import IntentContext
from ..utils.os_utils import OS


class DateTimeHandler:
    _PATTERN = re.compile(
        r"\b(datetime|date\s*time|time\s*and\s*date|current\s+(date\s+and\s+time|datetime)|what'?s\s+the\s+date\s+and\s+time)\b", re.I,
    )

    def matches(self, user_input: str) -> bool:
        return bool(self._PATTERN.search(user_input))

    async def handle(self, user_input: str, ctx: IntentContext) -> bool:
        cmd = "powershell -Command \"Get-Date -Format 'yyyy-MM-dd HH:mm:ss'\"" if OS.is_windows() else "date '+%Y-%m-%d %H:%M:%S'"
        await ctx.commands.maybe_run(cmd)
        return True
