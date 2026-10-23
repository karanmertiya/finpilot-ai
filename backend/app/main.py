import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.db.session import engine, Base, SessionLocal
from backend.app.api.v1 import api_router
from backend.app.services.telemetry_service import TelemetryService
from backend.app.models.financial import Category

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-Grade Fintech AI Copilot | Personal Financial Intelligence System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telemetry & Latency Middleware
@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    # Record telemetry for API routes (exclude static docs)
    path = request.url.path
    if path.startswith("/api/"):
        db = SessionLocal()
        try:
            TelemetryService.record_metric(
                db=db,
                endpoint=path,
                method=request.method,
                status_code=response.status_code,
                latency_ms=round(duration_ms, 2)
            )
        except Exception:
            pass
        finally:
            db.close()

    return response

# Include Versioned API Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    """Initializes tables and ensures default standard categories exist."""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        count = db.query(Category).count()
        if count == 0:
            defaults = [
                Category(name="Salary", type="INCOME", icon="Briefcase", color="#10b981"),
                Category(name="Investments", type="INCOME", icon="TrendingUp", color="#059669"),
                Category(name="Housing & Rent", type="EXPENSE", icon="Home", color="#6366f1"),
                Category(name="Groceries", type="EXPENSE", icon="ShoppingCart", color="#3b82f6"),
                Category(name="Food & Dining", type="EXPENSE", icon="Utensils", color="#f59e0b"),
                Category(name="Transportation", type="EXPENSE", icon="Car", color="#8b5cf6"),
                Category(name="Utilities", type="EXPENSE", icon="Zap", color="#06b6d4"),
                Category(name="Shopping", type="EXPENSE", icon="ShoppingBag", color="#ec4899"),
                Category(name="Healthcare", type="EXPENSE", icon="HeartPulse", color="#ef4444"),
                Category(name="Entertainment", type="EXPENSE", icon="Film", color="#d946ef"),
                Category(name="General", type="EXPENSE", icon="CreditCard", color="#64748b")
            ]
            db.add_all(defaults)
            db.commit()
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "api_docs": "/docs",
        "health_check": f"{settings.API_V1_STR}/health"
    }
