from fastapi import APIRouter, status
from pydantic import BaseModel
from src.integrations.mobile_passkey_push import mobile_passkey_push_engine

router = APIRouter(prefix="/api/v1/mobile", tags=["Mobile Super App Passkeys, Biometrics & Push (Section 41.2 & 26.5)"])

class PasskeyVerifyRequest(BaseModel):
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    organization_id: str = "ORG-KARIS-RETAIL"
    platform: str = "IOS_APPLE_SECURE_ENCLAVE"
    credential_id: str = "PASSKEY-CRED-2026-89A1B2C3"

class RegisterPushDeviceRequest(BaseModel):
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    token: str = "FCM-TOKEN-AMINA-01"
    platform: str = "ANDROID_FCM"
    model: str = "Samsung Galaxy S24 Ultra"
    role: str = "CUSTOMER"

@router.post("/passkeys/verify-challenge", status_code=status.HTTP_200_OK)
def verify_passkey(req: PasskeyVerifyRequest):
    """Verifies cryptographic FIDO2 passkey challenge and checks gamified 250 KRT Security Champion bonus (`Rule 6`)."""
    return mobile_passkey_push_engine.execute_mobile_passkey_challenge_and_bonus(
        req.identity_id, req.organization_id, req.platform, req.credential_id
    )

@router.post("/push/register-device", status_code=status.HTTP_201_CREATED)
def register_push_device(req: RegisterPushDeviceRequest):
    return mobile_passkey_push_engine.register_push_device(
        req.identity_id, req.token, req.platform, req.model, req.role
    )
