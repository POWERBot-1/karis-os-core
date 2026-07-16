from typing import Optional
from fastapi import APIRouter, status
from pydantic import BaseModel
from src.security.fraud_ai import fraud_ai_engine

router = APIRouter(prefix="/api/v1/security/fraud", tags=["AI Fraud Detection & Velocity Anomaly Engine (Section 38.6)"])

class FraudCheckRequest(BaseModel):
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    wallet_id: Optional[str] = None
    amount_kes: float = 15000.0
    device_fingerprint: str = "DEVICE-IP-192.168.1.10-CLEAN"
    location_gps: str = "-1.3564,36.9321"
    transaction_type: str = "M_PESA_CHECKOUT"
    organization_id: str = "ORG-KARIS-RETAIL"

@router.post("/evaluate", status_code=status.HTTP_200_OK)
def evaluate_fraud(req: FraudCheckRequest):
    """Evaluates transaction velocity, impossible travel (`Machakos -> Mombasa in 3 mins`), and blacklisted devices (`Rule 5`)."""
    return fraud_ai_engine.evaluate_transaction_fraud_risk(
        req.identity_id, req.wallet_id, req.amount_kes, req.device_fingerprint,
        req.location_gps, req.transaction_type, req.organization_id
    )
