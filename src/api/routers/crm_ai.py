from fastapi import APIRouter, status
from pydantic import BaseModel
from src.ai.crm_intelligence import crm_ai_engine

router = APIRouter(prefix="/api/v1/crm/ai", tags=["AI CRM Churn Prediction & Retention Campaign Engine (Section 23.4)"])

class CrmEvaluationRequest(BaseModel):
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    historical_spend_kes: float = 125000.0
    purchase_frequency_days: float = 95.0
    organization_id: str = "ORG-KARIS-RETAIL"
    customer_name: str = "Amina Wanjiku"

class TriggerRetentionRequest(BaseModel):
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    organization_id: str = "ORG-KARIS-RETAIL"
    customer_name: str = "Amina Wanjiku"
    bonus_tokens: float = 500.0

@router.post("/evaluate-ltv-churn", status_code=status.HTTP_201_CREATED)
def evaluate_ltv_churn(req: CrmEvaluationRequest):
    return crm_ai_engine.evaluate_customer_ltv_and_churn(
        req.identity_id, req.historical_spend_kes, req.purchase_frequency_days, req.organization_id, req.customer_name
    )

@router.post("/trigger-retention-grant", status_code=status.HTTP_201_CREATED)
def trigger_retention(req: TriggerRetentionRequest):
    return crm_ai_engine.execute_automated_retention_campaign(
        req.identity_id, req.organization_id, req.customer_name, req.bonus_tokens
    )
