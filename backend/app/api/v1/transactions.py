import csv
import io
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.financial import Transaction, Category
from backend.app.schemas.financial import (
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse,
    CategoryResponse
)
from backend.app.services.anomaly_detector import TransactionAnomalyDetector
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Retrieves all standard financial categories."""
    cats = db.query(Category).order_by(Category.name.asc()).all()
    return [CategoryResponse.model_validate(c) for c in cats]

@router.get("", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = None,
    type: Optional[str] = Query(None, pattern=r"^(INCOME|EXPENSE)$"),
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    anomaly_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists transactions with multi-dimensional filtering, searching, and pagination."""
    q = (
        db.query(Transaction, Category.name.label("category_name"), Category.color.label("category_color"))
        .join(Category, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == current_user.id)
    )

    if category_id:
        q = q.filter(Transaction.category_id == category_id)
    if type:
        q = q.filter(Transaction.type == type)
    if search:
        kw = f"%{search}%"
        q = q.filter((Transaction.merchant.ilike(kw)) | (Transaction.description.ilike(kw)))
    if start_date:
        q = q.filter(Transaction.date >= start_date)
    if end_date:
        q = q.filter(Transaction.date <= end_date)
    if min_amount is not None:
        q = q.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        q = q.filter(Transaction.amount <= max_amount)
    if anomaly_only:
        q = q.filter(Transaction.anomaly_flag == True)

    total_count = q.count()

    # Aggregate income and expenses
    all_matching = q.all()
    total_inc = sum(t.amount for t, _, _ in all_matching if t.type == "INCOME")
    total_exp = sum(t.amount for t, _, _ in all_matching if t.type == "EXPENSE")

    # Pagination
    items = q.order_by(Transaction.date.desc()).offset((page - 1) * page_size).limit(page_size).all()

    tx_list = []
    for t, cat_name, cat_color in items:
        tx_dict = {
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
        tx_list.append(TransactionResponse(**tx_dict))

    return TransactionListResponse(
        transactions=tx_list,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_income=round(total_inc, 2),
        total_expense=round(total_exp, 2)
    )

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new transaction and runs automated anomaly scoring."""
    category = db.query(Category).filter(Category.id == tx_in.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category_id")

    tx = Transaction(
        user_id=current_user.id,
        category_id=tx_in.category_id,
        date=tx_in.date,
        amount=tx_in.amount,
        type=tx_in.type,
        merchant=tx_in.merchant,
        payment_method=tx_in.payment_method,
        description=tx_in.description,
        is_recurring=tx_in.is_recurring,
        is_synthetic=False
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    # Check for anomaly against user's history
    user_txs = (
        db.query(Transaction, Category.name.label("category_name"))
        .join(Category, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )
    formatted = [
        {"id": t.id, "amount": t.amount, "type": t.type, "category_name": c_name, "merchant": t.merchant}
        for t, c_name in user_txs
    ]
    anomalies = TransactionAnomalyDetector.detect_anomalies(formatted)
    flagged = next((a for a in anomalies if a["transaction_id"] == tx.id), None)
    if flagged:
        tx.anomaly_flag = True
        tx.anomaly_score = flagged["anomaly_score"]
        tx.anomaly_reason = flagged["reason"]
        db.commit()
        db.refresh(tx)

    AuditService.log_event(
        db=db,
        action="TRANSACTION_CREATE",
        resource_type="TRANSACTION",
        user_id=current_user.id,
        resource_id=tx.id,
        details={"amount": tx.amount, "merchant": tx.merchant, "anomaly": tx.anomaly_flag}
    )

    return TransactionResponse(
        id=tx.id,
        user_id=tx.user_id,
        category_id=tx.category_id,
        category_name=category.name,
        category_color=category.color,
        date=tx.date,
        amount=tx.amount,
        type=tx.type,
        merchant=tx.merchant,
        payment_method=tx.payment_method,
        description=tx.description,
        is_recurring=tx.is_recurring,
        is_synthetic=tx.is_synthetic,
        anomaly_flag=tx.anomaly_flag,
        anomaly_score=tx.anomaly_score,
        anomaly_reason=tx.anomaly_reason,
        created_at=tx.created_at
    )

@router.post("/import-csv")
def import_transactions_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Imports transactions from a CSV file with validation and duplicate detection.
    Expected CSV columns: date, amount, type, merchant, category, payment_method, description
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = file.file.read().decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(content))
    
    categories = {c.name.lower(): c.id for c in db.query(Category).all()}
    default_cat_id = list(categories.values())[0] if categories else None

    # Existing user transactions for duplicate checking (date, amount, merchant)
    existing_records = set(
        (t.date, round(t.amount, 2), t.merchant.strip().lower())
        for t in db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    )

    imported_count = 0
    duplicate_count = 0
    error_count = 0

    for row in reader:
        try:
            date_str = row.get("date", "").strip()
            amount_val = float(row.get("amount", 0))
            t_type = row.get("type", "EXPENSE").strip().upper()
            merchant_val = row.get("merchant", "Unknown").strip()
            cat_name = row.get("category", "General").strip().lower()
            method = row.get("payment_method", "UPI").strip()
            desc = row.get("description", "").strip()

            if not date_str or amount_val <= 0 or t_type not in ["INCOME", "EXPENSE"]:
                error_count += 1
                continue

            # Duplicate check
            key = (date_str, round(amount_val, 2), merchant_val.lower())
            if key in existing_records:
                duplicate_count += 1
                continue

            cat_id = categories.get(cat_name, default_cat_id)
            new_tx = Transaction(
                user_id=current_user.id,
                category_id=cat_id,
                date=date_str,
                amount=amount_val,
                type=t_type,
                merchant=merchant_val,
                payment_method=method,
                description=desc,
                is_synthetic=False
            )
            db.add(new_tx)
            existing_records.add(key)
            imported_count += 1
        except Exception:
            error_count += 1

    db.commit()

    AuditService.log_event(
        db=db,
        action="CSV_IMPORT",
        resource_type="TRANSACTION",
        user_id=current_user.id,
        details={
            "imported": imported_count,
            "duplicates_skipped": duplicate_count,
            "errors_skipped": error_count
        }
    )

    return {
        "status": "success",
        "imported_count": imported_count,
        "duplicate_count": duplicate_count,
        "error_count": error_count,
        "message": f"Successfully imported {imported_count} transaction(s). Skipped {duplicate_count} duplicate(s)."
    }

@router.get("/export-demo")
def export_demo_dataset():
    """Generates and downloads a clean synthetic Indian fintech CSV demo dataset."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "amount", "type", "merchant", "category", "payment_method", "description"])
    
    samples = [
        ["2026-10-01", "125000.00", "INCOME", "Tech Solutions Ltd", "Salary", "NETBANKING", "Monthly Salary Credit"],
        ["2026-10-02", "32000.00", "EXPENSE", "DLF CyberCity Properties", "Housing & Rent", "NETBANKING", "Apartment Rent October"],
        ["2026-10-04", "1850.00", "EXPENSE", "Blinkit", "Groceries", "UPI", "Weekly vegetables and dairy"],
        ["2026-10-05", "420.00", "EXPENSE", "Swiggy", "Food & Dining", "UPI", "Dinner order from Biryani Blues"],
        ["2026-10-08", "2499.00", "EXPENSE", "Reliance Digital", "Shopping", "CARD", "Bluetooth earbuds"],
        ["2026-10-10", "45000.00", "EXPENSE", "Apple Store Saket", "Shopping", "CARD", "iPad Air M3 Purchase (Unusual)"],
        ["2026-10-12", "1250.00", "EXPENSE", "Uber India", "Transportation", "UPI", "Airport commute cab"],
        ["2026-10-15", "849.00", "EXPENSE", "Netflix India", "Utilities", "CARD", "Premium 4K Subscription"],
        ["2026-10-18", "3400.00", "EXPENSE", "Apollo Pharmacy", "Healthcare", "UPI", "Monthly medicines and vitamins"]
    ]
    for row in samples:
        writer.writerow(row)
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=finpilot_demo_transactions.csv"}
    )
