"""Assistant service for handling user interactions."""

from typing import List, Dict, Any, Optional
from ..config.params import AiParameters
from ..llm.interfaces import LLMClient
from .history import HistoryManager
from ..intents.chain import IntentChain
from ..intents.base import IntentContext
from ..commands.service import CommandService
from ..commands.runner import SubprocessRunner
from ..commands.confirm import StdInConfirmation


class AssistantService:
    def __init__(self, params: AiParameters, client: LLMClient, history_manager: Optional[HistoryManager] = None) -> None:
        self._p = params
        self._client = client
        self._history_manager = history_manager or HistoryManager()
        self._command_service = CommandService(SubprocessRunner(), StdInConfirmation())
        self._intent_chain = self._create_intent_chain()

    async def answer(self, user_prompt: str, use_history: bool = True) -> str:
        if not user_prompt.strip():
            return "Please enter a non-empty request."
        
        # Add user message to history
        self._history_manager.add_message("user", user_prompt)
        
        # Check for intents first
        intent_context = IntentContext(self._command_service)
        intent_handled = await self._intent_chain.try_handle(user_prompt, intent_context)
        
        if intent_handled:
            # Intent was handled, add a generic response to history
            reply = "Intent handled successfully."
            self._history_manager.add_message("assistant", reply)
            return reply
        
        # No intent matched, proceed with LLM
        # Build enhanced system prompt
        system = self._build_enhanced_system_prompt()
        
        # Get conversation history
        history = self._history_manager.get_conversation_history()[:-1] if use_history else []  # Exclude current user message
        
        # Get response from LLM
        if use_history and history:
            reply = await self._client.complete_with_history(user_prompt, system, history)
        else:
            reply = await self._client.complete(user_prompt, system)
        
        # Add assistant response to history
        self._history_manager.add_message("assistant", reply)
        
        return reply
    
    def _build_enhanced_system_prompt(self) -> str:
        """Build an enhanced system prompt with better context and instructions."""
        base_prompt = self._p.system_prompt or f"You are {self._p.agent}, a helpful assistant."
        
        # Add context about the current session
        conversation_count = len(self._history_manager.current_conversation.messages) if self._history_manager.current_conversation else 0
        
        enhanced_prompt = f"""{base_prompt}

## Context
- You are responding in a conversational AI assistant session
- Current conversation has {conversation_count} previous messages
- Model: {self._p.model} via {self._p.provider}
- Session started: {self._history_manager.current_conversation.created_at if self._history_manager.current_conversation else 'now'}

## Instructions
- Provide accurate, helpful, and concise responses
- If you're unsure about something, say so rather than guessing
- For coding questions, provide working examples when possible
- For complex topics, break down explanations into clear steps
- Maintain context from previous messages in the conversation
- Be direct and to the point while remaining helpful

## Response Guidelines
- Use clear, professional language
- Include relevant details but avoid unnecessary verbosity
- If the question is unclear, ask for clarification
- For technical topics, assume the user has basic knowledge unless they indicate otherwise"""
        
        return enhanced_prompt
    
    def get_history_manager(self) -> HistoryManager:
        """Get the history manager instance."""
        return self._history_manager
    
    def clear_history(self) -> None:
        """Clear the current conversation history."""
        self._history_manager.clear_current_conversation()
    
    def _create_intent_chain(self) -> IntentChain:
        """Create and configure the intent chain with all available handlers."""
        from ..intents.weather import WeatherHandler
        from ..intents.public_ip import PublicIpHandler
        from ..intents.date_time import DateTimeHandler
        from ..intents.time_only import TimeHandler
        from ..intents.date_only import DateHandler
        from ..intents.list_files import ListFilesHandler
        
        handlers = [
            WeatherHandler(),
            PublicIpHandler(),
            DateTimeHandler(),
            TimeHandler(),
            DateHandler(),
            ListFilesHandler(),
        ]
        
        return IntentChain(handlers)
    
