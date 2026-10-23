from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.observability import SystemMetricsResponse, EvaluationRunResponse
from backend.app.services.telemetry_service import TelemetryService
from backend.app.models.observability import EvaluationRun
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/system", tags=["System & Evaluation Dashboard"])

@router.get("/metrics", response_model=SystemMetricsResponse)
def get_system_metrics(db: Session = Depends(get_db)):
    """
    Returns live operational metrics:
    request volume, latency percentiles, error rate, token costs, and sanitized security audit events.
    """
    metrics = TelemetryService.get_system_summary(db=db)
    return SystemMetricsResponse(**metrics)

@router.post("/run-evaluation", response_model=EvaluationRunResponse)
def trigger_evaluation_suite(db: Session = Depends(get_db)):
    """
    Executes automated RAG & analytics benchmark tests, records precision/recall/accuracy,
    and returns verified metrics.
    """
    from backend.app.ai.evaluation.runner import run_evaluation_suite
    result = run_evaluation_suite(db)
    return EvaluationRunResponse.model_validate(result)
