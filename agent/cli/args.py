"""Command line argument parsing."""

from typing import List, Tuple, Optional


class ArgParser:
    def parse(self, argv: List[str]) -> Tuple[str, Optional[str], Optional[str]]:
        agent = None
        model = None
        parts: List[str] = []
        i = 0
        while i < len(argv):
            a = argv[i]
            low = a.lower()
            if low.startswith("--agent="):
                agent = a.split("=", 1)[1]
            elif low == "--agent" and i + 1 < len(argv):
                i += 1
                agent = argv[i]
            elif low.startswith("--model="):
                model = a.split("=", 1)[1]
            elif low == "--model" and i + 1 < len(argv):
                i += 1
                model = argv[i]
            else:
                parts.append(a)
            i += 1
        return (" ".join(parts), agent, model)

    @staticmethod
    def normalize_agent(v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        vv = v.strip().lower()
        if vv in ("openaiagent", "openai"):
            return "openaiagent"
        if vv in ("geminiagent", "gemini", "google"):
            return "geminiagent"
        return vv

