from fastapi import APIRouter, status
from pydantic import BaseModel
from src.verticals.crm_call_center.sla_engine import call_center_sla_engine

router = APIRouter(prefix="/api/v1/crm/sla", tags=["Call Center SLA Management & Escalation Engine (Section 24.4)"])

class TrackSlaRequest(BaseModel):
    ticket_id: str
    priority: str = "HIGH"
    first_due_minutes: int = 120
    res_due_minutes: int = 1440
    organization_id: str = "ORG-KARIS-RETAIL"

@router.post("/track", status_code=status.HTTP_201_CREATED)
def track_ticket_sla(req: TrackSlaRequest):
    return call_center_sla_engine.track_ticket_sla(
        req.ticket_id, req.priority, req.first_due_minutes, req.res_due_minutes, req.organization_id
    )

@router.post("/sweep", status_code=status.HTTP_200_OK)
def trigger_sla_sweep():
    """Sweeps active SLA records, identifies breaches, and auto-escalates support tickets (`TICKET_ESCALATED`)."""
    escalated = call_center_sla_engine.execute_sla_escalation_sweep()
    return {"status": "SUCCESS", "escalated_count": len(escalated), "escalated_tickets": escalated}
