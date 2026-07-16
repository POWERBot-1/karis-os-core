from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.security.auth import auth_engine

router = APIRouter(prefix="/api/v1/auth", tags=["Security & MFA/OTP Authentication (Section 38)"])

class GenerateOtpRequest(BaseModel):
    phone_number: str

class VerifyOtpRequest(BaseModel):
    phone_number: str
    otp_code: str
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    organization_id: str = "ORG-KARIS-RETAIL"
    roles: Optional[list[str]] = ["USER", "CUSTOMER"]

@router.post("/otp/generate", status_code=status.HTTP_200_OK)
def generate_otp(req: GenerateOtpRequest):
    """Generates a 6-digit OTP code for mobile SMS / WhatsApp verification."""
    otp = auth_engine.generate_otp(req.phone_number)
    return {"status": "SUCCESS", "phone_number": req.phone_number, "otp_code": otp, "expires_in_seconds": 300}

@router.post("/otp/verify", status_code=status.HTTP_200_OK)
def verify_otp_and_login(req: VerifyOtpRequest):
    """Verifies submitted OTP and returns a cryptographically signed JWT Access Token."""
    is_valid = auth_engine.verify_otp(req.phone_number, req.otp_code)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP code.")
    
    token = auth_engine.create_access_token(req.identity_id, req.organization_id, roles=req.roles)
    return {
        "status": "SUCCESS",
        "access_token": token,
        "token_type": "Bearer",
        "expires_in_minutes": 1440,
        "identity_id": req.identity_id,
        "organization_id": req.organization_id,
        "roles": req.roles
    }
