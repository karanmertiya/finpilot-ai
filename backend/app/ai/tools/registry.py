from typing import Dict, Any, List, Optional, Callable
import time
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from backend.app.models.financial import Transaction, Category, Budget, SavingsGoal
from backend.app.services.financial_math import FinancialMathService
from backend.app.services.anomaly_detector import TransactionAnomalyDetector
from backend.app.services.document_service import DocumentService
from backend.app.services.telemetry_service import TelemetryService

# Tool Input Schemas
class TransactionSearchInput(BaseModel):
    query: Optional[str] = Field(None, description="Keyword for merchant or description")
    category: Optional[str] = Field(None, description="Filter by category name")
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD")
    min_amount: Optional[float] = Field(None, ge=0, description="Minimum transaction amount")
    max_amount: Optional[float] = Field(None, ge=0, description="Maximum transaction amount")
    limit: int = Field(default=10, ge=1, le=50)

class SpendingAnalysisInput(BaseModel):
    start_date: Optional[str] = Field(None, description="Start date YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="End date YYYY-MM-DD")
    category: Optional[str] = Field(None, description="Specific category to analyze")

class CashFlowInput(BaseModel):
    months_lookback: int = Field(default=3, ge=1, le=12)

class BudgetAnalysisInput(BaseModel):
    month_year: Optional[str] = Field(None, description="Target month in YYYY-MM")

class EMICalculatorInput(BaseModel):
    principal: float = Field(..., gt=0, description="Principal loan amount in INR")
    annual_interest_rate: float = Field(..., ge=0, description="Annual interest rate percentage")
    tenure_months: int = Field(..., gt=0, le=480, description="Tenure in months")

class LoanAffordabilityInput(BaseModel):
    proposed_emi: float = Field(..., gt=0, description="Proposed monthly loan EMI in INR")
    existing_emis: float = Field(default=0.0, ge=0, description="Any existing active loan EMIs")

class AnomalyDetectionInput(BaseModel):
    limit: int = Field(default=5, ge=1, le=20)

class DocumentSearchInput(BaseModel):
    query: str = Field(..., min_length=2, description="Search query over user's uploaded financial documents")
    top_k: int = Field(default=3, ge=1, le=5)

class FinancialSummaryInput(BaseModel):
    pass

class BudgetRecommendationInput(BaseModel):
    savings_target_monthly: Optional[float] = Field(None, ge=0, description="Desired monthly savings target")

# Tool Definition Registry
TOOL_DEFINITIONS = [
    {
        "name": "transaction_search",
        "description": "Searches and filters the user's personal financial transactions by merchant, category, date range, or amount.",
        "parameters": TransactionSearchInput.model_json_schema()
    },
    {
        "name": "spending_analysis",
        "description": "Computes exact spending totals, category breakdowns, monthly trends, and month-over-month percentage changes.",
        "parameters": SpendingAnalysisInput.model_json_schema()
    },
    {
        "name": "cash_flow_analysis",
        "description": "Calculates verified total income, total expenditure, net cash flow, and savings rate using deterministic formulas.",
        "parameters": CashFlowInput.model_json_schema()
    },
    {
        "name": "budget_analysis",
        "description": "Compares actual spending against budgeted limits and flags categories exceeding thresholds.",
        "parameters": BudgetAnalysisInput.model_json_schema()
    },
    {
        "name": "emi_calculator",
        "description": "Computes exact monthly instalment (EMI), total interest, and amortization schedule for loans.",
        "parameters": EMICalculatorInput.model_json_schema()
    },
    {
        "name": "loan_affordability",
        "description": "Estimates the effect of a proposed loan EMI on the user's disposable cash flow and evaluates debt-to-income risk.",
        "parameters": LoanAffordabilityInput.model_json_schema()
    },
    {
        "name": "transaction_anomaly_detection",
        "description": "Scans transactions using robust statistical thresholds and an Isolation Forest model to flag unusual spending deviations.",
        "parameters": AnomalyDetectionInput.model_json_schema()
    },
    {
        "name": "financial_document_search",
        "description": "Performs semantic search over the user's uploaded financial documents (PDF/CSV/TXT) and returns relevant passages with page citations.",
        "parameters": DocumentSearchInput.model_json_schema()
    },
    {
        "name": "financial_summary",
        "description": "Generates a comprehensive structured financial status report based on verified calculations.",
        "parameters": FinancialSummaryInput.model_json_schema()
    },
    {
        "name": "budget_recommendation",
        "description": "Suggests specific category budget adjustments based on historical spending patterns and savings targets.",
        "parameters": BudgetRecommendationInput.model_json_schema()
    }
]

class ToolRegistry:
    @classmethod
    def execute_tool(
        cls,
        tool_name: str,
        arguments: Dict[str, Any],
        db: Session,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Executes a typed tool with server-side authorization enforcement.
        user_id is strictly provided from the authenticated session and cannot be spoofed.
        """
        start_time = time.time()
        TelemetryService.record_tool_invocation(tool_name)
        
        try:
            if tool_name == "transaction_search":
                inp = TransactionSearchInput(**arguments)
                q = (
                    db.query(Transaction, Category.name.label("category_name"))
                    .join(Category, Transaction.category_id == Category.id)
                    .filter(Transaction.user_id == user_id)
                )
                if inp.query:
                    kw = f"%{inp.query}%"
                    q = q.filter((Transaction.merchant.ilike(kw)) | (Transaction.description.ilike(kw)))
                if inp.category:
                    q = q.filter(Category.name.ilike(f"%{inp.category}%"))
                if inp.start_date:
                    q = q.filter(Transaction.date >= inp.start_date)
                if inp.end_date:
                    q = q.filter(Transaction.date <= inp.end_date)
                if inp.min_amount is not None:
                    q = q.filter(Transaction.amount >= inp.min_amount)
                if inp.max_amount is not None:
                    q = q.filter(Transaction.amount <= inp.max_amount)
                    
                rows = q.order_by(Transaction.date.desc()).limit(inp.limit).all()
                results = [
                    {
                        "id": t.id,
                        "date": t.date,
                        "merchant": t.merchant,
                        "category": cat_name,
                        "amount": t.amount,
                        "type": t.type,
                        "payment_method": t.payment_method
                    } for t, cat_name in rows
                ]
                return {"count": len(results), "transactions": results}

            elif tool_name == "spending_analysis":
                inp = SpendingAnalysisInput(**arguments)
                q = (
                    db.query(Transaction, Category.name.label("category_name"))
                    .join(Category, Transaction.category_id == Category.id)
                    .filter(Transaction.user_id == user_id, Transaction.type == "EXPENSE")
                )
                if inp.start_date:
                    q = q.filter(Transaction.date >= inp.start_date)
                if inp.end_date:
                    q = q.filter(Transaction.date <= inp.end_date)
                if inp.category:
                    q = q.filter(Category.name.ilike(f"%{inp.category}%"))
                    
                txs = q.all()
                total_spent = sum(t.amount for t, _ in txs)
                by_cat = {}
                by_month = {}
                for t, cat in txs:
                    by_cat[cat] = by_cat.get(cat, 0.0) + t.amount
                    m = t.date[:7]
                    by_month[m] = by_month.get(m, 0.0) + t.amount
                    
                return {
                    "total_spending": round(total_spent, 2),
                    "transaction_count": len(txs),
                    "by_category": {k: round(v, 2) for k, v in by_cat.items()},
                    "by_month": {k: round(v, 2) for k, v in sorted(by_month.items())}
                }

            elif tool_name == "cash_flow_analysis":
                inp = CashFlowInput(**arguments)
                txs = db.query(Transaction).filter(Transaction.user_id == user_id).all()
                inc = sum(t.amount for t in txs if t.type == "INCOME")
                exp = sum(t.amount for t in txs if t.type == "EXPENSE")
                return FinancialMathService.calculate_cash_flow(inc, exp)

            elif tool_name == "budget_analysis":
                inp = BudgetAnalysisInput(**arguments)
                budgets = (
                    db.query(Budget, Category.name.label("category_name"))
                    .join(Category, Budget.category_id == Category.id)
                    .filter(Budget.user_id == user_id)
                    .all()
                )
                m_filter = inp.month_year or time.strftime("%Y-%m")
                txs = db.query(Transaction).filter(
                    Transaction.user_id == user_id,
                    Transaction.type == "EXPENSE",
                    Transaction.date.startswith(m_filter)
                ).all()
                
                spend_by_cat = {}
                for t in txs:
                    spend_by_cat[t.category_id] = spend_by_cat.get(t.category_id, 0.0) + t.amount
                    
                comparison = []
                for b, cat_name in budgets:
                    spent = spend_by_cat.get(b.category_id, 0.0)
                    pct = (spent / b.monthly_limit * 100.0) if b.monthly_limit > 0 else 0.0
                    comparison.append({
                        "category": cat_name,
                        "monthly_limit": b.monthly_limit,
                        "actual_spent": round(spent, 2),
                        "remaining": round(b.monthly_limit - spent, 2),
                        "percentage_used": round(pct, 1),
                        "over_budget": spent > b.monthly_limit
                    })
                return {"target_month": m_filter, "categories": comparison}

            elif tool_name == "emi_calculator":
                inp = EMICalculatorInput(**arguments)
                return FinancialMathService.calculate_emi(
                    principal=inp.principal,
                    annual_interest_rate=inp.annual_interest_rate,
                    tenure_months=inp.tenure_months
                )

            elif tool_name == "loan_affordability":
                inp = LoanAffordabilityInput(**arguments)
                txs = db.query(Transaction).filter(Transaction.user_id == user_id).all()
                monthly_inc = sum(t.amount for t in txs if t.type == "INCOME") / max(1, len(set(t.date[:7] for t in txs)))
                monthly_exp = sum(t.amount for t in txs if t.type == "EXPENSE") / max(1, len(set(t.date[:7] for t in txs)))
                return FinancialMathService.calculate_affordability(
                    monthly_income=monthly_inc,
                    monthly_expenses=monthly_exp,
                    proposed_emi=inp.proposed_emi,
                    existing_emis=inp.existing_emis
                )

            elif tool_name == "transaction_anomaly_detection":
                inp = AnomalyDetectionInput(**arguments)
                txs = (
                    db.query(Transaction, Category.name.label("category_name"))
                    .join(Category, Transaction.category_id == Category.id)
                    .filter(Transaction.user_id == user_id)
                    .order_by(Transaction.date.desc())
                    .all()
                )
                tx_dicts = [
                    {
                        "id": t.id,
                        "date": t.date,
                        "merchant": t.merchant,
                        "category_name": cat_name,
                        "amount": t.amount,
                        "type": t.type,
                        "payment_method": t.payment_method
                    } for t, cat_name in txs
                ]
                anomalies = TransactionAnomalyDetector.detect_anomalies(tx_dicts)
                return {"anomalies_detected": anomalies[:inp.limit]}

            elif tool_name == "financial_document_search":
                inp = DocumentSearchInput(**arguments)
                chunks = DocumentService.retrieve_relevant_chunks(
                    db=db,
                    user_id=user_id,
                    query=inp.query,
                    top_k=inp.top_k
                )
                return {
                    "query": inp.query,
                    "retrieved_count": len(chunks),
                    "passages": chunks
                }

            elif tool_name == "financial_summary":
                txs = db.query(Transaction).filter(Transaction.user_id == user_id).all()
                inc = sum(t.amount for t in txs if t.type == "INCOME")
                exp = sum(t.amount for t in txs if t.type == "EXPENSE")
                cf = FinancialMathService.calculate_cash_flow(inc, exp)
                return {
                    "summary_period": "Historical records",
                    "total_income": cf["total_income"],
                    "total_expenses": cf["total_expenses"],
                    "net_cash_flow": cf["net_cash_flow"],
                    "savings_rate_pct": cf["savings_rate"],
                    "total_transactions": len(txs)
                }

            elif tool_name == "budget_recommendation":
                inp = BudgetRecommendationInput(**arguments)
                budgets = (
                    db.query(Budget, Category.name.label("category_name"))
                    .join(Category, Budget.category_id == Category.id)
                    .filter(Budget.user_id == user_id)
                    .all()
                )
                txs = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.type == "EXPENSE").all()
                cat_spend = {}
                for t in txs:
                    cat_spend[t.category_id] = cat_spend.get(t.category_id, 0.0) + t.amount
                    
                recommendations = []
                for b, cat_name in budgets:
                    actual = cat_spend.get(b.category_id, 0.0)
                    if actual > b.monthly_limit:
                        recs = f"Consider increasing {cat_name} budget to ₹{actual * 1.05:,.0f} or curtailing discretionary spend by {(actual - b.monthly_limit):,.0f}."
                    else:
                        recs = f"Spending is within limit. You have a surplus buffer of ₹{(b.monthly_limit - actual):,.0f}."
                    recommendations.append({
                        "category": cat_name,
                        "current_limit": b.monthly_limit,
                        "observed_monthly_spending": round(actual, 2),
                        "recommendation": recs
                    })
                return {"recommendations": recommendations}

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e), "tool": tool_name}
        finally:
            exec_time = (time.time() - start_time) * 1000
