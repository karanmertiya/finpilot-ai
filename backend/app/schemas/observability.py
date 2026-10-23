from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class AuditEventResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    status: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class EvaluationRunResponse(BaseModel):
    id: str
    run_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float
    avg_latency_ms: float
    metrics: Dict[str, Any]
    details: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SystemMetricsResponse(BaseModel):
    total_requests_24h: int
    avg_latency_ms: float
    p95_latency_ms: float
    error_rate_percentage: float
    token_usage_total: int
    estimated_cost_usd: float
    tool_invocations: Dict[str, int]
    endpoint_breakdown: List[Dict[str, Any]]
    recent_events: List[AuditEventResponse]
    evaluation_benchmarks: Optional[List[EvaluationRunResponse]] = None
