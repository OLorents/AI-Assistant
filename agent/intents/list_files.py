"""List files intent handler."""

import re
from .base import IntentContext
from ..utils.os_utils import OS


class ListFilesHandler:
    _PATTERN = re.compile(
        r"""(?xi)
        (?:\b(list|show|display|print)\b .* \b(file|files|dir|directory|folder)s?\b)
        | \b(ls|dir)\b
        | \bcurrent\s+files\b
        # optional: uncomment if you want “files” alone to match
        # | \bfiles\b
        """
    )

    def matches(self, user_input: str) -> bool:
        return bool(self._PATTERN.search(user_input))

    async def handle(self, user_input: str, ctx: IntentContext) -> bool:
        want_all = re.search(r"\b(all|hidden|including\s+hidden|/a|-a)\b", user_input, re.I) is not None
        if OS.is_windows():
            cmd = f"powershell -Command \"Get-ChildItem {'-Force' if want_all else ''}\""
        else:
            cmd = "ls -la" if want_all else "ls -l"
        await ctx.commands.maybe_run(cmd)
        return True