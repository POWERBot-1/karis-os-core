import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus

class CallCenterSlaManagementEngine:
    """
    KARIS OS™ Call Center SLA Management & Escalation Engine (Section 24.4).
    Monitors First Response Time, Resolution Time, and automatic supervisor escalations.
    """
    def __init__(self):
        self.sla_records: Dict[str, Dict] = {}
        self.escalations: Dict[str, Dict] = {}

    def track_ticket_sla(
        self,
        ticket_id: str,
        priority: str = "HIGH",
        first_response_due_minutes: int = 120,
        resolution_due_minutes: int = 1440,
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        now = datetime.now(timezone.utc)
        sla_id = f"SLA-REC-{uuid.uuid4().hex[:8].upper()}"
        record = {
            "sla_record_id": sla_id,
            "ticket_id": ticket_id,
            "organization_id": organization_id,
            "ticket_priority": priority,
            "first_response_due_at": (now + timedelta(minutes=first_response_due_minutes)).isoformat(),
            "resolution_due_at": (now + timedelta(minutes=resolution_due_minutes)).isoformat(),
            "sla_status": "ACTIVE_WITHIN_SLA"
        }
        self.sla_records[sla_id] = record
        return record

    def execute_sla_escalation_sweep(self) -> List[Dict]:
        """Sweeps active SLA records, identifies breaches, and auto-escalates tickets."""
        escalated = []
        now = datetime.now(timezone.utc).isoformat()
        for sla_id, rec in list(self.sla_records.items()):
            if rec["sla_status"] == "ACTIVE_WITHIN_SLA" and now > rec["resolution_due_at"]:
                rec["sla_status"] = "ESCALATED_SUPERVISOR"
                esc_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"
                esc = {
                    "escalation_id": esc_id,
                    "ticket_id": rec["ticket_id"],
                    "sla_record_id": sla_id,
                    "escalated_to_supervisor_id": "SUPERVISOR-ID-99",
                    "escalation_reason": "RESOLUTION_TIME_EXCEEDED",
                    "sla_status": "ESCALATED_SUPERVISOR",
                    "organization_id": rec["organization_id"]
                }
                self.escalations[esc_id] = esc
                escalated.append(esc)

                ev = EventPayload(
                    event_type="TICKET_ESCALATED",
                    event_category=EventCategory.GOVERNANCE,
                    actor_identity_id="SYSTEM_SLA_ENGINE",
                    organization_id=rec["organization_id"],
                    correlation_id=esc_id,
                    source_module="CALL_CENTER_SLA_ENGINE",
                    payload={
                        "escalation_id": esc_id,
                        "ticket_id": rec["ticket_id"],
                        "previous_agent_id": "AGENT-ID-01",
                        "escalated_to_supervisor_id": "SUPERVISOR-ID-99",
                        "escalation_reason": "RESOLUTION_TIME_EXCEEDED",
                        "sla_status": "ESCALATED_SUPERVISOR"
                    }
                )
                event_bus.publish(ev)

        return escalated

call_center_sla_engine = CallCenterSlaManagementEngine()
