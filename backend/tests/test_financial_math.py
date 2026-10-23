import pytest
from backend.app.services.financial_math import FinancialMathService

def test_emi_standard_calculation():
    """Verify standard loan EMI formula matches exact mathematical amortization."""
    res = FinancialMathService.calculate_emi(
        principal=500000.0,
        annual_interest_rate=8.5,
        tenure_months=60
    )
    assert abs(res["monthly_emi"] - 10258.26) <= 0.05
    assert abs(res["total_principal"] - 500000.0) <= 0.01
    assert abs(res["total_interest"] - 115495.6) <= 1.0
    assert abs(res["total_payment"] - (500000.0 + res["total_interest"])) <= 0.05
    assert len(res["schedule_preview"]) > 0

def test_emi_zero_interest():
    """Verify zero-interest edge case divides principal by tenure exactly."""
    res = FinancialMathService.calculate_emi(
        principal=120000.0,
        annual_interest_rate=0.0,
        tenure_months=12
    )
    assert res["monthly_emi"] == 10000.0
    assert res["total_interest"] == 0.0
    assert res["total_payment"] == 120000.0

def test_emi_invalid_inputs():
    """Verify input validation on negative principal or zero tenure."""
    with pytest.raises(ValueError):
        FinancialMathService.calculate_emi(principal=-1000, annual_interest_rate=8.5, tenure_months=12)

    with pytest.raises(ValueError):
        FinancialMathService.calculate_emi(principal=100000, annual_interest_rate=8.5, tenure_months=0)

    with pytest.raises(ValueError):
        FinancialMathService.calculate_emi(principal=100000, annual_interest_rate=-5.0, tenure_months=12)

def test_affordability_verdict_thresholds():
    """Verify Debt-to-Income (DTI) thresholds and cash-flow surplus."""
    # Affordable: DTI <= 35%
    res1 = FinancialMathService.calculate_affordability(
        monthly_income=100000.0,
        monthly_expenses=40000.0,
        proposed_emi=25000.0,
        existing_emis=0.0
    )
    assert res1["affordability_verdict"] == "AFFORDABLE"
    assert res1["debt_to_income_ratio"] == 25.0
    assert res1["remaining_disposable_cash_flow"] == 35000.0

    # Unaffordable / High Risk: DTI > 55%
    res2 = FinancialMathService.calculate_affordability(
        monthly_income=50000.0,
        monthly_expenses=30000.0,
        proposed_emi=30000.0,
        existing_emis=0.0
    )
    assert res2["affordability_verdict"] == "UNAFFORDABLE"
    assert res2["debt_to_income_ratio"] == 60.0
    assert res2["remaining_disposable_cash_flow"] < 0

def test_cash_flow_and_savings_rate():
    """Verify net cash flow and savings rate calculation."""
    cf = FinancialMathService.calculate_cash_flow(income=100000.0, expenses=65000.0)
    assert cf["net_cash_flow"] == 35000.0
    assert cf["savings_rate"] == 35.0

    cf_zero_income = FinancialMathService.calculate_cash_flow(income=0.0, expenses=25000.0)
    assert cf_zero_income["net_cash_flow"] == -25000.0
    assert cf_zero_income["savings_rate"] == 0.0
