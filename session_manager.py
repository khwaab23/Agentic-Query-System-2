"""
Session manager for maintaining conversation history in the Agentic Query System.
Handles chat sessions with memory for follow-up questions.
"""
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Represents a single message in the chat."""
    role: str  # "user", "assistant", "tool"
    content: str
    timestamp: datetime
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ChatSession(BaseModel):
    """Represents a chat session with history."""
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    last_updated: datetime


class SessionManager:
    """Manages chat sessions and conversation history."""
    
    def __init__(self, session_timeout_hours: int = 24):
        self.sessions: Dict[str, ChatSession] = {}
        self.session_timeout = timedelta(hours=session_timeout_hours)
    
    def create_session(self) -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = ChatSession(
            session_id=session_id,
            messages=[],
            created_at=now,
            last_updated=now
        )
        
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session has expired
        if datetime.now() - session.last_updated > self.session_timeout:
            del self.sessions[session_id]
            return None
        
        return session
    
    def add_message(self, session_id: str, role: str, content: str, 
                   tool_calls: Optional[List[Dict[str, Any]]] = None,
                   tool_call_id: Optional[str] = None) -> bool:
        """Add a message to a session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            tool_calls=tool_calls,
            tool_call_id=tool_call_id
        )
        
        session.messages.append(message)
        session.last_updated = datetime.now()
        return True
    
    def get_conversation_history(self, session_id: str, include_system: bool = True) -> List[Dict[str, Any]]:
        """Get conversation history formatted for OpenAI API."""
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = []
        
        # Add system message if requested
        if include_system:
            from openai_tools import SYSTEM_PROMPT
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
        
        # Convert chat messages to OpenAI format
        for msg in session.messages:
            if msg.role == "tool":
                messages.append({
                    "role": "tool",
                    "content": msg.content,
                    "tool_call_id": msg.tool_call_id
                })
            elif msg.role == "assistant" and msg.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": msg.tool_calls
                })
            else:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        return messages
    
    def clear_session(self, session_id: str) -> bool:
        """Clear all messages from a session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.messages = []
        session.last_updated = datetime.now()
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session completely."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if now - session.last_updated > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def get_session_count(self) -> int:
        """Get the number of active sessions."""
        self.cleanup_expired_sessions()
        return len(self.sessions)


# Global session manager instance
session_manager = SessionManager()
