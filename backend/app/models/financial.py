import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    type = Column(String(20), nullable=False)  # 'INCOME' or 'EXPENSE'
    icon = Column(String(50), nullable=True)   # icon identifier for UI
    color = Column(String(20), nullable=True)  # hex color for charts

    # Relationships
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False, index=True)
    
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    amount = Column(Float, nullable=False)  # Stored as standard float, calculations done with Decimal
    type = Column(String(20), nullable=False)  # 'INCOME' or 'EXPENSE'
    merchant = Column(String(255), nullable=False, index=True)
    payment_method = Column(String(50), nullable=False, default="UPI")  # 'UPI', 'CARD', 'NETBANKING', 'CASH'
    description = Column(String(500), nullable=True)
    
    is_recurring = Column(Boolean, default=False, nullable=False)
    is_synthetic = Column(Boolean, default=True, nullable=False)
    
    # Anomaly detection results
    anomaly_flag = Column(Boolean, default=False, nullable=False, index=True)
    anomaly_score = Column(Float, default=0.0, nullable=False)
    anomaly_reason = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    __table_args__ = (
        Index("idx_user_date_type", "user_id", "date", "type"),
        Index("idx_user_merchant", "user_id", "merchant"),
    )

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False, index=True)
    
    monthly_limit = Column(Float, nullable=False)
    month_year = Column(String(7), nullable=False, index=True)  # YYYY-MM
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

    __table_args__ = (
        Index("idx_user_category_month", "user_id", "category_id", "month_year", unique=True),
    )

class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(200), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0, nullable=False)
    target_date = Column(String(10), nullable=True)  # YYYY-MM-DD
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="savings_goals")
