import re
from typing import Dict, Any, Tuple

class RequestRouter:
    """
    Classifies user intent to route requests to the most efficient, safe, and cost-effective execution path.
    Prevents prompt injection and filters unsupported/unsafe financial advice.
    """

    ADVERSARIAL_PATTERNS = [
        r"ignore (all )?(previous|prior) instructions",
        r"system prompt",
        r"you are now a",
        r"jailbreak",
        r"drop table",
        r"delete from",
        r"update users",
        r"<script>",
        r"reveal (?:your )?(?:system |secret |api )?key",
        r"reveal your secrets",
        r"bypass security"
    ]

    UNSUPPORTED_ADVICE_PATTERNS = [
        r"\b(?:penny )?stock(?:s)?\b.*(?:buy|sell|pick)",
        r"which (?:penny )?stock",
        r"guaranteed (?:[0-9]+% )?returns",
        r"crypto (?:pump|tips|dump)",
        r"insider trading",
        r"will the market crash tomorrow"
    ]

    EDUCATIONAL_KNOWLEDGE_PATTERNS = [
        r"what is the difference between",
        r"what is an? (?:emergency fund|dti|debt-to-income|amortization)",
        r"explain what (?:debt-to-income|dti|nominal|effective|compound)",
        r"why (?:do )?lenders care about",
        r"how does (?:compound interest|reducing balance) work"
    ]

    @classmethod
    def classify_intent(cls, message: str) -> Tuple[str, Dict[str, Any]]:
        msg = message.lower().strip()

        # 1. Adversarial / Prompt Injection check
        for pattern in cls.ADVERSARIAL_PATTERNS:
            if re.search(pattern, msg):
                return "unsupported_or_unsafe", {
                    "reason": "Security policy violation: prompt injection or unauthorized instruction attempt."
                }

        # 2. Unsupported financial speculation check
        for pattern in cls.UNSUPPORTED_ADVICE_PATTERNS:
            if re.search(pattern, msg):
                return "unsupported_or_unsafe", {
                    "reason": "Regulatory compliance: FinPilot AI provides deterministic analytics over verified personal records and does not provide speculative investment recommendations or stock tips."
                }

        # 3. Pure Educational / Definitional Knowledge (e.g. difference between nominal vs effective rate)
        for pattern in cls.EDUCATIONAL_KNOWLEDGE_PATTERNS:
            if re.search(pattern, msg):
                return "financial_knowledge", {}

        # 4. Document RAG (Statements, PDFs, uploaded documents, agreements, clauses, sanction letters)
        if any(w in msg for w in [
            "document", "pdf", "file", "statement", "policy", "agreement",
            "uploaded", "clause", "contract", "salary slip", "prepayment",
            "sanction letter", "processing fee", "late payment fee", "mandate"
        ]):
            return "document_rag", {}

        # 5. Loan & EMI calculations
        if any(w in msg for w in ["emi", "calculate emi", "loan", "amortization", "afford", "tenure", "interest rate", "home loan", "car loan"]):
            return "loan_calculation", {}

        # 6. Anomaly detection
        if any(w in msg for w in ["unusual", "anomaly", "fraud", "suspicious", "spike", "irregular", "flagged"]):
            return "anomaly_explanation", {}

        # 7. Budgeting & Planning
        if any(w in msg for w in ["budget", "savings goal", "savings targets", "overspending", "target", "recommend budget", "saving rate"]):
            return "budget_planning", {}

        # 8. Personal transaction analytics
        if any(w in msg for w in [
            "spend", "expense", "expenses", "income", "transaction", "transactions", "swiggy", "zomato",
            "amazon", "uber", "ola", "blusmart", "rides", "merchant", "how much did i", "cash flow", "balance", "total",
            "salary", "groceries", "housing & rent", "dmart", "blinkit"
        ]):
            return "personal_analytics", {}

        # 9. Fallback general financial knowledge
        return "financial_knowledge", {}
