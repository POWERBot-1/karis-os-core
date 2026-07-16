from fastapi import APIRouter, status
from pydantic import BaseModel
from src.observability.ledger_reconciliation import ledger_reconciliation_engine

router = APIRouter(prefix="/api/v1/observability/ledger", tags=["Universal Double-Entry Ledger Reconciliation Sweeps (Section 37.4 & 10.4)"])

class LedgerReconRequest(BaseModel):
    organization_id: str = "ORG-KARIS-RETAIL"

@router.post("/reconciliation-sweep", status_code=status.HTTP_200_OK)
def run_ledger_recon_sweep(req: LedgerReconRequest):
    """Sweeps all multi-asset wallets against exact double-entry sums. Corrects drift via cryptographic Reversing Entries (`Rule 9`)."""
    return ledger_reconciliation_engine.execute_automated_ledger_reconciliation_sweep(req.organization_id)
