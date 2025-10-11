from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AiParameters:
    agent: str
    model: str
    provider: str  # "gemini" | "openai" | "stub"
    api_key: Optional[str] = None
    system_prompt: Optional[str] = None
