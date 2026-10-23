from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ToolCallRecord(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]
    status: str = "success"
    execution_time_ms: float = 0.0

class CitationRecord(BaseModel):
    document_id: str
    filename: str
    page_number: Optional[int] = None
    passage: str
    similarity_score: float

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    citations: Optional[List[Dict[str, Any]]] = None
    chart_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageResponse]] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    sender: str = "assistant"
    content: str
    intent: str
    tool_calls: List[ToolCallRecord] = []
    citations: List[CitationRecord] = []
    chart_data: Optional[Dict[str, Any]] = None
    latency_ms: float
