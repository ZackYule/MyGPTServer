# pandora_models.py
from typing import List, Optional
from pydantic import BaseModel


# Pydantic 模型
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]


class ChatMessage(BaseModel):
    role: str
    content: str


class Choice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    system_fingerprint: Optional[str] = None
    choices: List[Choice]
    usage: Usage
