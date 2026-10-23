import os
import sys
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from backend.app.db.session import engine, Base, SessionLocal
from backend.app.core.security import get_password_hash
from backend.app.models.user import User
from backend.app.models.financial import Category, Transaction, Budget, SavingsGoal
from backend.app.models.document import Document
from backend.app.services.document_service import DocumentService
from backend.app.services.anomaly_detector import TransactionAnomalyDetector

def seed_database():
    print("[INIT] Initializing FinPilot AI Database & Seeding Synthetic Indian Data...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed or Retrieve Categories
        categories_data = [
            ("Salary", "INCOME", "Briefcase", "#10b981"),
            ("Investments", "INCOME", "TrendingUp", "#059669"),
            ("Housing & Rent", "EXPENSE", "Home", "#6366f1"),
            ("Groceries", "EXPENSE", "ShoppingCart", "#3b82f6"),
            ("Food & Dining", "EXPENSE", "Utensils", "#f59e0b"),
            ("Transportation", "EXPENSE", "Car", "#8b5cf6"),
            ("Utilities", "EXPENSE", "Zap", "#06b6d4"),
            ("Shopping", "EXPENSE", "ShoppingBag", "#ec4899"),
            ("Healthcare", "EXPENSE", "HeartPulse", "#ef4444"),
            ("Entertainment", "EXPENSE", "Film", "#d946ef"),
            ("General", "EXPENSE", "CreditCard", "#64748b")
        ]
        
        cat_map = {}
        for name, c_type, icon, color in categories_data:
            cat = db.query(Category).filter(Category.name == name).first()
            if not cat:
                cat = Category(name=name, type=c_type, icon=icon, color=color)
                db.add(cat)
                db.commit()
                db.refresh(cat)
            cat_map[name] = cat.id

        # 2. Seed Demo User
        demo_user = db.query(User).filter(User.email == "demo@finpilot.ai").first()
        if not demo_user:
            demo_user = User(
                email="demo@finpilot.ai",
                full_name="Aarav Sharma",
                hashed_password=get_password_hash("DemoFinPilot2026!"),
                is_demo_user=True
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print(f"Created demo user: {demo_user.email} (ID: {demo_user.id})")
        else:
            print(f"Using existing demo user: {demo_user.email}")

        # Clear existing demo transactions to ensure clean idempotency
        db.query(Transaction).filter(Transaction.user_id == demo_user.id).delete()
        db.query(Budget).filter(Budget.user_id == demo_user.id).delete()
        db.query(SavingsGoal).filter(SavingsGoal.user_id == demo_user.id).delete()
        db.commit()

        # 3. Seed Realistic Indian Transactions (Aug, Sep, Oct 2026)
        synthetic_txs = [
            # August 2026
            ("2026-08-01", 125000.00, "INCOME", "Salary", "Infosys Technologies", "NETBANKING", "Monthly Salary August"),
            ("2026-08-02", 32000.00, "EXPENSE", "Housing & Rent", "DLF CyberCity Properties", "NETBANKING", "August Apartment Rent"),
            ("2026-08-03", 2250.00, "EXPENSE", "Groceries", "Blinkit", "UPI", "Organic staples and milk"),
            ("2026-08-05", 480.00, "EXPENSE", "Food & Dining", "Zomato", "UPI", "Lunch bowl delivery"),
            ("2026-08-07", 1200.00, "EXPENSE", "Transportation", "Uber India", "UPI", "Office ride"),
            ("2026-08-10", 3100.00, "EXPENSE", "Utilities", "Tata Power", "NETBANKING", "Electricity Bill"),
            ("2026-08-14", 1540.00, "EXPENSE", "Food & Dining", "Swiggy", "UPI", "Weekend dinner"),
            ("2026-08-18", 4500.00, "EXPENSE", "Shopping", "Myntra", "CARD", "Formal shirts & trousers"),
            ("2026-08-22", 849.00, "EXPENSE", "Entertainment", "Netflix India", "CARD", "Monthly subscription"),
            ("2026-08-25", 1450.00, "EXPENSE", "Healthcare", "Apollo Pharmacy", "UPI", "Multivitamins"),
            
            # September 2026
            ("2026-09-01", 125000.00, "INCOME", "Salary", "Infosys Technologies", "NETBANKING", "Monthly Salary September"),
            ("2026-09-02", 32000.00, "EXPENSE", "Housing & Rent", "DLF CyberCity Properties", "NETBANKING", "September Apartment Rent"),
            ("2026-09-04", 3100.00, "EXPENSE", "Groceries", "Zepto", "UPI", "Fresh groceries & fruits"),
            ("2026-09-06", 650.00, "EXPENSE", "Food & Dining", "Zomato", "UPI", "Dinner order"),
            ("2026-09-09", 980.00, "EXPENSE", "Transportation", "Ola Cabs", "UPI", "Commute ride"),
            ("2026-09-12", 1499.00, "EXPENSE", "Utilities", "Airtel Xstream Fiber", "UPI", "Broadband internet"),
            ("2026-09-15", 5200.00, "EXPENSE", "Shopping", "Amazon India", "CARD", "Kitchen appliances"),
            ("2026-09-20", 849.00, "EXPENSE", "Entertainment", "Netflix India", "CARD", "Monthly subscription"),
            ("2026-09-23", 2800.00, "EXPENSE", "Healthcare", "Max Healthcare", "UPI", "Consultation fee"),
            ("2026-09-28", 18500.00, "EXPENSE", "Food & Dining", "Taj Palace Luxury Dining", "CARD", "Anniversary celebration dinner (Unusual Spike)"),
            
            # October 2026 (Current Month)
            ("2026-10-01", 125000.00, "INCOME", "Salary", "Infosys Technologies", "NETBANKING", "Monthly Salary October"),
            ("2026-10-02", 32000.00, "EXPENSE", "Housing & Rent", "DLF CyberCity Properties", "NETBANKING", "October Apartment Rent"),
            ("2026-10-04", 2850.00, "EXPENSE", "Groceries", "D-Mart", "CARD", "Monthly grocery haul"),
            ("2026-10-05", 540.00, "EXPENSE", "Food & Dining", "Swiggy", "UPI", "Lunch meal"),
            ("2026-10-07", 1320.00, "EXPENSE", "Transportation", "Uber India", "UPI", "Airport ride"),
            ("2026-10-10", 45000.00, "EXPENSE", "Shopping", "Apple Store Saket", "CARD", "iPad Air M3 Purchase (Outlier/Unusual)"),
            ("2026-10-12", 2800.00, "EXPENSE", "Utilities", "Tata Power", "NETBANKING", "Electricity Bill"),
            ("2026-10-15", 950.00, "EXPENSE", "Food & Dining", "Zomato", "UPI", "Dinner combo"),
            ("2026-10-18", 1200.00, "EXPENSE", "Transportation", "BluSmart EV", "UPI", "Office commute"),
            ("2026-10-20", 3500.00, "EXPENSE", "Healthcare", "Apollo Pharmacy", "UPI", "Winter medications"),
            ("2026-10-22", 2100.00, "EXPENSE", "Groceries", "Blinkit", "UPI", "Household essentials")
        ]

        tx_objects = []
        for dt, amt, t_type, cat_name, merch, method, desc in synthetic_txs:
            t = Transaction(
                user_id=demo_user.id,
                category_id=cat_map[cat_name],
                date=dt,
                amount=amt,
                type=t_type,
                merchant=merch,
                payment_method=method,
                description=desc,
                is_synthetic=True,
                anomaly_flag=False,
                anomaly_score=0.0
            )
            db.add(t)
            tx_objects.append(t)
        db.commit()

        # Run Anomaly Detector to flag outliers
        formatted = [
            {"id": t.id, "amount": t.amount, "type": t.type, "category_name": next(c for c, id_ in cat_map.items() if id_ == t.category_id), "merchant": t.merchant}
            for t in tx_objects
        ]
        anomalies = TransactionAnomalyDetector.detect_anomalies(formatted)
        anomaly_map = {a["transaction_id"]: a for a in anomalies}
        
        for t in tx_objects:
            if t.id in anomaly_map:
                t.anomaly_flag = True
                t.anomaly_score = anomaly_map[t.id]["anomaly_score"]
                t.anomaly_reason = anomaly_map[t.id]["reason"]
        db.commit()
        print(f"Seeded {len(synthetic_txs)} transactions with {len(anomalies)} detected anomalies.")

        # 4. Seed Monthly Budgets for October 2026
        budget_specs = [
            ("Housing & Rent", 35000.00),
            ("Groceries", 12000.00),
            ("Food & Dining", 10000.00),
            ("Transportation", 8000.00),
            ("Utilities", 6000.00),
            ("Shopping", 15000.00),
            ("Healthcare", 5000.00),
            ("Entertainment", 3000.00)
        ]
        for c_name, limit in budget_specs:
            b = Budget(
                user_id=demo_user.id,
                category_id=cat_map[c_name],
                monthly_limit=limit,
                month_year="2026-10"
            )
            db.add(b)
        db.commit()
        print(f"Seeded {len(budget_specs)} category budgets for October 2026.")

        # 5. Seed Savings Goals
        goals = [
            SavingsGoal(
                user_id=demo_user.id,
                title="Emergency Reserve Fund (6 Months Expenses)",
                target_amount=300000.00,
                current_amount=215000.00,
                target_date="2027-03-31"
            ),
            SavingsGoal(
                user_id=demo_user.id,
                title="Down Payment for Electric Vehicle (Tata Curvv EV)",
                target_amount=400000.00,
                current_amount=160000.00,
                target_date="2027-08-15"
            ),
            SavingsGoal(
                user_id=demo_user.id,
                title="International Vacation to Japan",
                target_amount=250000.00,
                current_amount=95000.00,
                target_date="2027-05-01"
            )
        ]
        db.add_all(goals)
        db.commit()
        print(f"Seeded {len(goals)} active savings goals.")

        # 6. Seed Sample Financial Document in Document Center
        doc_filename = "HDFC_Home_Loan_Sanction_and_Schedule.txt"
        doc_content = """HDFC BANK HOME LOAN SANCTION LETTER & AMORTIZATION TERMS
Loan Account Number: HDFC-HL-2026-88912
Applicant Name: Aarav Sharma
Sanction Date: 15-September-2026
Sanctioned Principal Loan Amount: INR 50,00,000 (Fifty Lakhs Indian Rupees)
Applicable Interest Rate: 8.50% per annum (Floating, linked to HDFC Repo-Linked Benchmark Lending Rate)
Tenure: 240 Months (20 Years)
Calculated Monthly Instalment (EMI): INR 43,391.16 per month

KEY BORROWER TERMS & CONDITIONS:
1. Prepayment & Foreclosure Charges: Nil prepayment penalty on floating rate home loans for individual borrowers, in accordance with Reserve Bank of India (RBI) master directives.
2. Property Insurance: Mandatory comprehensive property insurance coverage covering natural disasters and structural damage during loan tenure.
3. Repayment Mandate: Auto-debit via NACH/e-Mandate from primary salary account on the 5th of each calendar month.
4. Late Payment Fee: Penal interest of 2.0% per month on overdue instalments exceeding 30 days.
5. Processing Fee: One-time administrative fee of INR 10,000 plus applicable GST.
"""
        db.query(Document).filter(Document.user_id == demo_user.id).delete()
        db.commit()

        doc = Document(
            user_id=demo_user.id,
            filename=doc_filename,
            file_type="txt",
            file_size_bytes=len(doc_content.encode("utf-8")),
            status="PROCESSING"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        chunks = DocumentService.process_and_index_document(db, doc, doc_content.encode("utf-8"))
        print(f"Indexed sample financial agreement document with {chunks} chunks.")

        print("[SUCCESS] FinPilot AI Database successfully initialized and seeded!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
