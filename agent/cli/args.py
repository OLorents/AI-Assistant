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
    
    def is_history_command(self, argv: List[str]) -> bool:
        """Check if the command is a history management command."""
        if not argv:
            return False
        first_arg = argv[0].lower()
        return first_arg in ["history", "hist", "h"]
    
    def parse_history_command(self, argv: List[str]) -> Tuple[str, Optional[str]]:
        """Parse history management commands."""
        if len(argv) < 2:
            return "list", None
        
        command = argv[1].lower()
        target_id = argv[2] if len(argv) > 2 else None
        
        if command in ["list", "ls", "show"]:
            return "list", None
        elif command in ["show", "view"] and target_id:
            return "show", target_id
        elif command in ["delete", "del", "remove"] and target_id:
            return "delete", target_id
        elif command in ["clear", "reset"]:
            return "clear", None
        elif command in ["save"]:
            return "save", None
        else:
            return "help", None

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

