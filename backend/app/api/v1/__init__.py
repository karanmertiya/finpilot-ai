from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.transactions import router as transactions_router
from backend.app.api.v1.budgets import router as budgets_router
from backend.app.api.v1.chat import router as chat_router
from backend.app.api.v1.documents import router as documents_router
from backend.app.api.v1.calculations import router as calculations_router
from backend.app.api.v1.system import router as system_router
from backend.app.api.v1.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(transactions_router)
api_router.include_router(budgets_router)
api_router.include_router(chat_router)
api_router.include_router(documents_router)
api_router.include_router(calculations_router)
api_router.include_router(system_router)

__all__ = ["api_router"]
