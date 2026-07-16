from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.verticals.loyalty.network_tier_engine import loyalty_network_engine

router = APIRouter(prefix="/api/v1/loyalty", tags=["Loyalty Tiers & Cross-Merchant Network Clearing (Section 23.2 & 18)"])

class TierEvalRequest(BaseModel):
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    total_lifetime_spend_kes: float = 125000.0
    krt_balance: float = 450.0
    organization_id: str = "ORG-KARIS-RETAIL"

class CrossRedeemRequest(BaseModel):
    customer_identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    source_organization_id: str = "ORG-KARIS-FARM"
    target_organization_id: str = "ORG-KARIS-EATERY"
    krt_tokens_redeemed: float = 150.0

@router.post("/tiers/evaluate-upgrade", status_code=status.HTTP_200_OK)
def evaluate_tier(req: TierEvalRequest):
    return loyalty_network_engine.evaluate_and_upgrade_customer_tier(
        req.identity_id, req.total_lifetime_spend_kes, req.krt_balance, req.organization_id
    )

@router.post("/network/cross-merchant-redeem", status_code=status.HTTP_201_CREATED)
def cross_merchant_redeem(req: CrossRedeemRequest):
    try:
        return loyalty_network_engine.execute_cross_merchant_network_redemption(
            req.customer_identity_id, req.source_organization_id, req.target_organization_id, req.krt_tokens_redeemed
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
