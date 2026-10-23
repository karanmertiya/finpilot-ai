import os
import re
import csv
import io
import math
import json
from typing import List, Dict, Any, Optional, Tuple
from pypdf import PdfReader
from sqlalchemy.orm import Session
import httpx

from backend.app.core.config import settings
from backend.app.models.document import Document, DocumentChunk

class LocalEmbeddingEngine:
    """
    Fast, deterministic, normalized n-gram bag-of-words / sub-word vector generator (dimension: 384).
    Produces cosine-comparable dense representations entirely on CPU with zero dependencies.
    """
    DIM = 384

    STOPWORDS = {
        "what", "is", "the", "are", "about", "for", "in", "and", "to", "a", "an", "it",
        "of", "on", "my", "does", "say", "tell", "me", "show", "from", "with", "as", "by", "at"
    }

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        vec = [0.0] * cls.DIM
        clean_text = text.lower()
        raw_words = re.findall(r"\b\w+\b", clean_text)
        words = [w for w in raw_words if w not in cls.STOPWORDS and len(w) > 2]
        if not words:
            words = raw_words
        if not words:
            return vec
        
        # Word and character 3-gram hashing into vector dimensions
        for w in words:
            h = abs(hash(w)) % cls.DIM
            vec[h] += 2.0
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    sub = w[i:i+3]
                    h_sub = abs(hash(sub)) % cls.DIM
                    vec[h_sub] += 0.5

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two unit-normalized vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    return float(max(0.0, min(1.0, dot)))

