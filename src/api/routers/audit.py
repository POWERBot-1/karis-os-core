from fastapi import APIRouter
from src.security.audit import audit_engine

router = APIRouter(prefix="/api/v1/audit", tags=["Cryptographic Audit Verification (Section 38.5 & Rule 9)"])

@router.get("/verify-ledger")
def verify_ledger():
    """Scans the Universal Double-Entry Ledger and verifies 100% unbroken SHA-256 hash chaining."""
    return audit_engine.verify_ledger_chain()

@router.get("/verify-events")
def verify_events():
    """Scans the Universal Event Store and verifies tamper-evidence across all published events."""
    return audit_engine.verify_event_store_integrity()
