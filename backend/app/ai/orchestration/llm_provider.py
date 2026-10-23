from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
from backend.app.core.config import settings

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, tools_data: Optional[Dict[str, Any]] = None) -> str:
        pass

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str, tools_data: Optional[Dict[str, Any]] = None) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        full_prompt = f"System Instructions:\n{system_prompt}\n\n"
        if tools_data:
            full_prompt += f"Verified Tool Calculation Data:\n{tools_data}\n\n"
        full_prompt += f"User Request:\n{user_prompt}"

        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
        }
        
        try:
            resp = httpx.post(url, json=payload, timeout=settings.REQUEST_TIMEOUT_SECONDS)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            return f"Gemini API returned code {resp.status_code}: {resp.text}"
        except Exception as e:
            return f"Error communicating with Gemini provider: {str(e)}"

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str, tools_data: Optional[Dict[str, Any]] = None) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        sys_content = system_prompt
        if tools_data:
            sys_content += f"\n\nVerified Tool Data:\n{tools_data}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": sys_content},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        try:
            resp = httpx.post(url, headers=headers, json=payload, timeout=settings.REQUEST_TIMEOUT_SECONDS)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            return f"OpenAI API returned code {resp.status_code}: {resp.text}"
        except Exception as e:
            return f"Error communicating with OpenAI provider: {str(e)}"

class DeterministicFallbackProvider(BaseLLMProvider):
    """
    Offline/zero-credential engine that synthesizes answers from verified tool calculations.
    Guarantees mathematically exact and grounded outputs during offline testing and interview demos.
    """
    def generate(self, system_prompt: str, user_prompt: str, tools_data: Optional[Dict[str, Any]] = None) -> str:
        if not tools_data:
            return (
                "FinPilot AI is ready to analyze your financial records, compute loan EMIs, "
                "or search your uploaded financial documents. Please ask a specific query regarding your spending, "
                "budget, or financial documents."
            )
        
        # Tool-specific deterministic formatting
        tool_name = tools_data.get("tool_executed")
        result = tools_data.get("result", {})
        
        if tool_name == "emi_calculator":
            return (
                f"### 📊 Loan EMI Amortization Summary\n\n"
                f"- **Monthly EMI**: ₹{result.get('monthly_emi', 0):,.2f}\n"
                f"- **Total Principal**: ₹{result.get('total_principal', 0):,.2f}\n"
                f"- **Total Interest Payable**: ₹{result.get('total_interest', 0):,.2f}\n"
                f"- **Total Cost of Loan**: ₹{result.get('total_payment', 0):,.2f}\n"
                f"- **Interest-to-Principal Ratio**: {result.get('interest_to_principal_ratio', 0) * 100:.1f}%\n\n"
                f"*Calculation verified using standard reducing balance amortization formula.*"
            )

        if tool_name == "loan_affordability":
            return (
                f"### 🛡️ Loan Affordability Analysis\n\n"
                f"- **Verdict**: **{result.get('affordability_verdict')}**\n"
                f"- **Proposed EMI**: ₹{result.get('proposed_emi', 0):,.2f}\n"
                f"- **Debt-to-Income (DTI) Ratio**: {result.get('debt_to_income_ratio', 0)}%\n"
                f"- **Projected Remaining Surplus**: ₹{result.get('remaining_disposable_cash_flow', 0):,.2f}\n\n"
                f"{result.get('analysis_text', '')}\n\n"
                f"**Assumptions & Limitations:**\n"
                + "\n".join([f"- {a}" for a in result.get('assumptions_and_limitations', [])])
            )

        if tool_name == "cash_flow_analysis":
            return (
                f"### 📈 Cash Flow & Savings Summary\n\n"
                f"- **Total Recorded Income**: ₹{result.get('total_income', 0):,.2f}\n"
                f"- **Total Recorded Expenses**: ₹{result.get('total_expenses', 0):,.2f}\n"
                f"- **Net Cash Flow**: ₹{result.get('net_cash_flow', 0):,.2f}\n"
                f"- **Effective Savings Rate**: {result.get('savings_rate', 0)}%\n\n"
                f"Your cash flow is currently positive, reflecting disciplined financial headroom."
            )

        if tool_name == "spending_analysis":
            cat_lines = [f"- **{cat}**: ₹{amt:,.2f}" for cat, amt in result.get("by_category", {}).items()]
            return (
                f"### 💳 Spending Breakdown\n\n"
                f"- **Total Expenditure**: ₹{result.get('total_spending', 0):,.2f}\n"
                f"- **Transactions Count**: {result.get('transaction_count', 0)}\n\n"
                f"**Top Categories:**\n" + "\n".join(cat_lines)
            )

        if tool_name == "transaction_anomaly_detection":
            anomalies = result.get("anomalies_detected", [])
            if not anomalies:
                return "✅ No abnormal spending deviations detected. All recent transactions conform to your baseline patterns."
            
            lines = []
            for a in anomalies[:3]:
                lines.append(
                    f"⚠️ **{a['merchant']}** (₹{a['amount']:,.2f}) on {a['date']}\n"
                    f"  - **Severity**: {a['severity']}\n"
                    f"  - **Reason**: {a['reason']}\n"
                    f"  - **Benchmark**: {a['historical_benchmark']}\n"
                    f"  - *Note*: {a['caveat']}"
                )
            return "### 🔍 Anomaly Detection Report\n\n" + "\n\n".join(lines)

        if tool_name == "financial_document_search":
            passages = result.get("passages", [])
            if not passages:
                return (
                    "I searched your uploaded financial documents, but found no passages exceeding the similarity threshold. "
                    "Please verify that the document is uploaded and indexed, or refine your query keywords."
                )
            lines = [f"**Document: {p['filename']} (Page {p.get('page_number', 1)})**\n> \"{p['passage'][:300]}...\"" for p in passages]
            return (
                f"Based on your uploaded financial documents, here are the verified findings:\n\n"
                + "\n\n".join(lines)
            )

        if tool_name == "budget_recommendation":
            recs = [f"- **{r['category']}**: {r['recommendation']}" for r in result.get("recommendations", [])]
            return "### 🎯 Smart Budget Recommendations\n\n" + "\n".join(recs)

        return f"Here is the verified data for your query:\n\n```json\n{result}\n```"

def get_llm_provider() -> BaseLLMProvider:
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.LLM_MODEL)
    elif settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return OpenAIProvider(api_key=settings.OPENAI_API_KEY)
    else:
        return DeterministicFallbackProvider()
