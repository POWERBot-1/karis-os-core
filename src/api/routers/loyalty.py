from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.verticals.loyalty.service import loyalty_engine

router = APIRouter(prefix="/api/v1/loyalty", tags=["Loyalty & Incentive Engine (Section 26)"])

class CreateCampaignRequest(BaseModel):
    organization_id: str
    campaign_code: str
    campaign_name: str
    target_stakeholder: str = "ALL"
    reward_type: str = "KARIS_TOKENS_KRT"
    multiplier: float = 2.0
    fixed_bonus: float = 50.0

class GrantRewardRequest(BaseModel):
    campaign_id: str
    recipient_identity_id: str
    organization_id: str
    trigger_reason: str
    base_amount: float = 100.0

@router.post("/campaigns", status_code=status.HTTP_201_CREATED)
def create_campaign(req: CreateCampaignRequest):
    return loyalty_engine.create_campaign(
        req.organization_id, req.campaign_code, req.campaign_name,
        req.target_stakeholder, req.reward_type, req.multiplier, req.fixed_bonus
    )

@router.post("/rewards/grant", status_code=status.HTTP_200_OK)
def grant_reward(req: GrantRewardRequest):
    try:
        return loyalty_engine.grant_campaign_reward(
            req.campaign_id, req.recipient_identity_id, req.organization_id, req.trigger_reason, req.base_amount
        )
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
