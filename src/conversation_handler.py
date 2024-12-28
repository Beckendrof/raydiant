"""Conversation handler for AI Teaching Assistant"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class ConversationHandler:
    """Handles conversations between students and the AI TA"""
    
    def __init__(self, max_context_length: int = 10):
        """Initialize conversation handler
        
        Args:
            max_context_length: Maximum number of messages to keep in context
        """
        self.max_context_length = max_context_length
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
    
    def start_conversation(self, user_id: str) -> str:
        """Start a new conversation for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Conversation ID
        """
        conversation_id = f"{user_id}_{datetime.now().timestamp()}"
        self.conversations[conversation_id] = []
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Add a message to the conversation
        
        Args:
            conversation_id: ID of the conversation
            role: Role of the message sender (user/assistant)
            content: Message content
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversations[conversation_id].append(message)
        
        # Trim context if needed
        if len(self.conversations[conversation_id]) > self.max_context_length:
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_context_length:]
    
    def get_context(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation context for AI processing
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of messages for context
        """
        if conversation_id not in self.conversations:
            return []
        
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversations[conversation_id]
        ] 