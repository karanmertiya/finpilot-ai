from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.financial import Transaction
from backend.app.schemas.financial import (
    EMICalculatorRequest,
    EMICalculatorResponse,
    LoanAffordabilityRequest,
    LoanAffordabilityResponse
)
from backend.app.services.financial_math import FinancialMathService
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/calculations", tags=["Financial Calculators"])

@router.post("/emi", response_model=EMICalculatorResponse)
def calculate_emi(calc_in: EMICalculatorRequest):
    """
    Computes exact monthly instalment (EMI) using the standard reducing balance formula.
    Includes amortization preview and interest-to-principal cost ratio.
    """
    result = FinancialMathService.calculate_emi(
        principal=calc_in.principal,
        annual_interest_rate=calc_in.annual_interest_rate,
        tenure_months=calc_in.tenure_months
    )
    return EMICalculatorResponse(**result)

@router.post("/affordability", response_model=LoanAffordabilityResponse)
def estimate_loan_affordability(
    req: LoanAffordabilityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates loan affordability by calculating Debt-To-Income (DTI) and post-loan surplus
    using the authenticated user's actual 3-month income and expenditure averages.
    """
    txs = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    
    unique_months = len(set(t.date[:7] for t in txs)) or 1
    total_inc = sum(t.amount for t in txs if t.type == "INCOME")
    total_exp = sum(t.amount for t in txs if t.type == "EXPENSE")
    
    avg_monthly_income = total_inc / unique_months
    avg_monthly_expenses = total_exp / unique_months

    result = FinancialMathService.calculate_affordability(
        monthly_income=avg_monthly_income,
        monthly_expenses=avg_monthly_expenses,
        proposed_emi=req.proposed_emi,
        existing_emis=req.existing_emis
    )
    return LoanAffordabilityResponse(**result)
