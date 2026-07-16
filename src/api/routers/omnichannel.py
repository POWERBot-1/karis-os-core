from fastapi import APIRouter
from src.core.omnichannel_portal import omnichannel_portal_engine

router = APIRouter(prefix="/api/v1/omnichannel", tags=["Unified Super App & Merchant Portal Gateway (Section 31.2 & 31.3)"])

@router.get("/customer-super-app/{identity_id}")
def get_super_app_profile(identity_id: str, organization_id: str = "ORG-KARIS-RETAIL"):
    """Returns aggregated single-account profile across all 12 verticals (Wallets, Medical, Rides, Edu-Pay, Safaris)."""
    return omnichannel_portal_engine.get_unified_customer_super_app_profile(identity_id, organization_id)

@router.get("/merchant-portal/{organization_id}")
def get_merchant_portal(organization_id: str = "ORG-KARIS-RETAIL"):
    """Returns aggregated merchant inventory, pending KDS kitchen orders, and double-entry settlement connection status."""
    return omnichannel_portal_engine.get_unified_merchant_portal_dashboard(organization_id)
