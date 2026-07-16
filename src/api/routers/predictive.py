from fastapi import APIRouter, status
from pydantic import BaseModel
from src.ai.predictive_intelligence import predictive_engine

router = APIRouter(prefix="/api/v1/predictive", tags=["Predictive Intelligence & Demand Forecasting (Section 27.4)"])

class DemandForecastRequest(BaseModel):
    organization_id: str = "ORG-KARIS-RETAIL"
    product_id: str
    branch_store_id: str = "STORE-RETAIL-MLOLONGO-01"
    daily_sales_velocity: float = 45.0
    current_shelf_quantity: float = 300.0

class DynamicPricingRequest(BaseModel):
    organization_id: str = "ORG-KARIS-RETAIL"
    product_id: str
    current_price_kes: float = 150.0
    trigger_factor: str = "SHELF_EXPIRY_APPROACHING"

@router.post("/demand-forecast", status_code=status.HTTP_201_CREATED)
def generate_forecast(req: DemandForecastRequest):
    return predictive_engine.generate_demand_forecast(
        req.organization_id, req.product_id, req.branch_store_id, req.daily_sales_velocity, req.current_shelf_quantity
    )

@router.post("/dynamic-pricing", status_code=status.HTTP_201_CREATED)
def recommend_pricing(req: DynamicPricingRequest):
    return predictive_engine.recommend_dynamic_pricing(
        req.organization_id, req.product_id, req.current_price_kes, req.trigger_factor
    )
