from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.core.escrow_dispute import escrow_dispute_engine

router = APIRouter(prefix="/api/v1/commerce/escrow", tags=["Unified Escrow Clearing House & Dispute Resolution (Section 31.1 & 11.2)"])

class EscrowHoldRequest(BaseModel):
    order_id: str = "ORD-ESCROW-101"
    buyer_identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    seller_identity_id: str = "268e1e85-a0b3-445d-827b-98e327af3bee"
    amount_kes: float = 250000.0
    organization_id: str = "ORG-KARIS-FARM"

class DisputeResolveRequest(BaseModel):
    escrow_id: str
    dispute_reason: str = "PRODUCE_QUALITY_CLAIM"
    dispute_summary: str = "Received 500 KG Avocados, but 150 KG were bruised"
    seller_payout_pct: float = 60.0
    buyer_refund_pct: float = 40.0
    resolver_identity_id: str = "ADMIN-DISPUTE-01"

@router.post("/hold", status_code=status.HTTP_201_CREATED)
def hold_escrow(req: EscrowHoldRequest):
    return escrow_dispute_engine.hold_funds_in_escrow(
        req.order_id, req.buyer_identity_id, req.seller_identity_id, req.amount_kes, req.organization_id
    )

@router.post("/resolve-dispute", status_code=status.HTTP_200_OK)
def resolve_dispute(req: DisputeResolveRequest):
    try:
        return escrow_dispute_engine.raise_and_resolve_dispute(
            req.escrow_id, req.dispute_reason, req.dispute_summary, req.seller_payout_pct, req.buyer_refund_pct, req.resolver_identity_id
        )
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
