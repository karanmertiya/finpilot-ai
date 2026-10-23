from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.financial import DashboardMetricsResponse
from backend.app.services.analytics_service import AnalyticsService
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/metrics", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Computes real-time dashboard analytics directly from the verified database records
    belonging exclusively to the authenticated user.
    """
    metrics = AnalyticsService.get_dashboard_metrics(db=db, user_id=current_user.id)
    return DashboardMetricsResponse(**metrics)
