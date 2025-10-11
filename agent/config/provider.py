from __future__ import annotations
import os
from .params import AiParameters

# --- dotenv load (robust) ---
try:
    from dotenv import load_dotenv, find_dotenv
    # 1) Try CWD upwards (when you run `python -m agent.app` from project root)
    env_path = find_dotenv(usecwd=True)
    # 2) Fallback to repo root (two levels above this file: agent/config -> <repo>/.env)
    if not env_path:
        import pathlib
        env_path = str(pathlib.Path(__file__).resolve().parents[2] / ".env")
    load_dotenv(env_path, override=True)

    # Optional debug: set DEBUG_DOTENV=1 in your .env to print what was loaded
    if os.getenv("DEBUG_DOTENV") == "1":
        print(f"[dotenv] Loaded: {env_path}")
        print("[dotenv] Has OPENAI_API_KEY:", bool(os.getenv("OPENAI_API_KEY")))
        print("[dotenv] Has GEMINI_API_KEY:", bool(os.getenv("GEMINI_API_KEY")))
except Exception:
    # If python-dotenv isn't installed, this silently falls through (will use stub)
    pass


class EnvConfigProvider:
    def load(self, question: str = "") -> AiParameters:
        agent = os.getenv("AGENT") or os.getenv("AI_AGENT") or "DefaultAgent"
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        # Prefer Gemini if both present; swap these two if you want OpenAI first
        if gemini_key:
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            return AiParameters(agent=agent, model=model, provider="gemini", api_key=gemini_key)
        if openai_key:
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            return AiParameters(agent=agent, model=model, provider="openai", api_key=openai_key)

        return AiParameters(agent=agent, model="stub-model", provider="stub")
