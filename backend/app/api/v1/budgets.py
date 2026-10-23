from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.financial import Budget, SavingsGoal, Category, Transaction
from backend.app.schemas.financial import (
    BudgetCreate,
    BudgetResponse,
    BudgetVsActual,
    SavingsGoalCreate,
    SavingsGoalResponse
)
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets & Goals"])

@router.get("", response_model=List[BudgetVsActual])
def get_budgets_vs_actual(
    month_year: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all category budgets and compares against actual verified spending."""
    target_month = month_year or datetime.now().strftime("%Y-%m")

    budgets = (
        db.query(Budget, Category.name.label("category_name"), Category.color.label("category_color"))
        .join(Category, Budget.category_id == Category.id)
        .filter(Budget.user_id == current_user.id)
        .all()
    )

    # Actual spending in month
    txs = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "EXPENSE",
        Transaction.date.startswith(target_month)
    ).all()

    spending_by_cat = {}
    for t in txs:
        spending_by_cat[t.category_id] = spending_by_cat.get(t.category_id, 0.0) + t.amount

    result = []
    for b, cat_name, cat_color in budgets:
        spent = spending_by_cat.get(b.category_id, 0.0)
        limit = b.monthly_limit
        rem = limit - spent
        pct = (spent / limit * 100.0) if limit > 0 else 0.0
        result.append(BudgetVsActual(
            category_id=b.category_id,
            category_name=cat_name,
            category_color=cat_color,
            budget_limit=round(limit, 2),
            actual_spent=round(spent, 2),
            remaining=round(rem, 2),
            percentage_used=round(pct, 1),
            is_over_budget=spent > limit
        ))

    result.sort(key=lambda x: x.percentage_used, reverse=True)
    return result

@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def set_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sets or updates a monthly category budget."""
    category = db.query(Category).filter(Category.id == budget_in.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category_id")

    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category_id == budget_in.category_id,
        Budget.month_year == budget_in.month_year
    ).first()

    if existing:
        existing.monthly_limit = budget_in.monthly_limit
        db.commit()
        db.refresh(existing)
        target_budget = existing
    else:
        new_b = Budget(
            user_id=current_user.id,
            category_id=budget_in.category_id,
            monthly_limit=budget_in.monthly_limit,
            month_year=budget_in.month_year
        )
        db.add(new_b)
        db.commit()
        db.refresh(new_b)
        target_budget = new_b

    return BudgetResponse(
        id=target_budget.id,
        user_id=target_budget.user_id,
        category_id=target_budget.category_id,
        category_name=category.name,
        category_color=category.color,
        monthly_limit=target_budget.monthly_limit,
        month_year=target_budget.month_year,
        created_at=target_budget.created_at
    )

@router.get("/goals", response_model=List[SavingsGoalResponse])
def list_savings_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all active savings goals for the user."""
    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == current_user.id).order_by(SavingsGoal.created_at.desc()).all()
    resp = []
    for g in goals:
        progress = (g.current_amount / g.target_amount * 100.0) if g.target_amount > 0 else 0.0
        resp.append(SavingsGoalResponse(
            id=g.id,
            user_id=g.user_id,
            title=g.title,
            target_amount=g.target_amount,
            current_amount=g.current_amount,
            target_date=g.target_date,
            progress_percentage=round(min(progress, 100.0), 1),
            created_at=g.created_at
        ))
    return resp

@router.post("/goals", response_model=SavingsGoalResponse, status_code=status.HTTP_201_CREATED)
def create_savings_goal(
    goal_in: SavingsGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new financial savings target."""
    goal = SavingsGoal(
        user_id=current_user.id,
        title=goal_in.title,
        target_amount=goal_in.target_amount,
        current_amount=goal_in.current_amount,
        target_date=goal_in.target_date
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    progress = (goal.current_amount / goal.target_amount * 100.0) if goal.target_amount > 0 else 0.0
    return SavingsGoalResponse(
        id=goal.id,
        user_id=goal.user_id,
        title=goal.title,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        progress_percentage=round(min(progress, 100.0), 1),
        created_at=goal.created_at
    )
