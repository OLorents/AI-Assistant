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


class Application:
    def __init__(self, cfg, arg_parser):
        self._cfg = cfg
        self._arg_parser = arg_parser

    @staticmethod
    def configure_ctrl_c() -> None:
        try:
            signal.signal(signal.SIGINT, signal.default_int_handler)
        except Exception:
            pass

    async def process_query(self, user_input: str, assistant: AssistantService) -> None:
        try:
            answer = (await assistant.answer(user_input)).strip()
        except Exception as ex:  # noqa: BLE001
            print(f"LLM error: {ex}")
            return
        if not answer:
            print("No answer.")
            return
        print("\n🧾 Answer:")
        print(answer)
        print("\nCan I help you with anything else?")

    async def run(self, argv: List[str]) -> None:
        self.configure_ctrl_c()

        # Build params + assistant once (REPL preserves memory)
        params = EnvConfigProvider().load("")

        # ONE-SHOT
        if len(argv) > 1:
            question, agent_override, model_override = self._arg_parser.parse(argv[1:])
            if agent_override:
                params = AiParameters(
                    agent=ArgParser.normalize_agent(agent_override) or params.agent,
                    model=params.model,
                    provider=params.provider,
                    api_key=params.api_key,
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
            assistant = AssistantService(params, client)
            print(f"Agent: {params.agent} | Provider: {params.provider} | Model: {params.model}")
            if params.provider == "stub":
                print("⚠️ No API key detected — using stub client. Set OPENAI_API_KEY or GEMINI_API_KEY in .env.")
            await self.process_query(question, assistant)
            return

        # REPL
        client = LLMClientFactory.create(params)
        assistant = AssistantService(params, client)
        print(f"Agent: {params.agent} | Provider: {params.provider} | Model: {params.model}")
        if params.provider == "stub":
            print("⚠️ No API key detected — using stub client. Set OPENAI_API_KEY or GEMINI_API_KEY in .env.")
        print("Type your request (or 'exit')")
        while True:
            try:
                user_in = input("\nHow can I help?\n> ")
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break
            if not user_in or user_in.strip().lower() == "exit":
                print("Bye!")
                break
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
