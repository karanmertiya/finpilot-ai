import re
import sys
import os

sys.path.append(os.path.abspath("."))
from backend.app.db.session import SessionLocal
from backend.app.models.document import DocumentChunk
from backend.app.services.document_service import LocalEmbeddingEngine, cosine_similarity

db = SessionLocal()
chunk = db.query(DocumentChunk).first().content

def hybrid_score(q, doc):
    stopwords = {'what', 'does', 'about', 'uploaded', 'document', 'documents', 'mentioned', 'specified', 'letter', 'search', 'financial'}
    q_words = set(w for w in re.findall(r'\b\w+\b', q.lower()) if len(w) > 3 and w not in stopwords)
    d_words = set(re.findall(r'\b\w+\b', doc.lower()))
    lex = len(q_words & d_words) / max(1, len(q_words)) if q_words else 0.0
    v1 = LocalEmbeddingEngine.get_embedding(q)
    v2 = LocalEmbeddingEngine.get_embedding(doc)
    cos = cosine_similarity(v1, v2)
    return round(0.5 * cos + 0.5 * lex, 4)

print('Property insurance:', hybrid_score('Search my financial documents for property insurance requirements', chunk))
print('Abstention:', hybrid_score('What does my uploaded document say about life insurance payout for space travel?', chunk))
