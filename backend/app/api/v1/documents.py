import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.document import Document, DocumentChunk
from backend.app.schemas.document import (
    DocumentResponse,
    DocumentChunkResponse,
    DocumentUploadResponse
)
from backend.app.services.document_service import DocumentService
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/documents", tags=["Financial Document Center"])

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all financial documents uploaded by the current user."""
    docs = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return [DocumentResponse.model_validate(d) for d in docs]

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads, validates, chunks, embeds, and indexes a financial document (PDF, TXT, CSV).
    Enforces file extension whitelist and 10MB file size limit.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    file_bytes = file.file.read()
    max_bytes = settings.MAX_UPLOAD_FILE_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_FILE_SIZE_MB}MB."
        )

    # Create document record
    doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_type=ext.replace(".", ""),
        file_size_bytes=len(file_bytes),
        status="PROCESSING"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        chunks_count = DocumentService.process_and_index_document(
            db=db,
            document=doc,
            file_bytes=file_bytes
        )
        AuditService.log_event(
            db=db,
            action="DOCUMENT_UPLOAD",
            resource_type="DOCUMENT",
            user_id=current_user.id,
            resource_id=doc.id,
            details={"filename": doc.filename, "size": len(file_bytes), "chunks": chunks_count}
        )
        return DocumentUploadResponse(
            id=doc.id,
            filename=doc.filename,
            status="INDEXED",
            message=f"Document successfully processed and indexed into {chunks_count} searchable chunks.",
            chunks_indexed=chunks_count
        )
    except Exception as e:
        AuditService.log_event(
            db=db,
            action="DOCUMENT_INDEX_FAILED",
            resource_type="DOCUMENT",
            user_id=current_user.id,
            resource_id=doc.id,
            status="ERROR",
            details={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves document metadata and its indexed text passages."""
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == doc.id)
        .order_by(DocumentChunk.chunk_index.asc())
        .limit(20)
        .all()
    )

    resp = DocumentResponse.model_validate(doc)
    resp.chunks = [DocumentChunkResponse.model_validate(c) for c in chunks]
    return resp

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes document and cascades cleanup of all associated chunks and embeddings."""
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    db.delete(doc)
    db.commit()

    AuditService.log_event(
        db=db,
        action="DOCUMENT_DELETE",
        resource_type="DOCUMENT",
        user_id=current_user.id,
        resource_id=document_id,
        details={"filename": doc.filename}
    )
    return None
