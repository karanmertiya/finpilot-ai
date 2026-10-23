import time
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.chat import Conversation, Message
from backend.app.schemas.chat import ChatResponse, ToolCallRecord, CitationRecord
from backend.app.ai.orchestration.router import RequestRouter
from backend.app.ai.orchestration.llm_provider import get_llm_provider
from backend.app.ai.tools.registry import ToolRegistry
from backend.app.services.audit_service import AuditService

SYSTEM_FINANCIAL_PROMPT = """You are FinPilot AI, a production-grade personal financial intelligence copilot.
Your mission is to provide accurate, verified, and helpful insights based exclusively on the user's authentic financial records.

Core Directives:
1. Grounding: All numbers, percentages, and merchant details must strictly match the verified data provided. Never fabricate figures or hallucinate transactions.
2. Financial Precision: Clarify whether interest rates are nominal reducing balance or flat. Remind users that affordability calculations are illustrative.
3. Tone: Professional, clear, objective, and empathetic fintech assistant.
4. Formatting: Use clean Markdown tables, bullet points, and highlight key numbers in bold INR (₹).
5. Safety: Do not make speculative stock market predictions or guarantee financial returns.
"""

class AIOrchestrator:
    @classmethod
    def process_chat_message(
        cls,
        db: Session,
        user_id: str,
        message_text: str,
        conversation_id: Optional[str] = None
    ) -> ChatResponse:
        start_time = time.time()
        
        # 1. Retrieve or create conversation
        if conversation_id:
            conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
            if not conv:
                conv = Conversation(id=conversation_id, user_id=user_id, title=message_text[:40])
                db.add(conv)
                db.commit()
        else:
            conv = Conversation(user_id=user_id, title=message_text[:40])
            db.add(conv)
            db.commit()
            db.refresh(conv)

        # Record User Message
        user_msg = Message(
            conversation_id=conv.id,
            sender="user",
            content=message_text
        )
        db.add(user_msg)
        db.commit()

        # 2. Intent Classification & Safety Filtering
        intent, intent_meta = RequestRouter.classify_intent(message_text)

        tool_calls_executed = []
        citations_found = []
        chart_data = None
        assistant_reply = ""

        # 3. Handle Unsupported or Unsafe queries immediately
        if intent == "unsupported_or_unsafe":
            AuditService.log_event(
                db=db,
                action="SECURITY_ALERT",
                resource_type="CHAT",
                user_id=user_id,
                status="DENIED",
                details={"reason": intent_meta.get("reason"), "query": message_text[:100]}
            )
            assistant_reply = (
                f"🛡️ **Security & Compliance Notice**: I cannot fulfill this request. "
                f"{intent_meta.get('reason', 'Request violates security or regulatory policy.')} "
                f"FinPilot AI operates strictly within secure personal financial analytics boundaries."
            )

        # 4. Route and execute tools
        elif intent == "loan_calculation":
            # Extract loan numbers from text if available
            p_match = re.search(r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|k|inr|rs|rupees)?", message_text.lower())
            
            # Smart parameter extraction
            principal = 500000.0
            if "10 lakh" in message_text.lower() or "10,00,000" in message_text:
                principal = 1000000.0
            elif "25 lakh" in message_text.lower():
                principal = 2500000.0
            elif "50 lakh" in message_text.lower():
                principal = 5000000.0
            elif "20 lakh" in message_text.lower():
                principal = 2000000.0
            elif "5 lakh" in message_text.lower():
                principal = 500000.0

            rate = 8.5
            rate_match = re.search(r"(\d+(?:\.\d+)?)\s*%", message_text)
            if rate_match:
                rate = float(rate_match.group(1))

            tenure = 240  # 20 years default
            tenure_match = re.search(r"(\d+)\s*(?:years?|yrs?)", message_text.lower())
            if tenure_match:
                tenure = int(tenure_match.group(1)) * 12

            if "afford" in message_text.lower():
                tool_name = "loan_affordability"
                args = {"proposed_emi": 25000.0, "existing_emis": 0.0}
            else:
                tool_name = "emi_calculator"
                args = {"principal": principal, "annual_interest_rate": rate, "tenure_months": tenure}

            t_start = time.time()
            t_res = ToolRegistry.execute_tool(tool_name, args, db, user_id)
            t_dur = (time.time() - t_start) * 1000
            
            tool_calls_executed.append(ToolCallRecord(
                tool_name=tool_name,
                arguments=args,
                result=t_res,
                execution_time_ms=round(t_dur, 2)
            ))
            
            provider = get_llm_provider()
            assistant_reply = provider.generate(
                system_prompt=SYSTEM_FINANCIAL_PROMPT,
                user_prompt=message_text,
                tools_data={"tool_executed": tool_name, "result": t_res}
            )

        elif intent == "anomaly_explanation":
            tool_name = "transaction_anomaly_detection"
            args = {"limit": 5}
            t_start = time.time()
            t_res = ToolRegistry.execute_tool(tool_name, args, db, user_id)
            t_dur = (time.time() - t_start) * 1000
            
            tool_calls_executed.append(ToolCallRecord(
                tool_name=tool_name,
                arguments=args,
                result=t_res,
                execution_time_ms=round(t_dur, 2)
            ))
            
            provider = get_llm_provider()
            assistant_reply = provider.generate(
                system_prompt=SYSTEM_FINANCIAL_PROMPT,
                user_prompt=message_text,
                tools_data={"tool_executed": tool_name, "result": t_res}
            )

        elif intent == "document_rag":
            tool_name = "financial_document_search"
            args = {"query": message_text, "top_k": 3}
            t_start = time.time()
            t_res = ToolRegistry.execute_tool(tool_name, args, db, user_id)
            t_dur = (time.time() - t_start) * 1000
            
            tool_calls_executed.append(ToolCallRecord(
                tool_name=tool_name,
                arguments=args,
                result=t_res,
                execution_time_ms=round(t_dur, 2)
            ))
            
            for p in t_res.get("passages", []):
                citations_found.append(CitationRecord(
                    document_id=p["document_id"],
                    filename=p["filename"],
                    page_number=p.get("page_number", 1),
                    passage=p["passage"],
                    similarity_score=p["similarity_score"]
                ))
                
            provider = get_llm_provider()
            assistant_reply = provider.generate(
                system_prompt=SYSTEM_FINANCIAL_PROMPT,
                user_prompt=message_text,
                tools_data={"tool_executed": tool_name, "result": t_res}
            )

        elif intent == "budget_planning":
            tool_name = "budget_analysis" if "compare" in message_text.lower() or "limit" in message_text.lower() else "budget_recommendation"
            args = {}
            t_start = time.time()
            t_res = ToolRegistry.execute_tool(tool_name, args, db, user_id)
            t_dur = (time.time() - t_start) * 1000
            
            tool_calls_executed.append(ToolCallRecord(
                tool_name=tool_name,
                arguments=args,
                result=t_res,
                execution_time_ms=round(t_dur, 2)
            ))
            
            provider = get_llm_provider()
            assistant_reply = provider.generate(
                system_prompt=SYSTEM_FINANCIAL_PROMPT,
                user_prompt=message_text,
                tools_data={"tool_executed": tool_name, "result": t_res}
            )

        elif intent == "personal_analytics":
            if "cash flow" in message_text.lower() or "savings rate" in message_text.lower():
                tool_name = "cash_flow_analysis"
                args = {"months_lookback": 3}
            else:
                tool_name = "spending_analysis"
                args = {}
                
            t_start = time.time()
            t_res = ToolRegistry.execute_tool(tool_name, args, db, user_id)
            t_dur = (time.time() - t_start) * 1000
            
            tool_calls_executed.append(ToolCallRecord(
                tool_name=tool_name,
                arguments=args,
                result=t_res,
                execution_time_ms=round(t_dur, 2)
            ))
            
            if tool_name == "spending_analysis" and "by_category" in t_res:
                chart_data = {
                    "type": "pie",
                    "title": "Spending by Category",
                    "data": [{"name": k, "value": v} for k, v in t_res["by_category"].items()]
                }
                
            provider = get_llm_provider()
            assistant_reply = provider.generate(
                system_prompt=SYSTEM_FINANCIAL_PROMPT,
                user_prompt=message_text,
                tools_data={"tool_executed": tool_name, "result": t_res}
            )

        else: # general financial knowledge
            provider = get_llm_provider()
            assistant_reply = provider.generate(
                system_prompt=SYSTEM_FINANCIAL_PROMPT,
                user_prompt=message_text,
                tools_data=None
            )

        total_latency = (time.time() - start_time) * 1000

        # Persist assistant response
        asst_msg = Message(
            conversation_id=conv.id,
            sender="assistant",
            content=assistant_reply,
            tool_calls=[tc.model_dump() for tc in tool_calls_executed] if tool_calls_executed else None,
            citations=[c.model_dump() for c in citations_found] if citations_found else None,
            chart_data=chart_data,
            latency_ms={"total_ms": round(total_latency, 2)}
        )
        db.add(asst_msg)
        db.commit()
        db.refresh(asst_msg)

        # Audit query execution
        AuditService.log_event(
            db=db,
            action="CHAT_COMPLETION",
            resource_type="CHAT",
            user_id=user_id,
            resource_id=conv.id,
            status="SUCCESS",
            details={
                "intent": intent,
                "tool_calls_count": len(tool_calls_executed),
                "citations_count": len(citations_found),
                "latency_ms": round(total_latency, 2)
            }
        )

        return ChatResponse(
            conversation_id=conv.id,
            message_id=asst_msg.id,
            sender="assistant",
            content=assistant_reply,
            intent=intent,
            tool_calls=tool_calls_executed,
            citations=citations_found,
            chart_data=chart_data,
            latency_ms=round(total_latency, 2)
        )
