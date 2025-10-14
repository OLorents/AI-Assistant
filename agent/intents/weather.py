"""Weather intent handler."""

import re
from .base import IntentContext
from ..utils.os_utils import OS


class WeatherHandler:
    _PATTERN = re.compile(r"weather", re.I)
    
    def matches(self, user_input: str) -> bool:
        return bool(self._PATTERN.search(user_input))

    async def handle(self, user_input: str, ctx: IntentContext) -> bool:
        m = re.search(r"weather\s+(in|for)\s+(?P<city>.+)$", user_input or "", re.I)
        city = (m.group("city").strip() if m else "").replace(" ", "_").rstrip(".!?")
        if OS.is_windows():
            cmd = f"curl.exe -s https://wttr.in/{city}" if city else "curl.exe -s https://wttr.in"
        else:
            cmd = f"curl -s https://wttr.in/{city}" if city else "curl -s https://wttr.in"
        await ctx.commands.maybe_run(cmd)
        return True
