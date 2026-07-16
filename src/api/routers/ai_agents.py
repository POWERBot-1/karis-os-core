from fastapi import APIRouter
from pydantic import BaseModel
from src.core.ai_gateway import ai_gateway

router = APIRouter(prefix="/api/v1/ai-agents", tags=["AI Orchestration & Multi-Agent Gateway"])

class RiskEvalRequest(BaseModel):
    borrower_identity_id: str
    requested_amount_kes: float
    historical_spend_kes: float

class DispatchOptRequest(BaseModel):
    pickup_address: str
    dropoff_address: str
    distance_km: float

class YieldForecastRequest(BaseModel):
    crop_type: str
    acreage: float
    county: str

@router.post("/evaluate-risk")
def evaluate_risk(req: RiskEvalRequest):
    return ai_gateway.evaluate_credit_risk(req.borrower_identity_id, req.requested_amount_kes, req.historical_spend_kes)

@router.post("/optimize-route")
def optimize_route(req: DispatchOptRequest):
    return ai_gateway.optimize_dispatch_route(req.pickup_address, req.dropoff_address, req.distance_km)

@router.post("/forecast-yield")
def forecast_yield(req: YieldForecastRequest):
    return ai_gateway.forecast_harvest_yield(req.crop_type, req.acreage, req.county)
