"""Conversation history management."""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


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
    """Manages conversation history storage and retrieval."""
    
    def __init__(self, history_dir: str = ".history"):
        self.history_dir = history_dir
        self.current_conversation: Optional[Conversation] = None
        self._ensure_history_dir()
    
    def _ensure_history_dir(self) -> None:
        """Ensure the history directory exists."""
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
    
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
    
    def save_conversation(self) -> None:
        """Save the current conversation to disk."""
        if not self.current_conversation:
            return
        
        filename = os.path.join(self.history_dir, f"{self.current_conversation.id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.current_conversation), f, indent=2, ensure_ascii=False)
    
    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Load a conversation from disk."""
        filename = os.path.join(self.history_dir, f"{conversation_id}.json")
        if not os.path.exists(filename):
            return None
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert message dictionaries back to Message objects
            messages = [Message(**msg) for msg in data['messages']]
            conversation = Conversation(
                id=data['id'],
                title=data['title'],
                messages=messages,
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            return conversation
        except (json.JSONDecodeError, KeyError, TypeError):
            return None
    
    def list_conversations(self) -> List[Dict[str, str]]:
        """List all saved conversations."""
        conversations = []
        if not os.path.exists(self.history_dir):
            return conversations
        
        for filename in os.listdir(self.history_dir):
            if filename.endswith('.json'):
                conversation_id = filename[:-5]  # Remove .json extension
                conversation = self.load_conversation(conversation_id)
                if conversation:
                    conversations.append({
                        'id': conversation.id,
                        'title': conversation.title,
                        'created_at': conversation.created_at,
                        'updated_at': conversation.updated_at,
                        'message_count': len(conversation.messages)
                    })
        
        # Sort by updated_at, most recent first
        conversations.sort(key=lambda x: x['updated_at'], reverse=True)
        return conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation from disk."""
        filename = os.path.join(self.history_dir, f"{conversation_id}.json")
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False
    
    def clear_current_conversation(self) -> None:
        """Clear the current conversation."""
        if self.current_conversation:
            self.current_conversation.messages.clear()
            self.current_conversation.updated_at = datetime.now().isoformat()
