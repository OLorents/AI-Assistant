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
    def configure_ctrl_c() -> None:
        try:
            signal.signal(signal.SIGINT, signal.default_int_handler)
        except Exception:
            pass
    
    def handle_history_command(self, argv: List[str], assistant: AssistantService = None) -> None:
        """Handle history management commands."""
        command, target_id = self._arg_parser.parse_history_command(argv)
        history_manager = HistoryManager()
        
        if command == "list":
            self._list_conversations(history_manager)
        elif command == "show" and target_id:
            self._show_conversation(history_manager, target_id)
        elif command == "delete" and target_id:
            self._delete_conversation(history_manager, target_id)
        elif command == "clear":
            self._clear_current_conversation(assistant)
        elif command == "save":
            self._save_current_conversation(assistant)
        else:
            self._show_history_help()
    
    def _list_conversations(self, history_manager: HistoryManager) -> None:
        """List all saved conversations."""
        conversations = history_manager.list_conversations()
        if not conversations:
            print("No saved conversations found.")
            return
        
        print(f"\nSaved Conversations ({len(conversations)}):")
        print("-" * 80)
        for conv in conversations:
            print(f"ID: {conv['id']}")
            print(f"Title: {conv['title']}")
            print(f"Messages: {conv['message_count']}")
            print(f"Updated: {conv['updated_at']}")
            print("-" * 80)
    
    def _show_conversation(self, history_manager: HistoryManager, conversation_id: str) -> None:
        """Show a specific conversation."""
        conversation = history_manager.load_conversation(conversation_id)
        if not conversation:
            print(f"Conversation '{conversation_id}' not found.")
            return
        
        print(f"\nConversation: {conversation.title}")
        print(f"ID: {conversation.id}")
        print(f"Created: {conversation.created_at}")
        print(f"Updated: {conversation.updated_at}")
        print("-" * 80)
        
        for msg in conversation.messages:
            role_icon = "User" if msg.role == "user" else "Assistant"
            print(f"{role_icon} {msg.role.title()}: {msg.content}")
            print()
    
    def _delete_conversation(self, history_manager: HistoryManager, conversation_id: str) -> None:
        """Delete a conversation."""
        if history_manager.delete_conversation(conversation_id):
            print(f"Conversation '{conversation_id}' deleted.")
        else:
            print(f"Conversation '{conversation_id}' not found.")
    
    def _clear_current_conversation(self, assistant: AssistantService = None) -> None:
        """Clear the current conversation history."""
        if assistant:
            assistant.clear_history()
            print("Current conversation history cleared.")
        else:
            print("No active conversation to clear.")
    
    def _save_current_conversation(self, assistant: AssistantService = None) -> None:
        """Save the current conversation."""
        if assistant:
            assistant.save_conversation()
            print("Current conversation saved.")
        else:
            print("No active conversation to save.")
    
    def _show_history_help(self) -> None:
        """Show help for history commands."""
        print("\nHistory Commands:")
        print("  history list          - List all saved conversations")
        print("  history show <id>     - Show a specific conversation")
        print("  history delete <id>   - Delete a conversation")
        print("  history clear         - Clear current conversation")
        print("  history save          - Save current conversation")
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
        params = EnvConfigProvider().load("")
        history_manager = HistoryManager()

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
            if self._arg_parser.is_history_command([user_in]):
                self.handle_history_command([user_in], assistant)
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
