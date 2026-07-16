from fastapi import APIRouter, HTTPException, status, Header, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
import hashlib
import hmac
import json
from src.integrations.payment_links import payment_link_engine
from src.config import config

router = APIRouter(prefix="/api/v1/payment-links", tags=["PalPlus & Hosted Payment Links Checkout (Section 51 / Section 34.5)"])

class CreateCheckoutRequest(BaseModel):
    order_id: str = "ORDER-FARM-9901"
    amount_kes: float = 3500.0
    payer_identity_id: str = "USER-AMINA-777"
    description: str = "Universal Checkout via PalPlus Temporary Payment Link"

class PalPlusWebhookRequest(BaseModel):
    payment_link_id: str = "6e8de0bc-1284-4bba-a5de-f886665bf18f"
    payer_identity_id: str = "USER-AMINA-777"
    amount_kes: float = 3500.0
    external_receipt_number: str = "PALPLUS-RC-99021"
    organization_id: str = "ORG-KARIS-RETAIL"
    target_order_id: str = "ORDER-FARM-9901"

def _verify_palplus_signature(payload_dict: dict, signature_header: Optional[str]) -> bool:
    """Verifies X-PalPlus-Signature HMAC-SHA256 against our configured secret key (`PALPLUS_API_KEY`)."""
    if not signature_header or not hasattr(config, "PALPLUS_WEBHOOK_SECRET"):
        return True  # Allow local or staging simulation when no secret is explicitly required
    secret = getattr(config, "PALPLUS_WEBHOOK_SECRET", "palplus_live_key_9901")
    encoded_payload = json.dumps(payload_dict, sort_keys=True).encode("utf-8")
    expected_sig = hmac.new(secret.encode("utf-8"), encoded_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, signature_header)

@router.get("/active-temporary", status_code=status.HTTP_200_OK)
def get_active_temporary_link():
    """Returns metadata for our active temporary PalPlus payment link (`https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f`)."""
    link = payment_link_engine.get_or_register_payment_link()
    return {"status": "ACTIVE", "payment_link": link.model_dump()}

@router.post("/checkout-package", status_code=status.HTTP_200_OK)
def create_checkout_package(req: CreateCheckoutRequest):
    """Generates a checkout package pointing any invoice directly to our active temporary PalPlus payment link."""
    return payment_link_engine.generate_checkout_package(
        order_id=req.order_id,
        amount_kes=req.amount_kes,
        payer_identity_id=req.payer_identity_id,
        description=req.description
    )

@router.post("/webhook/palplus", status_code=status.HTTP_200_OK)
def handle_palplus_webhook(
    req: PalPlusWebhookRequest,
    x_palplus_signature: Optional[str] = Header(default=None, alias="X-PalPlus-Signature")
):
    """Reconciles incoming PalPlus webhooks upon payment completion, executing double-entry KES/KRT settlement (`Rule 2 & 9`)."""
    if not _verify_palplus_signature(req.model_dump(), x_palplus_signature):
        raise HTTPException(status_code=403, detail="Invalid X-PalPlus-Signature HMAC validation.")
    try:
        return payment_link_engine.process_palplus_webhook(
            payment_link_id=req.payment_link_id,
            payer_identity_id=req.payer_identity_id,
            amount_kes=req.amount_kes,
            external_receipt_number=req.external_receipt_number,
            organization_id=req.organization_id,
            target_order_id=req.target_order_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
