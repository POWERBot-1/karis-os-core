from typing import Dict, List
from fastapi import APIRouter, status
from pydantic import BaseModel
from src.core.offline_sync import offline_sync_engine

router = APIRouter(prefix="/api/v1/integrations/offline-sync", tags=["Mobile App & POS Offline Synchronization (Section 41.5)"])

class OfflineSyncRequest(BaseModel):
    device_terminal_code: str = "POS-MLO-01"
    offline_transactions: List[Dict] = [{"type": "POS_CHECKOUT", "amount_kes": 4500.0, "customer_id": "7f8013a9-310c-4f16-9031-295274a26944"}]
    cashier_identity_id: str = "268e1e85-a0b3-445d-827b-98e327af3bee"
    organization_id: str = "ORG-KARIS-RETAIL"

@router.post("/batch", status_code=status.HTTP_201_CREATED)
def sync_offline_batch(req: OfflineSyncRequest):
    """Synchronizes locally cached offline checkouts during M-Pesa/network interruptions (`Rule 5 & Rule 6`)."""
    return offline_sync_engine.synchronize_offline_batch(
        req.device_terminal_code, req.offline_transactions, req.cashier_identity_id, req.organization_id
    )
