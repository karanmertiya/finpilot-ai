from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.ensemble import IsolationForest

class TransactionAnomalyDetector:
    """
    Transparent transaction anomaly detection engine combining robust statistical thresholds (IQR / Z-score)
    and an Isolation Forest machine learning model.
    """

    @staticmethod
    def detect_anomalies(
        transactions: List[Dict[str, Any]],
        contamination: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Analyzes a list of transactions for a user and flags atypical deviations.
        
        Args:
            transactions: List of dicts with keys: id, date, amount, type, merchant, category_name
            contamination: Expected proportion of outliers in the data
            
        Returns:
            List of detected anomaly items with scores, severity, reasons, and historical comparisons.
        """
        expense_txs = [t for t in transactions if t.get("type") == "EXPENSE" and t.get("amount", 0) > 0]
        if not expense_txs:
            return []

        # 1. Group by category to build baseline statistics
        category_stats: Dict[str, Dict[str, float]] = {}
        for cat in set(t.get("category_name", "General") for t in expense_txs):
            cat_amounts = [t["amount"] for t in expense_txs if t.get("category_name") == cat]
            if cat_amounts:
                arr = np.array(cat_amounts)
                q25, q75 = np.percentile(arr, 25), np.percentile(arr, 75)
                iqr = q75 - q25
                category_stats[cat] = {
                    "mean": float(np.mean(arr)),
                    "median": float(np.median(arr)),
                    "std": float(np.std(arr)) if len(arr) > 1 else 0.0,
                    "q75": float(q75),
                    "iqr": float(iqr),
                    "upper_bound": float(q75 + 1.5 * iqr),
                    "count": len(cat_amounts)
                }

        # 2. Fit Isolation Forest if sufficient transactions exist (>= 15)
        iso_scores = {}
        if len(expense_txs) >= 15:
            try:
                features = []
                for t in expense_txs:
                    cat = t.get("category_name", "General")
                    c_stat = category_stats.get(cat, {"mean": t["amount"], "std": 1.0})
                    std_val = c_stat["std"] if c_stat["std"] > 0 else 1.0
                    z_cat = (t["amount"] - c_stat["mean"]) / std_val
                    features.append([
                        np.log1p(t["amount"]),
                        z_cat,
                        1.0 if t.get("payment_method") == "UPI" else 0.0
                    ])
                
                X = np.array(features)
                model = IsolationForest(
                    contamination=min(max(contamination, 0.02), 0.15),
                    random_state=42,
                    n_estimators=100
                )
                model.fit(X)
                # Decision function: lower values mean more anomalous
                raw_scores = model.decision_function(X)
                # Map to [0, 1] anomaly score where 1.0 is extreme anomaly
                min_s, max_s = raw_scores.min(), raw_scores.max()
                norm_scores = 1.0 - (raw_scores - min_s) / (max_s - min_s + 1e-9)
                for i, t in enumerate(expense_txs):
                    iso_scores[t["id"]] = float(norm_scores[i])
            except Exception:
                iso_scores = {}

        anomalies = []
        for t in expense_txs:
            t_id = t["id"]
            amount = t["amount"]
            cat = t.get("category_name", "General")
            c_stat = category_stats.get(cat)
            
            is_flagged = False
            reasons = []
            severity = "LOW"
            benchmark_text = ""
            
            iso_score = iso_scores.get(t_id, 0.0)
            
            if c_stat:
                upper = c_stat["upper_bound"]
                mean_val = c_stat["mean"]
                multiplier = amount / (mean_val + 1e-6)
                
                if amount > upper and multiplier >= 2.0:
                    is_flagged = True
                    reasons.append(f"Transaction amount ₹{amount:,.2f} is {multiplier:.1f}x higher than the typical average of ₹{mean_val:,.2f} for {cat}.")
                    benchmark_text = f"Category '{cat}' average: ₹{mean_val:,.2f} (IQR upper bound: ₹{upper:,.2f})"
                    
                    if multiplier >= 4.0 or iso_score > 0.8:
                        severity = "HIGH"
                    elif multiplier >= 2.5 or iso_score > 0.65:
                        severity = "MEDIUM"
                    else:
                        severity = "LOW"
            
            # Combine statistical rule with Isolation Forest score
            combined_score = round(max(iso_score, min(multiplier / 5.0, 1.0) if c_stat else iso_score), 2)
            
            if is_flagged or combined_score >= 0.75:
                reason_str = " ".join(reasons) if reasons else f"Unusual spend pattern detected by multi-variate statistical model."
                anomalies.append({
                    "transaction_id": t_id,
                    "date": t.get("date", ""),
                    "merchant": t.get("merchant", "Unknown Merchant"),
                    "category": cat,
                    "amount": float(amount),
                    "anomaly_score": float(combined_score),
                    "severity": severity,
                    "reason": reason_str,
                    "historical_benchmark": benchmark_text or f"Deviates from typical user baseline.",
                    "caveat": "Flagged solely as an atypical spending deviation; does not indicate confirmed fraud or unauthorized activity."
                })

        # Sort by anomaly score descending
        anomalies.sort(key=lambda x: x["anomaly_score"], reverse=True)
        return anomalies
