"""Assistant service for handling user interactions."""

from typing import List, Dict, Any, Optional
from ..config.params import AiParameters
from ..llm.interfaces import LLMClient
from .history import HistoryManager


class AssistantService:
    def __init__(self, params: AiParameters, client: LLMClient, history_manager: Optional[HistoryManager] = None) -> None:
        self._p = params
        self._client = client
        self._history_manager = history_manager or HistoryManager()

    async def answer(self, user_prompt: str, use_history: bool = True) -> str:
        if not user_prompt.strip():
            return "Please enter a non-empty request."
        
        system = self._p.system_prompt or f"You are {self._p.agent}, a helpful assistant."
        
        # Add user message to history
        self._history_manager.add_message("user", user_prompt)
        
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
    
    def get_history_manager(self) -> HistoryManager:
        """Get the history manager instance."""
        return self._history_manager
    
    def clear_history(self) -> None:
        """Clear the current conversation history."""
        self._history_manager.clear_current_conversation()
    
    def save_conversation(self) -> None:
        """Save the current conversation."""
        self._history_manager.save_conversation()
