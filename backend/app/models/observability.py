import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action = Column(String(100), nullable=False, index=True)      # e.g., AUTH_LOGIN, TRANSACTION_CREATE, RAG_QUERY, TOOL_INVOKE
    resource_type = Column(String(50), nullable=False)            # e.g., TRANSACTION, DOCUMENT, CHAT
    resource_id = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="SUCCESS") # SUCCESS, DENIED, ERROR
    
    # Sanitized metadata without secrets
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_events")

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    run_name = Column(String(150), nullable=False)
    total_tests = Column(Integer, nullable=False)
    passed_tests = Column(Integer, nullable=False)
    failed_tests = Column(Integer, nullable=False)
    pass_rate = Column(Float, nullable=False)
    
    avg_latency_ms = Column(Float, nullable=False)
    metrics = Column(JSON, nullable=False)  # Breakdown by category: Recall@k, Faithfulness, Accuracy, etc.
    details = Column(JSON, nullable=True)  # Individual test case outcomes
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

class OperationalMetric(Base):
    __tablename__ = "operational_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    endpoint = Column(String(150), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    token_count = Column(Integer, default=0, nullable=False)
    cost_estimate_usd = Column(Float, default=0.0, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
