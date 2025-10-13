"""Main application for CLI interface."""

import asyncio
import signal
import sys
from typing import List
from .args import ArgParser
from ..config.provider import EnvConfigProvider
from ..config.params import AiParameters
from ..llm.factory import LLMClientFactory
from ..core.assistant import AssistantService
from ..core.history import HistoryManager


class Application:
    def __init__(self, cfg, arg_parser):
        self._cfg = cfg
        self._arg_parser = arg_parser
    
    @staticmethod
    def _get_provider_for_agent(agent: str) -> str:
        """Map agent to appropriate provider."""
        if agent == "openaiagent":
            return "openai"
        elif agent == "geminiagent":
            return "gemini"
        else:
            return "stub"  # fallback for unknown agents
    
    @staticmethod
    def _get_api_key_for_provider(provider: str) -> str:
        """Get the appropriate API key for the provider."""
        import os
        if provider == "openai":
            return os.getenv("OPENAI_API_KEY", "")
        elif provider == "gemini":
            return os.getenv("GEMINI_API_KEY", "")
        else:
            return ""
    
    @staticmethod
    def _get_default_model_for_provider(provider: str) -> str:
        """Get the default model for the provider."""
        import os
        if provider == "openai":
            return os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        elif provider == "gemini":
            return os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
        else:
            return "stub-model"

    @staticmethod
    def configure_ctrl_c() -> None:
        try:
            signal.signal(signal.SIGINT, signal.default_int_handler)
        except Exception:
            pass
    
    def handle_history_command(self, argv: List[str], assistant: AssistantService = None) -> None:
        """Handle history management commands."""
        command, _ = self._arg_parser.parse_history_command(argv)
        
        if command == "clear":
            self._clear_current_conversation(assistant)
        else:
            self._show_history_help()
    
    def _clear_current_conversation(self, assistant: AssistantService = None) -> None:
        """Clear the current conversation history."""
        if assistant:
            assistant.clear_history()
            print("Current conversation history cleared.")
        else:
            print("No active conversation to clear.")
    
    def _show_history_help(self) -> None:
        """Show help for history commands."""
        print("\nHistory Commands:")
        print("  history clear         - Clear current conversation")
        print("  history help          - Show this help")

    async def process_query(self, user_input: str, assistant: AssistantService) -> None:
        try:
            answer = (await assistant.answer(user_input)).strip()
        except Exception as ex:  # noqa: BLE001
            print(f"LLM error: {ex}")
            return
        if not answer:
            print("No answer.")
            return
        print("\nAnswer:")
        print(answer)
        print("\nCan I help you with anything else?")

    async def run(self, argv: List[str]) -> None:
        self.configure_ctrl_c()

        # Check for history commands first
        if len(argv) > 1 and self._arg_parser.is_history_command(argv[1:]):
            self.handle_history_command(argv[1:])
            return

        # Build params + assistant once (REPL preserves memory)
        params = EnvConfigProvider().load()
        history_manager = HistoryManager()

        # ONE-SHOT
        if len(argv) > 1:
            question, agent_override, model_override = self._arg_parser.parse(argv[1:])
            if agent_override:
                normalized_agent = ArgParser.normalize_agent(agent_override) or params.agent
                provider = self._get_provider_for_agent(normalized_agent)
                api_key = self._get_api_key_for_provider(provider)
                model = self._get_default_model_for_provider(provider)
                params = AiParameters(
                    agent=normalized_agent,
                    model=model,
                    provider=provider,
                    api_key=api_key,
                    system_prompt=params.system_prompt,
                )
            if model_override:
                params = AiParameters(
                    agent=params.agent,
                    model=model_override,
                    provider=params.provider,
                    api_key=params.api_key,
                    system_prompt=params.system_prompt,
                )
            client = LLMClientFactory.create(params)
            assistant = AssistantService(params, client, history_manager)
            print(f"Agent: {params.agent} | Provider: {params.provider} | Model: {params.model}")
            if params.provider == "stub":
                print("WARNING: No API key detected — using stub client. Set OPENAI_API_KEY or GEMINI_API_KEY in .env.")
            await self.process_query(question, assistant)
            return

        # REPL
        client = LLMClientFactory.create(params)
        assistant = AssistantService(params, client, history_manager)
        print(f"Agent: {params.agent} | Provider: {params.provider} | Model: {params.model}")
        if params.provider == "stub":
            print("WARNING: No API key detected — using stub client. Set OPENAI_API_KEY or GEMINI_API_KEY in .env.")
        print("Type your request (or 'exit', 'history help' for history commands)")
        while True:
            try:
                user_in = input("\nHow can I help?\n> ")
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break
            if not user_in or user_in.strip().lower() == "exit":
                print("Bye!")
                break
            
            # Check for history commands in REPL
            command_parts = user_in.strip().split()
            if self._arg_parser.is_history_command(command_parts):
                self.handle_history_command(command_parts, assistant)
                continue
            
            try:
                await self.process_query(user_in, assistant)
            except KeyboardInterrupt:
                print("\nCanceled.")
            except Exception as e:  # noqa: BLE001
                print(f"Error: {e}", file=sys.stderr)


async def main_async(argv: list[str]) -> None:
    """Main async entry point."""
    arg_parser = ArgParser()
    app = Application(
        cfg=EnvConfigProvider(),
        arg_parser=arg_parser,
    )
    await app.run(argv)


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(main_async(sys.argv))
    except KeyboardInterrupt:
        print("\nBye!")
