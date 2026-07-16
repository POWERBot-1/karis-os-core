from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.security.hardware_hsm import hardware_hsm_engine

router = APIRouter(prefix="/api/v1/security/hsm", tags=["Mobile NFC Biometric Smart Terminal HSM Encryption Keys (Section 41.4 & 38.4)"])

class NfcTokenRequest(BaseModel):
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    wallet_id: str = "W-CUST-KES-01"
    authorized_amount_kes: float = 4500.0
    target_terminal_code: str = "POS-MLO-01"
    biometric_method: str = "FACE_ID_VERIFIED"
    organization_id: str = "ORG-KARIS-RETAIL"

class VerifyNfcRequest(BaseModel):
    nfc_cryptogram: str
    seller_identity_id: str = "268e1e85-a0b3-445d-827b-98e327af3bee"
    terminal_code: str = "POS-MLO-01"

@router.post("/generate-nfc-token", status_code=status.HTTP_201_CREATED)
def generate_nfc_token(req: NfcTokenRequest):
    try:
        return hardware_hsm_engine.generate_nfc_biometric_payment_token(
            req.identity_id, req.wallet_id, req.authorized_amount_kes,
            req.target_terminal_code, req.biometric_method, req.organization_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-payment", status_code=status.HTTP_200_OK)
def verify_nfc_payment(req: VerifyNfcRequest):
    try:
        return hardware_hsm_engine.verify_and_settle_nfc_token(
            req.nfc_cryptogram, req.seller_identity_id, req.terminal_code
        )
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
