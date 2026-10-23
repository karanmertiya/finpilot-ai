from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.financial import Transaction, Category, Budget, SavingsGoal
from backend.app.services.financial_math import FinancialMathService
from backend.app.services.anomaly_detector import TransactionAnomalyDetector

class AnalyticsService:
    @staticmethod
    def get_dashboard_metrics(db: Session, user_id: str) -> Dict[str, Any]:
        """Aggregates all core financial metrics for the primary dashboard."""
        # 1. Fetch user transactions
        txs = (
            db.query(Transaction, Category.name.label("category_name"), Category.color.label("category_color"))
            .join(Category, Transaction.category_id == Category.id)
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.date.desc())
            .all()
        )
        
        tx_dicts = []
        total_income = 0.0
        total_expense = 0.0
        category_spending = defaultdict(float)
        category_colors = {}
        monthly_income_map = defaultdict(float)
        monthly_expense_map = defaultdict(float)

        for t, cat_name, cat_color in txs:
            t_dict = {
                "id": t.id,
                "user_id": t.user_id,
                "category_id": t.category_id,
                "category_name": cat_name,
                "category_color": cat_color,
                "date": t.date,
                "amount": t.amount,
                "type": t.type,
                "merchant": t.merchant,
                "payment_method": t.payment_method,
                "description": t.description,
                "is_recurring": t.is_recurring,
                "is_synthetic": t.is_synthetic,
                "anomaly_flag": t.anomaly_flag,
                "anomaly_score": t.anomaly_score,
                "anomaly_reason": t.anomaly_reason,
                "created_at": t.created_at
            }
            tx_dicts.append(t_dict)
            
            month_str = t.date[:7]  # YYYY-MM
            if t.type == "INCOME":
                total_income += t.amount
                monthly_income_map[month_str] += t.amount
            else:
                total_expense += t.amount
                category_spending[cat_name] += t.amount
                category_colors[cat_name] = cat_color or "#0ea5e9"
                monthly_expense_map[month_str] += t.amount

        # Cash flow calculation
        cf = FinancialMathService.calculate_cash_flow(total_income, total_expense)

        # Category spending breakdown
        category_breakdown = []
        for cat_name, amount in category_spending.items():
            pct = (amount / total_expense * 100.0) if total_expense > 0 else 0.0
            category_breakdown.append({
                "category": cat_name,
                "amount": round(amount, 2),
                "percentage": round(pct, 1),
                "color": category_colors.get(cat_name, "#0ea5e9")
            })
        category_breakdown.sort(key=lambda x: x["amount"], reverse=True)

        # Monthly trends (sorted chronologically)
        all_months = sorted(list(set(list(monthly_income_map.keys()) + list(monthly_expense_map.keys()))))
        monthly_trends = []
        for m in all_months:
            inc = monthly_income_map.get(m, 0.0)
            exp = monthly_expense_map.get(m, 0.0)
            monthly_trends.append({
                "month": m,
                "income": round(inc, 2),
                "expenses": round(exp, 2),
                "net": round(inc - exp, 2)
            })

        # 2. Budget utilization (for latest month)
        current_month = datetime.now().strftime("%Y-%m")
        budgets = (
            db.query(Budget, Category.name.label("category_name"), Category.color.label("category_color"))
            .join(Category, Budget.category_id == Category.id)
            .filter(Budget.user_id == user_id)
            .all()
        )
        
        # Calculate spending in current or latest month
        latest_month = all_months[-1] if all_months else current_month
        month_spend_by_cat = defaultdict(float)
        for t in tx_dicts:
            if t["date"].startswith(latest_month) and t["type"] == "EXPENSE":
                month_spend_by_cat[t["category_id"]] += t["amount"]

        budget_utilization = []
        for b, cat_name, cat_color in budgets:
            actual = month_spend_by_cat.get(b.category_id, 0.0)
            limit = b.monthly_limit
            rem = limit - actual
            pct = (actual / limit * 100.0) if limit > 0 else 0.0
            budget_utilization.append({
                "category_id": b.category_id,
                "category_name": cat_name,
                "category_color": cat_color,
                "budget_limit": round(limit, 2),
                "actual_spent": round(actual, 2),
                "remaining": round(rem, 2),
                "percentage_used": round(pct, 1),
                "is_over_budget": actual > limit
            })
        budget_utilization.sort(key=lambda x: x["percentage_used"], reverse=True)

        # 3. Anomaly detection
        anomalies = TransactionAnomalyDetector.detect_anomalies(tx_dicts)

        # 4. Synthesize AI Financial Summary
        top_cat = category_breakdown[0]["category"] if category_breakdown else "General"
        top_cat_amt = category_breakdown[0]["amount"] if category_breakdown else 0.0
        ai_summary = (
            f"Over the recorded period, you had total income of ₹{cf['total_income']:,.2f} "
            f"and total expenses of ₹{cf['total_expenses']:,.2f}, resulting in a net cash surplus of "
            f"₹{cf['net_cash_flow']:,.2f} (Savings Rate: {cf['savings_rate']:.1f}%). "
            f"Your highest spending category is {top_cat} (₹{top_cat_amt:,.2f}). "
            f"{len(anomalies)} transaction(s) flagged for review due to unusual deviation from historical baselines."
        )

        return {
            "total_income": cf["total_income"],
            "total_expenses": cf["total_expenses"],
            "net_cash_flow": cf["net_cash_flow"],
            "savings_rate": cf["savings_rate"],
            "currency": "INR",
            "is_synthetic": True,
            "spending_by_category": category_breakdown,
            "monthly_trend": monthly_trends,
            "recent_transactions": tx_dicts[:10],
            "budget_utilization": budget_utilization,
            "unusual_alerts": anomalies[:5],
            "ai_financial_summary": ai_summary
        }
