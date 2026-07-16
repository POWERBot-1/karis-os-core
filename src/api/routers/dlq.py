from fastapi import APIRouter, status
from pydantic import BaseModel
from src.core.dlq_healing import dlq_engine

router = APIRouter(prefix="/api/v1/dlq", tags=["Distributed Dead-Letter Queue (DLQ) & Self-Healing (Section 36.6)"])

class RecordDlqRequest(BaseModel):
    event_id: str
    consumer_name: str = "RULE_ENGINE_SUBSCRIBER"
    error_message: str = "Transient database connection timeout during subscriber processing"
    organization_id: str = "ORG-KARIS-RETAIL"

@router.get("/status")
def get_dlq_status():
    return dlq_engine.get_dlq_status_summary()

@router.post("/record", status_code=status.HTTP_201_CREATED)
def record_dlq_failure(req: RecordDlqRequest):
    return dlq_engine.record_failed_dispatch(
        req.event_id, req.consumer_name, req.error_message, req.organization_id
    )

@router.post("/retry-recovery", status_code=status.HTTP_200_OK)
def trigger_dlq_retry_sweep():
    """Triggers self-healing retry sweep across pending DLQ records and re-publishes to Event Bus."""
    recovered = dlq_engine.retry_dead_letter_events()
    return {"status": "SUCCESS", "recovered_count": len(recovered), "recovered_events": recovered}
