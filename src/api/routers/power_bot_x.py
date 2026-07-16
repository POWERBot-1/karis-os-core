import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.core.event_bus import event_bus, UniversalEventBus
from src.core.ledger_engine import ledger_engine, UniversalLedgerEngine
from src.core.wallet_engine import wallet_engine, MultiAssetWalletEngine
from src.verticals.power_bot_x.service import power_bot_x_service, PowerBotXService

router = APIRouter(prefix="/api/v1/power-bot-x", tags=["KARIS OS :: POWER BOT X (Section 49 - AI Prediction Economy)"])

def get_power_bot_service() -> PowerBotXService:
    return power_bot_x_service

class RegisterRequest(BaseModel):
    user_id: str
    phone_number: str
    discovery_channel: str = "WHATSAPP"
    referring_agent_id: Optional[str] = None

class CreateFixtureRequest(BaseModel):
    title: str
    category: str
    start_time_utc: str
    odds_or_confidence: str = "DERBY_HIGH_VOLATILITY"

class DepositRequest(BaseModel):
    user_id: str
    amount_kes: float
    mpesa_receipt_number: str
    treasury_reserve_wallet_id: str = "WALLET-TREASURY-KRT-RESERVE"

class PredictRequest(BaseModel):
    user_id: str
    fixture_id: str
    predicted_outcome: str
    stake_krt: float
    escrow_wallet_id: str = "WALLET-POWERBOT-ESCROW"
    league_id: Optional[str] = None

class SettleRequest(BaseModel):
    fixture_id: str
    settlement_outcome: str
    escrow_wallet_id: str = "WALLET-POWERBOT-ESCROW"
    agent_commission_pct: float = 10.0

class MerchantSpendRequest(BaseModel):
    user_id: str
    merchant_organization_id: str = "ORG-KARIS-EATERY-MAIN"
    merchant_krt_wallet_id: str = "WALLET-EATERY-KRT-MAIN"
    amount_krt: float
    vertical_target: str = "KARIS_EATERY"
    order_reference: str = "MEAL-001"

class AgentCampaignRequest(BaseModel):
    agent_user_id: str
    fixture_id: str
    preferred_language: str = "SWAHILI_SHENG"

@router.post("/register")
def register_user(req: RegisterRequest, svc: PowerBotXService = Depends(get_power_bot_service)):
    profile = svc.register_user(req.user_id, req.phone_number, req.discovery_channel, req.referring_agent_id)
    return {"status": "REGISTERED", "profile": profile.model_dump()}

@router.post("/fixtures")
def create_fixture(req: CreateFixtureRequest, svc: PowerBotXService = Depends(get_power_bot_service)):
    try:
        dt = datetime.fromisoformat(req.start_time_utc.replace("Z", "+00:00"))
    except Exception:
        dt = datetime.now(timezone.utc)
    fixture = svc.create_fixture(req.title, req.category, dt, req.odds_or_confidence)
    return {"status": "FIXTURE_CREATED", "fixture": fixture.model_dump()}

@router.get("/fixtures/{fixture_id}/copilot")
def get_ai_copilot_analysis(fixture_id: str, svc: PowerBotXService = Depends(get_power_bot_service)):
    if fixture_id not in svc.fixtures:
        raise HTTPException(status_code=404, detail="Fixture not found")
    fixture = svc.fixtures[fixture_id]
    analysis = svc.ai_copilot.analyze_fixture_form(fixture)
    return {"status": "SUCCESS", "ai_copilot_analysis": analysis}

@router.post("/deposit")
def process_deposit(req: DepositRequest, svc: PowerBotXService = Depends(get_power_bot_service)):
    try:
        result = svc.process_mpesa_deposit_and_mint_krt(req.user_id, req.amount_kes, req.mpesa_receipt_number, req.treasury_reserve_wallet_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/predict")
def submit_prediction(req: PredictRequest, svc: PowerBotXService = Depends(get_power_bot_service)):
    try:
        pred = svc.submit_prediction(req.user_id, req.fixture_id, req.predicted_outcome, req.stake_krt, req.escrow_wallet_id, req.league_id)
        return {"status": "PREDICTION_SUBMITTED", "prediction": pred.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/settle")
def settle_match(req: SettleRequest, svc: PowerBotXService = Depends(get_power_bot_service)):
    try:
        result = svc.settle_match_and_payout(req.fixture_id, req.settlement_outcome, req.escrow_wallet_id, req.agent_commission_pct)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/spend-merchant")
def spend_at_merchant(req: MerchantSpendRequest, svc: PowerBotXService = Depends(get_power_bot_service)):
    try:
        result = svc.redeem_krt_at_karis_merchant(req.user_id, req.merchant_organization_id, req.merchant_krt_wallet_id, req.amount_krt, req.vertical_target, req.order_reference)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/agent/campaign")
def generate_agent_campaign(req: AgentCampaignRequest, svc: PowerBotXService = Depends(get_power_bot_service)):
    if req.fixture_id not in svc.fixtures:
        raise HTTPException(status_code=404, detail="Fixture not found")
    fixture = svc.fixtures[req.fixture_id]
    campaign = svc.ai_copilot.generate_agent_campaign(req.agent_user_id, fixture, "WHATSAPP_STATUS", req.preferred_language)
    return {"status": "CAMPAIGN_GENERATED", "campaign": campaign.model_dump()}

@router.post("/whatsapp/status")
def generate_whatsapp_status(req: AgentCampaignRequest, svc: PowerBotXService = Depends(get_power_bot_service)):
    if req.fixture_id not in svc.fixtures:
        raise HTTPException(status_code=404, detail="Fixture not found")
    fixture = svc.fixtures[req.fixture_id]
    package = svc.whatsapp_experience.generate_whatsapp_status_package(fixture, req.agent_user_id, req.preferred_language)
    return {"status": "WHATSAPP_STATUS_PACKAGE_READY", "package": package}

@router.get("/digital-twin/simulate")
def simulate_digital_twin_policy(
    commission_pct: float = 15.0,
    staking_bonus_pct: float = 5.0,
    growth_multiplier: float = 1.35,
    svc: PowerBotXService = Depends(get_power_bot_service)
):
    snapshot = svc.digital_twin.generate_real_time_snapshot()
    sim = svc.digital_twin.simulate_policy_change(snapshot, commission_pct, staking_bonus_pct, growth_multiplier)
    return {"status": "SIMULATION_COMPLETED", "digital_twin_result": sim}
