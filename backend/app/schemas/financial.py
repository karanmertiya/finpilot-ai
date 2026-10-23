from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CategoryResponse(BaseModel):
    id: str
    name: str
    type: str
    icon: Optional[str] = None
    color: Optional[str] = None

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    category_id: str
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD")
    amount: float = Field(..., gt=0, description="Transaction amount in INR")
    type: str = Field(..., pattern=r"^(INCOME|EXPENSE)$")
    merchant: str = Field(..., min_length=1, max_length=255)
    payment_method: str = Field(default="UPI", max_length=50)
    description: Optional[str] = None
    is_recurring: bool = False

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    category_id: str
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    date: str
    amount: float
    type: str
    merchant: str
    payment_method: str
    description: Optional[str] = None
    is_recurring: bool
    is_synthetic: bool
    anomaly_flag: bool
    anomaly_score: float
    anomaly_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total_count: int
    page: int
    page_size: int
    total_income: float
    total_expense: float

class BudgetCreate(BaseModel):
    category_id: str
    monthly_limit: float = Field(..., gt=0)
    month_year: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Month in YYYY-MM")

class BudgetResponse(BaseModel):
    id: str
    user_id: str
    category_id: str
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    monthly_limit: float
    month_year: str
    created_at: datetime

    class Config:
        from_attributes = True

class BudgetVsActual(BaseModel):
    category_id: str
    category_name: str
    category_color: Optional[str] = None
    budget_limit: float
    actual_spent: float
    remaining: float
    percentage_used: float
    is_over_budget: bool

class SavingsGoalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0.0, ge=0)
    target_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")

class SavingsGoalResponse(BaseModel):
    id: str
    user_id: str
    title: str
    target_amount: float
    current_amount: float
    target_date: Optional[str] = None
    progress_percentage: float
    created_at: datetime

    class Config:
        from_attributes = True

class EMICalculatorRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Principal loan amount in INR")
    annual_interest_rate: float = Field(..., ge=0, description="Annual interest rate in % (e.g. 8.5 for 8.5%)")
    tenure_months: int = Field(..., gt=0, le=480, description="Tenure in months (e.g. 240 for 20 years)")

class AmortizationScheduleItem(BaseModel):
    month: int
    emi: float
    principal_paid: float
    interest_paid: float
    remaining_balance: float

class EMICalculatorResponse(BaseModel):
    monthly_emi: float
    total_principal: float
    total_interest: float
    total_payment: float
    interest_to_principal_ratio: float
    effective_rate_type: str = "Nominal reducing balance"
    schedule_preview: List[AmortizationScheduleItem] = []

class LoanAffordabilityRequest(BaseModel):
    proposed_emi: float = Field(..., gt=0, description="Proposed monthly loan EMI in INR")
    existing_emis: float = Field(default=0.0, ge=0, description="Current monthly EMI obligations")

class LoanAffordabilityResponse(BaseModel):
    monthly_income: float
    current_fixed_expenses: float
    current_disposable_income: float
    proposed_emi: float
    total_obligations_post_loan: float
    debt_to_income_ratio: float  # Percentage
    remaining_disposable_cash_flow: float
    affordability_verdict: str  # AFFORDABLE, TIGHT, HIGH_RISK, UNAFFORDABLE
    analysis_text: str
    assumptions_and_limitations: List[str]

class AnomalyItem(BaseModel):
    transaction_id: str
    date: str
    merchant: str
    category: str
    amount: float
    anomaly_score: float
    severity: str  # LOW, MEDIUM, HIGH
    reason: str
    historical_benchmark: str
    caveat: str

class DashboardMetricsResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_cash_flow: float
    savings_rate: float
    currency: str = "INR"
    is_synthetic: bool = True
    spending_by_category: List[Dict[str, Any]]
    monthly_trend: List[Dict[str, Any]]
    recent_transactions: List[TransactionResponse]
    budget_utilization: List[BudgetVsActual]
    unusual_alerts: List[AnomalyItem]
    ai_financial_summary: str
