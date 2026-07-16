from fastapi import APIRouter, status
from pydantic import BaseModel
from src.security.privacy_engine import privacy_gdpr_engine

router = APIRouter(prefix="/api/v1/security/privacy", tags=["Enterprise Privacy Controls, Consent, Data Export & GDPR/DPA (Section 38.7)"])

class UpdateConsentRequest(BaseModel):
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    organization_id: str = "ORG-KARIS-RETAIL"
    category: str = "MARKETING_COMMUNICATIONS"
    is_granted: bool = True

class AnonymizeRequest(BaseModel):
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    reason: str = "KENYA_DPA_DELETION_REQUEST"
    executor_id: str = "ADMIN-PRIVACY-01"
    organization_id: str = "ORG-KARIS-RETAIL"

@router.post("/consents", status_code=status.HTTP_201_CREATED)
def update_consent(req: UpdateConsentRequest):
    return privacy_gdpr_engine.update_privacy_consent(
        req.identity_id, req.organization_id, req.category, req.is_granted
    )

@router.get("/export/{identity_id}")
def export_data(identity_id: str, organization_id: str = "ORG-KARIS-RETAIL"):
    """Section 38.7 Data Export: Compiles complete structured JSON personal data across all 12 verticals."""
    return privacy_gdpr_engine.export_customer_personal_data(identity_id, organization_id)

@router.post("/anonymize", status_code=status.HTTP_200_OK)
def anonymize_user(req: AnonymizeRequest):
    """Executes Kenya DPA / GDPR right-to-be-forgotten anonymization while preserving double-entry ledger SHA-256 integrity (`Rule 9`)."""
    return privacy_gdpr_engine.execute_right_to_be_forgotten_anonymization(
        req.identity_id, req.reason, req.executor_id, req.organization_id
    )
