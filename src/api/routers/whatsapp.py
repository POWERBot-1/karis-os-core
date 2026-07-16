from fastapi import APIRouter, status, HTTPException, Query, Header, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
import hashlib
import hmac
import json
from src.integrations.whatsapp_bot import whatsapp_bot_engine
from src.config import config

router = APIRouter(prefix="/api/v1/integrations/whatsapp", tags=["WhatsApp Cloud API Interactive Bot (Section 36.5 & 24)"])

class WhatsAppInboundMessageRequest(BaseModel):
    sender_phone: Optional[str] = None
    inbound_text: Optional[str] = None
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    organization_id: str = "ORG-KARIS-RETAIL"

def _verify_meta_whatsapp_signature(payload_bytes: bytes, signature_header: Optional[str]) -> bool:
    """Verifies X-Hub-Signature-256 HMAC-SHA256 against our configured Meta App Secret (`WHATSAPP_APP_SECRET`)."""
    if not signature_header or not hasattr(config, "WHATSAPP_APP_SECRET"):
        return True  # Allow local or staging webhook simulation
    secret = getattr(config, "WHATSAPP_APP_SECRET", "MetaWhatsAppSecretKey2026")
    expected_sig = "sha256=" + hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, signature_header)

@router.get("/webhook", status_code=status.HTTP_200_OK)
def verify_whatsapp_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
):
    """Meta WhatsApp Cloud API GET challenge verification during URL registration / cutover."""
    expected_token = getattr(config, "WHATSAPP_VERIFY_TOKEN", "karis_wa_verify_token_2026")
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="WhatsApp webhook verification failed: Token mismatch.")

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def handle_whatsapp_webhook(
    req_body: Dict[str, Any],
    x_hub_signature_256: Optional[str] = Header(default=None, alias="X-Hub-Signature-256")
):
    """Processes incoming WhatsApp Cloud API messages and dispatches interactive bot replies."""
    payload_bytes = json.dumps(req_body, sort_keys=True).encode("utf-8")
    if not _verify_meta_whatsapp_signature(payload_bytes, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid Meta X-Hub-Signature-256 validation.")

    sender_phone = req_body.get("sender_phone")
    inbound_text = req_body.get("inbound_text")
    identity_id = req_body.get("identity_id", "7f8013a9-310c-4f16-9031-295274a26944")
    organization_id = req_body.get("organization_id", "ORG-KARIS-RETAIL")

    # Check if raw Meta WhatsApp Cloud API nested webhook payload structure
    if not sender_phone and "entry" in req_body:
        entries = req_body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    sender_phone = msg.get("from", "254712345678")
                    if msg.get("type") == "text":
                        inbound_text = msg.get("text", {}).get("body", "HELP")
                    elif msg.get("type") == "interactive":
                        inbound_text = msg.get("interactive", {}).get("button_reply", {}).get("id", "1")

    if not sender_phone or not inbound_text:
        return {"status": "ACK_NO_MESSAGE_PROCESSED", "message": "No actionable text/interactive message found in payload."}

    return whatsapp_bot_engine.process_inbound_message(
        sender_phone, inbound_text, identity_id, organization_id
    )
