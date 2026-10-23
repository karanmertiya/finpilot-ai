from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import List, Dict, Any, Tuple
import math

# Set standard precision for financial arithmetic
getcontext().prec = 28

def round_inr(value: Decimal) -> Decimal:
    """Rounds a Decimal value to 2 decimal places using standard ROUND_HALF_UP."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class FinancialMathService:
    @staticmethod
    def calculate_emi(
        principal: float,
        annual_interest_rate: float,
        tenure_months: int
    ) -> Dict[str, Any]:
        """
        Calculates monthly instalment (EMI) using the standard reducing balance amortization formula.
        
        Formula:
            E = P * r * (1 + r)^n / ((1 + r)^n - 1)
            where:
                P = principal loan amount
                r = monthly interest rate = (annual_interest_rate / 12) / 100
                n = tenure in months
        
        Special Cases:
            - If annual_interest_rate == 0: E = P / n
        """
        if principal <= 0:
            raise ValueError("Principal amount must be greater than zero.")
        if tenure_months <= 0 or tenure_months > 480:
            raise ValueError("Tenure months must be between 1 and 480.")
        if annual_interest_rate < 0:
            raise ValueError("Annual interest rate cannot be negative.")

        dec_p = Decimal(str(principal))
        dec_n = Decimal(str(tenure_months))
        
        if annual_interest_rate == 0:
            monthly_emi = round_inr(dec_p / dec_n)
            total_payment = round_inr(dec_p)
            total_interest = Decimal("0.00")
            ratio = 0.0
            
            # Simple schedule preview
            schedule = []
            rem = dec_p
            for m in range(1, min(13, tenure_months + 1)):
                p_paid = monthly_emi if m < tenure_months else rem
                rem = max(Decimal("0.00"), rem - p_paid)
                schedule.append({
                    "month": m,
                    "emi": float(monthly_emi),
                    "principal_paid": float(p_paid),
                    "interest_paid": 0.0,
                    "remaining_balance": float(round_inr(rem))
                })
        else:
            monthly_rate = Decimal(str(annual_interest_rate)) / Decimal("1200")
            rate_factor = (Decimal("1") + monthly_rate) ** tenure_months
            
            numerator = dec_p * monthly_rate * rate_factor
            denominator = rate_factor - Decimal("1")
            dec_emi = round_inr(numerator / denominator)
            
            # Generate amortization schedule preview (up to 12 months)
            schedule = []
            rem_balance = dec_p
            total_int = Decimal("0.00")
            
            for m in range(1, tenure_months + 1):
                interest_payment = round_inr(rem_balance * monthly_rate)
                if m == tenure_months:
                    principal_payment = rem_balance
                    current_emi = principal_payment + interest_payment
                    rem_balance = Decimal("0.00")
                else:
                    principal_payment = dec_emi - interest_payment
                    rem_balance = max(Decimal("0.00"), rem_balance - principal_payment)
                    current_emi = dec_emi
                
                total_int += interest_payment
                
                if m <= 12 or m == tenure_months:
                    schedule.append({
                        "month": m,
                        "emi": float(round_inr(current_emi)),
                        "principal_paid": float(round_inr(principal_payment)),
                        "interest_paid": float(round_inr(interest_payment)),
                        "remaining_balance": float(round_inr(rem_balance))
                    })
            
            monthly_emi = dec_emi
            total_interest = round_inr(total_int)
            total_payment = round_inr(dec_p + total_interest)
            ratio = float(round(float(total_interest) / float(dec_p), 4)) if principal > 0 else 0.0

        return {
            "monthly_emi": float(monthly_emi),
            "total_principal": float(round_inr(dec_p)),
            "total_interest": float(total_interest),
            "total_payment": float(total_payment),
            "interest_to_principal_ratio": ratio,
            "effective_rate_type": "Nominal annual rate compounded monthly (reducing balance)",
            "schedule_preview": schedule[:12]
        }

    @staticmethod
    def calculate_affordability(
        monthly_income: float,
        monthly_expenses: float,
        proposed_emi: float,
        existing_emis: float = 0.0
    ) -> Dict[str, Any]:
        """
        Estimates loan affordability based on Debt-To-Income (DTI) and net disposable cash flow.
        
        Benchmark Rules:
            - DTI <= 35%: AFFORDABLE (Safe financial cushion)
            - 35% < DTI <= 45%: TIGHT (Manageable but leaves modest headroom for unexpected expenses)
            - 45% < DTI <= 55%: HIGH_RISK (Vulnerable to income disruption or emergencies)
            - DTI > 55%: UNAFFORDABLE (Likely to cause cash-flow deficits)
        """
        dec_income = Decimal(str(max(0.0, monthly_income)))
        dec_expenses = Decimal(str(max(0.0, monthly_expenses)))
        dec_proposed_emi = Decimal(str(max(0.0, proposed_emi)))
        dec_existing_emis = Decimal(str(max(0.0, existing_emis)))
        
        disposable_before_loan = round_inr(dec_income - dec_expenses - dec_existing_emis)
        total_monthly_debt = dec_existing_emis + dec_proposed_emi
        
        if dec_income > 0:
            dti = float(round((total_monthly_debt / dec_income) * Decimal("100"), 2))
        else:
            dti = 100.0 if total_monthly_debt > 0 else 0.0
            
        remaining_cash_flow = round_inr(disposable_before_loan - dec_proposed_emi)
        
        if dti <= 35.0 and remaining_cash_flow > 0:
            verdict = "AFFORDABLE"
            analysis = (
                f"Your proposed EMI of ₹{proposed_emi:,.2f} represents {dti:.1f}% of your monthly income. "
                f"This leaves a comfortable projected surplus of ₹{float(remaining_cash_flow):,.2f} per month."
            )
        elif dti <= 45.0 and remaining_cash_flow > 0:
            verdict = "TIGHT"
            analysis = (
                f"Your proposed EMI of ₹{proposed_emi:,.2f} brings total debt servicing to {dti:.1f}% of income. "
                f"Your estimated monthly surplus would be ₹{float(remaining_cash_flow):,.2f}. Budgeting discipline will be crucial."
            )
        elif dti <= 55.0 and remaining_cash_flow >= 0:
            verdict = "HIGH_RISK"
            analysis = (
                f"High debt obligation ({dti:.1f}% of income). Surplus is only ₹{float(remaining_cash_flow):,.2f}. "
                f"Any unexpected medical, home, or lifestyle expense could cause negative monthly cash flow."
            )
        else:
            verdict = "UNAFFORDABLE"
            analysis = (
                f"The proposed EMI results in an excessive debt-to-income ratio ({dti:.1f}%) and "
                f"a projected monthly cash deficit of ₹{abs(float(remaining_cash_flow)):,.2f}."
            )

        assumptions = [
            "Assumes stable monthly income consistent with historical averages.",
            "Living expenses are estimated based on past 3-month spending trends.",
            "Illustrative calculation only; does not constitute credit appraisal or guaranteed approval.",
            "Does not account for future inflation, tax slab changes, or discretionary bonuses."
        ]

        return {
            "monthly_income": float(round_inr(dec_income)),
            "current_fixed_expenses": float(round_inr(dec_expenses)),
            "current_disposable_income": float(disposable_before_loan),
            "proposed_emi": float(round_inr(dec_proposed_emi)),
            "total_obligations_post_loan": float(round_inr(total_monthly_debt)),
            "debt_to_income_ratio": dti,
            "remaining_disposable_cash_flow": float(remaining_cash_flow),
            "affordability_verdict": verdict,
            "analysis_text": analysis,
            "assumptions_and_limitations": assumptions
        }

    @staticmethod
    def calculate_cash_flow(income: float, expenses: float) -> Dict[str, Any]:
        """Calculates exact net cash flow and savings rate."""
        dec_inc = Decimal(str(max(0.0, income)))
        dec_exp = Decimal(str(max(0.0, expenses)))
        
        net_flow = round_inr(dec_inc - dec_exp)
        if dec_inc > 0:
            savings_rate = float(round((net_flow / dec_inc) * Decimal("100"), 2))
        else:
            savings_rate = 0.0

        return {
            "total_income": float(round_inr(dec_inc)),
            "total_expenses": float(round_inr(dec_exp)),
            "net_cash_flow": float(net_flow),
            "savings_rate": savings_rate
        }
