"""
Conversation memory and context management for the Personal Assistant.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import json
import hashlib
from models import AssistantConfig


class ConversationMemory:
    """Manages conversation history and context for the assistant."""
    
    def __init__(self, config: AssistantConfig):
        self.config = config
        self._conversations: Dict[str, deque] = {}
        self._context_summaries: Dict[str, str] = {}
        self._last_cleanup = datetime.now()
        
    def get_session_id(self, user_context: str = "") -> str:
        """Generate a session ID based on user context."""
        if not user_context:
            user_context = "default"
        return hashlib.md5(user_context.encode()).hexdigest()[:16]
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to conversation history."""
        if not self.config.conversation_memory:
            return
            
        if session_id not in self._conversations:
            self._conversations[session_id] = deque(maxlen=self.config.max_context_messages * 2)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self._conversations[session_id].append(message)
        self._cleanup_old_data()
    
    def get_conversation_history(self, session_id: str, include_system: bool = True) -> List[Dict[str, str]]:
        """Get conversation history for a session."""
        if not self.config.conversation_memory or session_id not in self._conversations:
            return []
        
        messages = list(self._conversations[session_id])
        
        # Filter out system messages if requested
        if not include_system:
            messages = [msg for msg in messages if msg["role"] != "system"]
        
        # Limit to max context messages
        if len(messages) > self.config.max_context_messages:
            messages = messages[-self.config.max_context_messages:]
        
        # Convert to format expected by AI client
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    
    def get_context_summary(self, session_id: str) -> Optional[str]:
        """Get or generate a context summary for the session."""
        if not self.config.auto_summarize_context:
            return None
            
        if session_id in self._context_summaries:
            return self._context_summaries[session_id]
        
        # Generate summary if conversation is long enough
        if session_id in self._conversations and len(self._conversations[session_id]) > 10:
            summary = self._generate_summary(session_id)
            self._context_summaries[session_id] = summary
            return summary
        
        return None
    
    def _generate_summary(self, session_id: str) -> str:
        """Generate a summary of the conversation."""
        if session_id not in self._conversations:
            return ""
        
        messages = list(self._conversations[session_id])
        
        # Simple summary generation - take key points from user messages
        user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
        
        if len(user_messages) > 5:
            # Take first few and last few messages for context
            key_messages = user_messages[:3] + user_messages[-3:]
            return f"Previous conversation topics: {'; '.join(key_messages[:100] for msg in key_messages)}"
        
        return ""
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session."""
        if session_id in self._conversations:
            del self._conversations[session_id]
        if session_id in self._context_summaries:
            del self._context_summaries[session_id]
    
    def clear_all_sessions(self):
        """Clear all conversation history."""
        self._conversations.clear()
        self._context_summaries.clear()
    
    def _cleanup_old_data(self):
        """Clean up old conversation data based on retention policy."""
        now = datetime.now()
        
        # Only cleanup every hour to avoid performance impact
        if now - self._last_cleanup < timedelta(hours=1):
            return
        
        self._last_cleanup = now
        cutoff_time = now - timedelta(hours=self.config.data_retention_hours)
        
        # Remove old conversations
        sessions_to_remove = []
        for session_id, messages in self._conversations.items():
            # Remove old messages from the session
            while messages and datetime.fromisoformat(messages[0]["timestamp"]) < cutoff_time:
                messages.popleft()
            
            # If session is empty, mark for removal
            if not messages:
                sessions_to_remove.append(session_id)
        
        # Remove empty sessions
        for session_id in sessions_to_remove:
            self.clear_session(session_id)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        total_messages = sum(len(conv) for conv in self._conversations.values())
        active_sessions = len(self._conversations)
        
        return {
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "summaries_cached": len(self._context_summaries),
            "memory_enabled": self.config.conversation_memory,
            "max_context_messages": self.config.max_context_messages,
            "data_retention_hours": self.config.data_retention_hours
        }
    
    def anonymize_session_data(self, session_id: str):
        """Anonymize sensitive data in a session if privacy mode is enabled."""
        if not self.config.anonymize_data or session_id not in self._conversations:
            return
        
        # Simple anonymization - replace potential sensitive patterns
        sensitive_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # SSN
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]'),  # Credit card
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email
        ]
        
        import re
        for message in self._conversations[session_id]:
            content = message["content"]
            for pattern, replacement in sensitive_patterns:
                content = re.sub(pattern, replacement, content)
            message["content"] = content


# Global conversation memory instance
conversation_memory = None

def get_conversation_memory(config: AssistantConfig) -> ConversationMemory:
    """Get or create the global conversation memory instance."""
    global conversation_memory
    if conversation_memory is None:
        conversation_memory = ConversationMemory(config)
    return conversation_memory