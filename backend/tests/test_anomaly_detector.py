import pytest
from backend.app.services.anomaly_detector import TransactionAnomalyDetector

def test_anomaly_detector_flags_extreme_spike():
    """Verify that an extreme 10x deviation in a category is flagged with appropriate severity."""
    txs = [
        {"id": f"tx-{i}", "amount": 500.0, "type": "EXPENSE", "category_name": "Food & Dining", "merchant": "Swiggy", "date": "2026-10-01"}
        for i in range(15)
    ]
    # Add outlier
    txs.append({
        "id": "tx-spike",
        "amount": 15000.0,
        "type": "EXPENSE",
        "category_name": "Food & Dining",
        "merchant": "Luxury Club Dining",
        "date": "2026-10-15"
    })

    anomalies = TransactionAnomalyDetector.detect_anomalies(txs)
    assert len(anomalies) > 0
    spike = next((a for a in anomalies if a["transaction_id"] == "tx-spike"), None)
    assert spike is not None
    assert spike["severity"] in ["MEDIUM", "HIGH"]
    assert "higher than" in spike["reason"]
    assert "does not indicate confirmed fraud" in spike["caveat"]

def test_anomaly_detector_empty_or_normal():
    """Verify that normal transactions with minimal variance are not flagged unnecessarily."""
    txs = [
        {"id": f"tx-{i}", "amount": 1000.0 + (i * 10), "type": "EXPENSE", "category_name": "Groceries", "merchant": "Blinkit", "date": "2026-10-01"}
        for i in range(10)
    ]
    anomalies = TransactionAnomalyDetector.detect_anomalies(txs)
    assert len(anomalies) == 0
