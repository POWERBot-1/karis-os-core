from fastapi import APIRouter, status
from pydantic import BaseModel
from src.verticals.retail_pos.pos_ai import pos_ai_engine

router = APIRouter(prefix="/api/v1/retail-pos/ai", tags=["AI POS Queue Congestion & Shrinkage Monitor (Section 20.3 & 30.5)"])

class QueueMonitorRequest(BaseModel):
    store_id: str = "STORE-RETAIL-MLOLONGO-01"
    terminal_id: str = "POS-MLO-01"
    active_customers: int = 8
    wait_time_minutes: float = 5.5
    organization_id: str = "ORG-KARIS-RETAIL"

class ShrinkageAuditRequest(BaseModel):
    store_id: str = "STORE-RETAIL-MLOLONGO-01"
    product_id: str = "PROD-AVO-01"
    expected_qty: float = 300.0
    physical_qty: float = 285.0
    unit_price_kes: float = 150.0
    reason: str = "UNRECORDED_SPOILAGE"

@router.post("/queue-monitor", status_code=status.HTTP_201_CREATED)
def monitor_queue(req: QueueMonitorRequest):
    return pos_ai_engine.monitor_pos_queue(
        req.store_id, req.terminal_id, req.active_customers, req.wait_time_minutes, req.organization_id
    )

@router.post("/shrinkage-check", status_code=status.HTTP_201_CREATED)
def check_shrinkage(req: ShrinkageAuditRequest):
    return pos_ai_engine.audit_inventory_shrinkage(
        req.store_id, req.product_id, req.expected_qty, req.physical_qty, req.unit_price_kes, req.reason
    )
