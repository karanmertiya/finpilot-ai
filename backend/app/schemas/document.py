from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class DocumentChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str
    page_number: Optional[int] = None

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    created_at: datetime
    updated_at: datetime
    chunks: Optional[List[DocumentChunkResponse]] = None

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    status: str
    message: str
    chunks_indexed: int
