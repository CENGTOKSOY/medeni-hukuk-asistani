from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    content: str
    role: MessageRole
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatSession(BaseModel):
    user_id: str
    session_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: List[Message] = []
    title: Optional[str] = None
    is_active: bool = True

    def add_message(self, message: Message):
        self.messages.append(message)
        self.updated_at = datetime.now()