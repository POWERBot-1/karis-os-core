import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from pydantic import BaseModel

SECRET_KEY = "KARIS_OS_SUPER_SECURE_HMAC_SECRET_2026_ENTERPRISE_KEY"
TOKEN_EXPIRATION_MINUTES = 1440  # 24 hours

class TokenPayload(BaseModel):
    identity_id: str
    organization_id: str
    identity_type: str
    roles: list[str]
    exp: float
    iat: float

class AuthenticationEngine:
    """
    KARIS OS™ Authentication Engine (Section 38.2 & 7.5).
    Provides OTP generation/verification, cryptographic hashing, and stateless JWT token issuance.
    """
    def __init__(self):
        # In-memory OTP registry for active session simulation: phone -> (otp_code, expires_at)
        self.otp_registry: Dict[str, tuple[str, float]] = {}

    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        if not salt:
            salt = secrets.token_hex(16)
        # PBKDF2 HMAC SHA-256
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
        return key.hex(), salt

    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        computed_hash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, stored_hash)

    def generate_otp(self, phone_number: str) -> str:
        """Generates a 6-digit OTP for SMS/WhatsApp verification (valid for 5 minutes)."""
        otp_code = f"{secrets.randbelow(900000) + 100000:06d}"
        expires_at = time.time() + 300
        self.otp_registry[phone_number] = (otp_code, expires_at)
        return otp_code

    def verify_otp(self, phone_number: str, submitted_otp: str) -> bool:
        """Verifies active OTP code and clears it upon success."""
        if phone_number not in self.otp_registry:
            return False
        stored_otp, expires_at = self.otp_registry[phone_number]
        if time.time() > expires_at:
            del self.otp_registry[phone_number]
            return False
        if hmac.compare_digest(stored_otp, submitted_otp):
            del self.otp_registry[phone_number]
            return True
        return False

    def create_access_token(
        self,
        identity_id: str,
        organization_id: str,
        identity_type: str = "INDIVIDUAL",
        roles: Optional[list[str]] = None
    ) -> str:
        """Issues a signed JWT access token."""
        if roles is None:
            roles = ["USER"]
        now = time.time()
        payload = {
            "identity_id": identity_id,
            "organization_id": organization_id,
            "identity_type": identity_type,
            "roles": roles,
            "iat": now,
            "exp": now + (TOKEN_EXPIRATION_MINUTES * 60)
        }
        # Encode Header & Payload
        header = json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode("utf-8")
        payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        
        import base64
        b64_header = base64.urlsafe_b64encode(header).rstrip(b"=").decode("ascii")
        b64_payload = base64.urlsafe_b64encode(payload_bytes).rstrip(b"=").decode("ascii")
        
        signing_input = f"{b64_header}.{b64_payload}".encode("ascii")
        signature = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        b64_signature = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
        
        return f"{b64_header}.{b64_payload}.{b64_signature}"

    def decode_access_token(self, token: str) -> Optional[TokenPayload]:
        """Decodes and validates JWT token signature and expiration."""
        try:
            import base64
            parts = token.split(".")
            if len(parts) != 3:
                return None
            b64_header, b64_payload, b64_signature = parts
            
            signing_input = f"{b64_header}.{b64_payload}".encode("ascii")
            expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
            expected_b64_sig = base64.urlsafe_b64encode(expected_sig).rstrip(b"=").decode("ascii")
            
            if not hmac.compare_digest(b64_signature, expected_b64_sig):
                return None
                
            # Decode payload
            padding = "=" * (-len(b64_payload) % 4)
            payload_json = base64.urlsafe_b64decode(b64_payload + padding).decode("utf-8")
            data = json.loads(payload_json)
            
            if time.time() > data.get("exp", 0):
                return None
                
            return TokenPayload(**data)
        except Exception:
            return None

auth_engine = AuthenticationEngine()
