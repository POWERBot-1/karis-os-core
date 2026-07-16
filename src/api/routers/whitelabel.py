from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List
from src.core.whitelabel_engine import whitelabel_engine

router = APIRouter(prefix="/api/v1/whitelabel", tags=["White-Label Customization & Multi-Tenant Branding (Section 35 / Frontier D)"])

class ApplyWhitelabelRequest(BaseModel):
    profile_code: str
    organization_id: str = "ORG-KARIS-RETAIL"
    actor_identity_id: str = "ADMIN-CFO-01"

@router.get("/profiles", status_code=status.HTTP_200_OK)
def get_profiles() -> List[Dict[str, Any]]:
    """Returns all available commercial white-label profiles (`Safaricom`, `Equity Bank`, `PalPlus`, `Default`)."""
    return whitelabel_engine.get_all_profiles()

@router.get("/active", status_code=status.HTTP_200_OK)
def get_active_profile() -> Dict[str, Any]:
    """Returns metadata for the active white-label branding profile currently running on KARIS OS."""
    return whitelabel_engine.get_active_profile()

@router.post("/apply", status_code=status.HTTP_200_OK)
def apply_profile(req: ApplyWhitelabelRequest) -> Dict[str, Any]:
    """Applies a white-label branding profile, dynamically modifying platform metadata and emitting `WHITELABEL_BRANDING_APPLIED` (`Rule 6 & 7`)."""
    try:
        return whitelabel_engine.apply_whitelabel_profile(
            profile_code=req.profile_code,
            organization_id=req.organization_id,
            actor_identity_id=req.actor_identity_id
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
