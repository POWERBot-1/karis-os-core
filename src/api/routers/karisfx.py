"""
KARIS OS™ :: FastAPI Router for KARISFX™ Global Financial Ecosystem (`Section 56 / Vertical 21`).
Exposes endpoints for KRT Foundation onboarding, Multi-Asset trading across 16 asset classes,
13 AI Services, KRT Staking, Reward Engine, Strategy Marketplace, Governance, and Social Copy-Trading.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.verticals.karisfx.service import karisfx_service, KarisFXService

router = APIRouter(prefix="/api/v1/karisfx", tags=["KARISFX Global Financial Ecosystem"])

def get_karisfx_service() -> KarisFXService:
    return karisfx_service

# Request Schemas
class AccountOnboardRequest(BaseModel):
    identity_id: str
    full_name: str
    phone_number: str
    initial_krt_deposit: float = 1000.0
    initial_usd_deposit: float = 5000.0

class TradeExecuteRequest(BaseModel):
    account_id: str
    asset_class: str
    symbol: str
    side: str
    requested_units: float
    execution_price: float
    leverage: float = 1.0
    pay_fees_in_krt: bool = True

class StakingPositionRequest(BaseModel):
    account_id: str
    amount_krt: float
    lockup_duration_days: int = 90

class RewardClaimRequest(BaseModel):
    account_id: str
    activity_type: str
    custom_amount_krt: float = 0.0
    trade_holding_seconds: float = 3600.0

class AIQueryRequest(BaseModel):
    account_id: str
    service_name: str
    query_text: str
    portfolio_context: Optional[Dict[str, Any]] = None

class MarketplacePublishRequest(BaseModel):
    creator_account_id: str
    item_type: str
    title: str
    description: str
    price_krt: float
    historical_win_rate_pct: Optional[float] = None
    sharpe_ratio: Optional[float] = None

class MarketplacePurchaseRequest(BaseModel):
    buyer_account_id: str
    item_id: str

class GovernanceProposeRequest(BaseModel):
    creator_account_id: str
    category: str
    title: str
    description: str
    voting_days: int = 7

class GovernanceVoteRequest(BaseModel):
    voter_account_id: str
    proposal_id: str
    vote_choice: str

class SocialCopyLinkRequest(BaseModel):
    follower_account_id: str
    master_trader_account_id: str
    allocation_krt: float
    copy_ratio: float = 1.0

class DeveloperAppRegisterRequest(BaseModel):
    developer_account_id: str
    app_name: str
    app_type: str
    monetization_fee_krt_per_call: float = 1.0

# Endpoints
@router.post("/accounts/onboard", status_code=status.HTTP_201_CREATED)
def onboard_account(
    req: AccountOnboardRequest,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    try:
        acc = service.onboard_karisfx_account(
            req.identity_id, req.full_name, req.phone_number,
            req.initial_krt_deposit, req.initial_usd_deposit
        )
        return {"status": "SUCCESS", "account": acc.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/accounts/{account_id}")
def get_account(
    account_id: str,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    if account_id not in service.accounts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KARISFX Account not found.")
    return {"status": "SUCCESS", "account": service.accounts[account_id].model_dump()}

@router.post("/trade/execute", status_code=status.HTTP_201_CREATED)
def execute_trade(
    req: TradeExecuteRequest,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    try:
        trade = service.execute_multi_asset_trade(
            req.account_id, req.asset_class, req.symbol, req.side,
            req.requested_units, req.execution_price, req.leverage, req.pay_fees_in_krt
        )
        return {"status": "SUCCESS", "trade_execution": trade.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/staking/stake", status_code=status.HTTP_201_CREATED)
def open_staking(
    req: StakingPositionRequest,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    try:
        pos = service.open_staking_position(req.account_id, req.amount_krt, req.lockup_duration_days)
        return {"status": "SUCCESS", "staking_position": pos.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/rewards/claim")
def claim_reward(
    req: RewardClaimRequest,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    try:
        rew = service.claim_platform_reward(
            req.account_id, req.activity_type, req.custom_amount_krt, req.trade_holding_seconds
        )
        if rew.anti_abuse_status != "VERIFIED_CLEAN":
            return {"status": "REJECTED_ANTI_ABUSE", "reason": rew.anti_abuse_status, "reward_entry": rew.model_dump()}
        return {"status": "SUCCESS", "reward_entry": rew.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/ai/query")
def query_ai(
    req: AIQueryRequest,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    if req.account_id not in service.accounts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KARISFX Account not found.")
    acc = service.accounts[req.account_id]
    krt_w = service.wallet_engine.get_wallet(acc.krt_wallet_id)
    balance = krt_w.balance if krt_w else 0.0
    staked = service._get_staked_amount_for_account(req.account_id)

    try:
        res = service.ai_economy.query_ai_service(
            req.service_name, req.query_text, acc.account_tier, balance, staked, req.portfolio_context
        )
        return {"status": "SUCCESS", "ai_response": res}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/marketplace/publish", status_code=status.HTTP_201_CREATED)
def publish_item(
    req: MarketplacePublishRequest,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    try:
        item = service.publish_marketplace_item(
            req.creator_account_id, req.item_type, req.title, req.description,
            req.price_krt, req.historical_win_rate_pct, req.sharpe_ratio
        )
        return {"status": "SUCCESS", "marketplace_item": item.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/marketplace/purchase", status_code=status.HTTP_201_CREATED)
def purchase_item(
    req: MarketplacePurchaseRequest,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    try:
        purchase = service.purchase_marketplace_item(req.buyer_account_id, req.item_id)
        return {"status": "SUCCESS", "purchase_record": purchase.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/governance/propose", status_code=status.HTTP_201_CREATED)
def propose_governance(
    req: GovernanceProposeRequest,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    try:
        prop = service.create_governance_proposal(
            req.creator_account_id, req.category, req.title, req.description, req.voting_days
        )
        return {"status": "SUCCESS", "governance_proposal": prop.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/governance/vote", status_code=status.HTTP_201_CREATED)
def vote_governance(
    req: GovernanceVoteRequest,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    try:
        vote = service.cast_governance_vote(req.voter_account_id, req.proposal_id, req.vote_choice)
        return {"status": "SUCCESS", "governance_vote": vote.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/social/copy-trade", status_code=status.HTTP_201_CREATED)
def setup_copy_trade(
    req: SocialCopyLinkRequest,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    try:
        link = service.link_copy_trade(
            req.follower_account_id, req.master_trader_account_id, req.allocation_krt, req.copy_ratio
        )
        return {"status": "SUCCESS", "social_copy_link": link.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/developer/register-app", status_code=status.HTTP_201_CREATED)
def register_dev_app(
    req: DeveloperAppRegisterRequest,
    service: KarisFXService = Depends(get_karisfx_service)
) -> Dict[str, Any]:
    try:
        app = service.register_developer_app(
            req.developer_account_id, req.app_name, req.app_type, req.monetization_fee_krt_per_call
        )
        return {"status": "SUCCESS", "developer_app": app.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
