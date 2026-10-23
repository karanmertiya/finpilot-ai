# FinPilot AI — REST API Contracts & Schema Specification

All API endpoints are versioned under `/api/v1`. Interactive Swagger documentation is available at `http://localhost:8000/docs`.

---

## 1. Authentication

### Instant Demo Login (1-Click)
- **POST** `/auth/demo-login`
- **Response** `200 OK`:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "user": {
      "id": "58b0456b-c1b1-4f9a-a2af-db6b687eff42",
      "email": "demo@finpilot.ai",
      "full_name": "Aarav Sharma",
      "is_active": true,
      "is_demo_user": true,
      "created_at": "2026-10-23T16:31:45.334900"
    }
  }
  ```

---

## 2. Financial Dashboard

### Real-time Computed Metrics
- **GET** `/dashboard/metrics`
- **Headers**: `Authorization: Bearer <token>`
- **Response** `200 OK`:
  ```json
  {
    "total_income": 375000.0,
    "total_expenses": 205207.0,
    "net_cash_flow": 169793.0,
    "savings_rate": 45.3,
    "currency": "INR",
    "is_synthetic": true,
    "spending_by_category": [
      { "category": "Housing & Rent", "amount": 96000.0, "percentage": 46.8, "color": "#6366f1" },
      { "category": "Shopping", "amount": 54700.0, "percentage": 26.7, "color": "#ec4899" }
    ],
    "budget_utilization": [...],
    "unusual_alerts": [...],
    "ai_financial_summary": "Over the recorded period, you had total income of ₹375,000.00..."
  }
  ```

---

## 3. AI Copilot Chat & Tool Calling

### Submit Natural Language Query
- **POST** `/chat`
- **Request Body**:
  ```json
  {
    "message": "Calculate EMI for a 20 lakh home loan at 8.5% interest for 20 years",
    "conversation_id": null
  }
  ```
- **Response** `200 OK`:
  ```json
  {
    "conversation_id": "99ea78f1-c423-4e47-a877-e63084bb9ef0",
    "message_id": "c7112028-1b6a-49a3-9565-d069a531b782",
    "sender": "assistant",
    "content": "### 📊 Loan EMI Amortization Summary\n\n- **Monthly EMI**: ₹17,356.46\n- **Total Principal**: ₹2,000,000.00\n- **Total Interest Payable**: ₹2,165,553.29\n- **Total Cost of Loan**: ₹4,165,553.29...",
    "intent": "loan_calculation",
    "tool_calls": [
      {
        "tool_name": "emi_calculator",
        "arguments": { "principal": 2000000.0, "annual_interest_rate": 8.5, "tenure_months": 240 },
        "result": { "monthly_emi": 17356.46, "total_interest": 2165553.29 },
        "execution_time_ms": 1.2
      }
    ],
    "citations": [],
    "chart_data": null,
    "latency_ms": 2.4
  }
  ```

---

## 4. Deterministic Financial Calculators

### Loan EMI Amortization
- **POST** `/calculations/emi`
- **Request Body**:
  ```json
  {
    "principal": 500000.0,
    "annual_interest_rate": 8.5,
    "tenure_months": 60
  }
  ```
- **Response** `200 OK`:
  ```json
  {
    "monthly_emi": 10258.26,
    "total_principal": 500000.0,
    "total_interest": 115495.6,
    "total_payment": 615495.6,
    "interest_to_principal_ratio": 0.231,
    "schedule_preview": [
      { "month": 1, "emi": 10258.26, "principal_paid": 6716.59, "interest_paid": 3541.67, "remaining_balance": 493283.41 }
    ]
  }
  ```

---

## 5. System Observability & Evaluation

### Live Metrics & Telemetry
- **GET** `/system/metrics`
- **Trigger 40-Test AI Evaluation Benchmark**:
  - **POST** `/system/run-evaluation`
  - Returns pass rate, category breakdown, RAG Recall@3, and average latency.
