from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.verticals.healthcare.ambulance_ai import ambulance_ai_engine

router = APIRouter(prefix="/api/v1/healthcare/ambulance", tags=["Life-Support Emergency Ambulance Dispatch (Section 32.8 & 33.5)"])

class AmbulanceDispatchRequest(BaseModel):
    pickup_gps: str = "-1.3650,36.9350"
    required_tier: str = "ADVANCED_LIFE_SUPPORT_ALS"
    organization_id: str = "ORG-KARIS-HEALTH"

@router.post("/dispatch", status_code=status.HTTP_201_CREATED)
def dispatch_ambulance(req: AmbulanceDispatchRequest):
    try:
        return ambulance_ai_engine.dispatch_nearest_emergency_unit(
            req.pickup_gps, req.required_tier, req.organization_id
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
