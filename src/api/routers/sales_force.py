from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.verticals.sales_force.service import sales_force_engine

router = APIRouter(prefix="/api/v1/sales-force", tags=["Sales Force Automation Engine (Section 22)"])

class RegisterAgentRequest(BaseModel):
    identity_id: str
    organization_id: str
    agent_code: str
    territory: str = "Machakos County - Mlolongo Ward"

class LogVisitRequest(BaseModel):
    agent_id: str
    organization_id: str
    customer_identity_id: str
    visit_type: str = "FARMER_ONBOARDING"
    notes: str = "Onboarded avocado farmer successfully"

class RegisterReferralRequest(BaseModel):
    agent_id: str
    referred_identity_id: str
    organization_id: str
    referral_code: str

class ConvertReferralRequest(BaseModel):
    referral_code: str
    first_order_kes: float = 3000.0

@router.post("/agents", status_code=status.HTTP_201_CREATED)
def register_agent(req: RegisterAgentRequest):
    return sales_force_engine.register_sales_agent(req.identity_id, req.organization_id, req.agent_code, req.territory)

@router.post("/visits", status_code=status.HTTP_201_CREATED)
def log_visit(req: LogVisitRequest):
    try:
        return sales_force_engine.log_sales_visit(req.agent_id, req.organization_id, req.customer_identity_id, req.visit_type, req.notes)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/referrals", status_code=status.HTTP_201_CREATED)
def register_referral(req: RegisterReferralRequest):
    try:
        return sales_force_engine.register_referral(req.agent_id, req.referred_identity_id, req.organization_id, req.referral_code)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/referrals/convert", status_code=status.HTTP_200_OK)
def convert_referral(req: ConvertReferralRequest):
    try:
        return sales_force_engine.convert_referral(req.referral_code, req.first_order_kes)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
