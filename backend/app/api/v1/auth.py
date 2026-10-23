from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user account."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_demo_user=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    AuditService.log_event(
        db=db,
        action="USER_REGISTER",
        resource_type="USER",
        user_id=user.id,
        details={"email": user.email}
    )

    token = create_access_token(user.id)
    return Token(access_token=token, user=UserResponse.model_validate(user))

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user credentials and returns JWT bearer token."""
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        AuditService.log_event(
            db=db,
            action="LOGIN_FAILED",
            resource_type="USER",
            status="DENIED",
            details={"email": login_in.email}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    AuditService.log_event(
        db=db,
        action="LOGIN_SUCCESS",
        resource_type="USER",
        user_id=user.id,
        details={"email": user.email}
    )

    token = create_access_token(user.id)
    return Token(access_token=token, user=UserResponse.model_validate(user))

@router.post("/demo-login", response_model=Token)
def demo_login(db: Session = Depends(get_db)):
    """Instant 1-click authentication into the seeded Indian Fintech Demo profile."""
    demo_user = db.query(User).filter(User.email == "demo@finpilot.ai").first()
    if not demo_user:
        # Create on the fly if not seeded yet
        demo_user = User(
            email="demo@finpilot.ai",
            full_name="Aarav Sharma",
            hashed_password=get_password_hash("DemoFinPilot2026!"),
            is_demo_user=True
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

    token = create_access_token(demo_user.id)
    return Token(access_token=token, user=UserResponse.model_validate(demo_user))

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieves profile of the authenticated user."""
    return UserResponse.model_validate(current_user)
