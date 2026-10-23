from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.observability import AuditEvent

class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditEvent:
        """Records a sanitized security audit event to the database."""
        # Sanitize sensitive fields from details
        sanitized_details = {}
        if details:
            for k, v in details.items():
                if any(secret_term in k.lower() for secret_term in ["password", "token", "secret", "auth", "credential", "card_number", "cvv"]):
                    sanitized_details[k] = "[REDACTED]"
                else:
                    sanitized_details[k] = str(v)[:500] if not isinstance(v, (int, float, bool, list, dict)) else v

        event = AuditEvent(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            details=sanitized_details,
            ip_address=ip_address
        )
        try:
            db.add(event)
            db.commit()
            db.refresh(event)
        except Exception:
            db.rollback()
        return event