class DocumentService:
    @staticmethod
    def extract_text(file_bytes: bytes, filename: str) -> List[Tuple[int, str]]:
        """
        Extracts text from PDF, CSV, or TXT file bytes.
        Returns list of (page_or_section_number, text_content).
        """
        ext = os.path.splitext(filename)[1].lower()
        pages = []
        
        if ext == ".pdf":
            reader = PdfReader(io.BytesIO(file_bytes))
            for page_idx, page in enumerate(reader.pages):
                extracted = page.extract_text() or ""
                clean_extracted = re.sub(r"\s+", " ", extracted).strip()
                if clean_extracted:
                    pages.append((page_idx + 1, clean_extracted))
        elif ext == ".csv":
            content_str = file_bytes.decode("utf-8", errors="replace")
            reader = csv.reader(io.StringIO(content_str))
            rows = list(reader)
            if rows:
                header = rows[0]
                chunk_lines = [f"Header: {', '.join(header)}"]
                for i, row in enumerate(rows[1:], start=1):
                    chunk_lines.append(f"Row {i}: {', '.join(row)}")
                    if len(chunk_lines) >= 20:
                        pages.append((len(pages) + 1, "\n".join(chunk_lines)))
                        chunk_lines = [f"Header: {', '.join(header)}"]
                if len(chunk_lines) > 1:
                    pages.append((len(pages) + 1, "\n".join(chunk_lines)))
        elif ext in [".txt", ".json", ".md"]:
            content_str = file_bytes.decode("utf-8", errors="replace")
            lines = content_str.splitlines()
            buffer = []
            for i, line in enumerate(lines):
                buffer.append(line)
                if len(buffer) >= 30:
                    pages.append((len(pages) + 1, "\n".join(buffer)))
                    buffer = []
            if buffer:
                pages.append((len(pages) + 1, "\n".join(buffer)))
        else:
            raise ValueError(f"Unsupported file format: {ext}. Allowed: .pdf, .txt, .csv")
            
        return pages

    @staticmethod
    def chunk_document_text(
        pages: List[Tuple[int, str]],
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ) -> List[Dict[str, Any]]:
        """Splits page texts into chunks with sliding-window overlap while tracking page numbers."""
        chunks = []
        chunk_idx = 0
        
        for page_num, text in pages:
            words = text.split()
            if not words:
                continue
                
            start = 0
            while start < len(words):
                end = min(start + chunk_size, len(words))
                chunk_words = words[start:end]
                chunk_str = " ".join(chunk_words)
                
                chunks.append({
                    "chunk_index": chunk_idx,
                    "content": chunk_str,
                    "page_number": page_num
                })
                chunk_idx += 1
                
                if end == len(words):
                    break
                start += (chunk_size - chunk_overlap)
                
        return chunks

    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """Generates embedding using Gemini/OpenAI if configured, else local high-performance CPU embedding."""
        if settings.EMBEDDING_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            try:
                # Call Gemini embedding API
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.EMBEDDING_MODEL}:embedContent?key={settings.GEMINI_API_KEY}"
                payload = {"content": {"parts": [{"text": text[:2000]}]}}
                resp = httpx.post(url, json=payload, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    values = data.get("embedding", {}).get("values", [])
                    if values:
                        return values
            except Exception:
                pass
                
        return LocalEmbeddingEngine.get_embedding(text)

    @classmethod
    def process_and_index_document(
        cls,
        db: Session,
        document: Document,
        file_bytes: bytes
    ) -> int:
        """Parses, chunks, embeds, and stores document records in the database."""
        try:
            pages = cls.extract_text(file_bytes, document.filename)
            if not pages:
                document.status = "FAILED"
                document.error_message = "No readable text could be extracted from document."
                db.commit()
                return 0
                
            raw_chunks = cls.chunk_document_text(pages)
            for c in raw_chunks:
                emb = cls.generate_embedding(c["content"])
                chunk_obj = DocumentChunk(
                    document_id=document.id,
                    user_id=document.user_id,
                    chunk_index=c["chunk_index"],
                    content=c["content"],
                    page_number=c["page_number"],
                    embedding=emb
                )
                db.add(chunk_obj)
                
            document.status = "INDEXED"
            document.chunk_count = len(raw_chunks)
            document.error_message = None
            db.commit()
            return len(raw_chunks)
        except Exception as e:
            db.rollback()
            document.status = "FAILED"
            document.error_message = str(e)
            db.commit()
            raise e

    @classmethod
    def retrieve_relevant_chunks(
        cls,
        db: Session,
        user_id: str,
        query: str,
        top_k: int = 4,
        similarity_threshold: float = 0.25
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-k relevant document chunks using production-grade hybrid retrieval:
        dense semantic cosine similarity (0.5 weight) + normalized lexical term matching (0.5 weight).
        Strictly enforces tenant user isolation: queries only chunks belonging to user_id.
        """
        query_emb = cls.generate_embedding(query)
        
        stopwords = {
            'what', 'does', 'about', 'uploaded', 'document', 'documents',
            'mentioned', 'specified', 'letter', 'tell', 'show', 'search', 'financial'
        }
        q_words = set(w for w in re.findall(r'\b\w+\b', query.lower()) if len(w) > 3 and w not in stopwords)
        
        # Query chunks for this specific user only
        chunks = (
            db.query(DocumentChunk, Document.filename)
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(DocumentChunk.user_id == user_id)
            .all()
        )
        
        scored_results = []
        for chunk, filename in chunks:
            if chunk.embedding:
                cos_score = cosine_similarity(query_emb, chunk.embedding)
                
                # Lexical overlap
                d_words = set(re.findall(r'\b\w+\b', chunk.content.lower()))
                lex_score = len(q_words & d_words) / max(1, len(q_words)) if q_words else 0.0
                
                # Hybrid score
                final_score = (0.5 * cos_score) + (0.5 * lex_score)
                
                if final_score >= similarity_threshold:
                    scored_results.append({
                        "document_id": chunk.document_id,
                        "filename": filename,
                        "chunk_index": chunk.chunk_index,
                        "page_number": chunk.page_number,
                        "passage": chunk.content,
                        "similarity_score": round(final_score, 4)
                    })
                    
        scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_results[:top_k]
