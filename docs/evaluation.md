# FinPilot AI — Automated Evaluation Benchmark Report

## 1. Evaluation Methodology
To prevent model hallucination, arithmetic drift, and unauthorized data leakage, FinPilot AI enforces an automated **40-question benchmark evaluation suite** executed against actual database records and indexed documents.

The test suite evaluates 6 core dimensions:
1. **Deterministic Calculations (6 tests)**: Standard reducing-balance EMI, zero-interest edge cases, high tenure, and DTI thresholds.
2. **Personal Transaction Analytics (8 tests)**: Exact category aggregates, merchant filtering, salary totals, and net cash flow.
3. **Budgeting & Planning (5 tests)**: Overspending detection, headroom calculation, and budget adjustments.
4. **Anomaly Detection (3 tests)**: Multi-factor outlier detection, deviation factors, and non-fraud caveats.
5. **RAG Document Retrieval (7 tests)**: Prepayment penalties, sanction terms, interest rates, and honest abstention on out-of-domain queries.
6. **Adversarial & Safety Defenses (8 tests)**: System prompt exfiltration, SQL injection, script injection, and market speculation refusal.
7. **Security & Tenant Isolation (3 tests)**: Cross-user ID spoofing attempts and document isolation.

---

## 2. Actual Measured Results

| Evaluation Metric | Target Benchmark | Measured Actual Result | Status |
| :--- | :--- | :--- | :--- |
| **Total Test Suite Pass Rate** | $\ge 90\%$ | **100.0% (40 / 40)** | PASSED |
| **Arithmetic Precision** | $100\%$ | **100.0% (Exact match within ₹0.05)** | PASSED |
| **RAG Retrieval Recall@3** | $\ge 85\%$ | **100.0%** | PASSED |
| **Honest RAG Abstention Rate** | $100\%$ | **100.0% (Zero false hallucinated citations)** | PASSED |
| **Prompt Injection Refusal Rate** | $100\%$ | **100.0%** | PASSED |
| **Cross-Tenant Access Refusal** | $100\%$ | **100.0%** | PASSED |
| **Average Query Latency** | $< 250\text{ ms}$ | **44.4 ms** | PASSED |

---

## 3. How to Run the Benchmark Locally
```bash
# Set Python UTF-8 encoding (Windows PowerShell)
$env:PYTHONIOENCODING="utf-8"

# Execute evaluation runner
python backend/app/ai/evaluation/runner.py
```
Outputs are written to `evals/reports/evaluation_results.json` and saved in the database under `evaluation_runs`.
