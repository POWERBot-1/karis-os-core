from fastapi import APIRouter, status
from pydantic import BaseModel
from src.observability.chaos_engine import chaos_engine

router = APIRouter(prefix="/api/v1/observability/chaos", tags=["Chaos Engineering & Fault Injection Resilience Suite (Section 44.2 & 40.7)"])

class ChaosDrillRequest(BaseModel):
    fault_type: str = "SIMULATED_DATABASE_SLAVE_DISCONNECT"
    target_component: str = "UNIVERSAL_LEDGER_ENGINE"
    concurrent_transactions: int = 20
    organization_id: str = "ORG-KARIS-RETAIL"

@router.post("/inject-drill", status_code=status.HTTP_201_CREATED)
def trigger_chaos_drill(req: ChaosDrillRequest):
    """Executes controlled fault injection disaster drill verifying DLQ self-healing & zero ledger corruption (`Rule 9`)."""
    return chaos_engine.run_automated_chaos_resilience_drill(
        req.fault_type, req.target_component, req.concurrent_transactions, req.organization_id
    )
