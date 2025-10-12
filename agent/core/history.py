"""Conversation history management."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Message:
    """Represents a single message in the conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str


@dataclass
class Conversation:
    """Represents a conversation session."""
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str


class HistoryManager:
    """Manages conversation history in memory."""
    
    def __init__(self):
        self.current_conversation: Optional[Conversation] = None
    
    def start_new_conversation(self, title: Optional[str] = None) -> Conversation:
        """Start a new conversation session."""
        conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not title:
            title = f"Conversation {conversation_id}"
        
        self.current_conversation = Conversation(
            id=conversation_id,
            title=title,
            messages=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        return self.current_conversation
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the current conversation."""
        if not self.current_conversation:
            self.start_new_conversation()
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        self.current_conversation.messages.append(message)
        self.current_conversation.updated_at = datetime.now().isoformat()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation as a list of message dictionaries."""
        if not self.current_conversation:
            return []
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.current_conversation.messages
        ]
    
    
    def clear_current_conversation(self) -> None:
        """Clear the current conversation."""
        if self.current_conversation:
            self.current_conversation.messages.clear()
            self.current_conversation.updated_at = datetime.now().isoformat()
