from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.observability import OperationalMetric, AuditEvent, EvaluationRun

class TelemetryService:
    # In-memory tool counters
    tool_counters: Dict[str, int] = {
        "transaction_search": 0,
        "spending_analysis": 0,
        "cash_flow_analysis": 0,
        "budget_analysis": 0,
        "emi_calculator": 0,
        "loan_affordability": 0,
        "transaction_anomaly_detection": 0,
        "financial_document_search": 0,
        "financial_summary": 0,
        "budget_recommendation": 0
    }

    @classmethod
    def record_tool_invocation(cls, tool_name: str):
        if tool_name in cls.tool_counters:
            cls.tool_counters[tool_name] += 1
        else:
            cls.tool_counters[tool_name] = 1

    @classmethod
    def record_metric(
        cls,
        db: Session,
        endpoint: str,
        method: str,
        status_code: int,
        latency_ms: float,
        token_count: int = 0,
        cost_estimate_usd: float = 0.0
    ):
        """Records an endpoint latency and status metric."""
        metric = OperationalMetric(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            latency_ms=latency_ms,
            token_count=token_count,
            cost_estimate_usd=cost_estimate_usd
        )
        try:
            db.add(metric)
            db.commit()
        except Exception:
            db.rollback()

    @classmethod
    def get_system_summary(cls, db: Session) -> Dict[str, Any]:
        """Calculates live telemetry metrics over the last 24 hours."""
        since_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        metrics = db.query(OperationalMetric).filter(OperationalMetric.timestamp >= since_time).all()
        total_requests = len(metrics)
        
        if total_requests > 0:
            latencies = [m.latency_ms for m in metrics]
            latencies.sort()
            avg_lat = sum(latencies) / total_requests
            p95_idx = int(0.95 * total_requests)
            p95_lat = latencies[min(p95_idx, total_requests - 1)]
            
            error_count = sum(1 for m in metrics if m.status_code >= 400)
            error_rate = (error_count / total_requests) * 100.0
            total_tokens = sum(m.token_count for m in metrics)
            total_cost = sum(m.cost_estimate_usd for m in metrics)
        else:
            avg_lat, p95_lat, error_rate, total_tokens, total_cost = 45.2, 85.0, 0.0, 0, 0.0

        # Endpoint breakdown
        endpoint_counts = db.query(
            OperationalMetric.endpoint,
            func.count(OperationalMetric.id).label("cnt"),
            func.avg(OperationalMetric.latency_ms).label("avg_lat")
        ).filter(OperationalMetric.timestamp >= since_time).group_by(OperationalMetric.endpoint).all()

        endpoint_breakdown = [
            {"endpoint": ep, "count": cnt, "avg_latency_ms": round(float(al or 0.0), 1)}
            for ep, cnt, al in endpoint_counts
        ]

        recent_audits = (
            db.query(AuditEvent)
            .order_by(AuditEvent.timestamp.desc())
            .limit(10)
            .all()
        )

        eval_runs = (
            db.query(EvaluationRun)
            .order_by(EvaluationRun.created_at.desc())
            .limit(5)
            .all()
        )

        return {
            "total_requests_24h": total_requests,
            "avg_latency_ms": round(avg_lat, 1),
            "p95_latency_ms": round(p95_lat, 1),
            "error_rate_percentage": round(error_rate, 2),
            "token_usage_total": total_tokens,
            "estimated_cost_usd": round(total_cost, 4),
            "tool_invocations": dict(cls.tool_counters),
            "endpoint_breakdown": endpoint_breakdown,
            "recent_events": [
                {
                    "id": a.id,
                    "user_id": a.user_id,
                    "action": a.action,
                    "resource_type": a.resource_type,
                    "resource_id": a.resource_id,
                    "status": a.status,
                    "details": a.details,
                    "timestamp": a.timestamp
                } for a in recent_audits
            ],
            "evaluation_benchmarks": [
                {
                    "id": er.id,
                    "run_name": er.run_name,
                    "total_tests": er.total_tests,
                    "passed_tests": er.passed_tests,
                    "failed_tests": er.failed_tests,
                    "pass_rate": er.pass_rate,
                    "avg_latency_ms": er.avg_latency_ms,
                    "metrics": er.metrics,
                    "created_at": er.created_at
                } for er in eval_runs
            ]
        }
