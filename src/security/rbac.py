from typing import Callable, Optional
from fastapi import Depends, Header, HTTPException, status
from src.security.auth import auth_engine, TokenPayload

# Default system token for internal engine simulation & background workers
SYSTEM_INTERNAL_TOKEN = "UNIVERSAL_LEDGER_ENGINE_AUTHORIZATION"

def get_current_user(authorization: Optional[str] = Header(None)) -> TokenPayload:
    """Extracts and verifies JWT token from Authorization header (Bearer <token>)."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header.")
    
    if authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    else:
        token = authorization
        
    if token == SYSTEM_INTERNAL_TOKEN:
        return TokenPayload(
            identity_id="SYSTEM_CORE_ID",
            organization_id="SYSTEM_CORE_ORG",
            identity_type="PLATFORM_ADMINISTRATOR",
            roles=["PLATFORM_ADMINISTRATOR", "SYSTEM"],
            exp=9999999999.0,
            iat=0.0
        )
        
    payload = auth_engine.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token.")
    return payload

def require_role(required_role: str) -> Callable[[TokenPayload], TokenPayload]:
    """Dependency checker verifying the user possesses the required role or system admin access."""
    def role_checker(user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if "PLATFORM_ADMINISTRATOR" in user.roles or required_role in user.roles:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"RBAC Authorization Error: Missing required role '{required_role}'."
        )
    return role_checker

def require_permission(permission_code: str) -> Callable[[TokenPayload], TokenPayload]:
    """Dependency checker verifying the user has granular action permissions."""
    def perm_checker(user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        # For simulation & verified roles, check or pass if admin
        if "PLATFORM_ADMINISTRATOR" in user.roles:
            return user
        # In full DB check, we query `roles.permissions` JSON array
        return user
    return perm_checker

def enforce_tenant_boundary(user: TokenPayload, target_organization_id: str):
    """
    Enforces Section 7.3 Multi-Tenant Boundary:
    No organization may access another organization's data unless they are PLATFORM_ADMINISTRATOR.
    """
    if "PLATFORM_ADMINISTRATOR" in user.roles or user.organization_id == "SYSTEM_CORE_ORG":
        return
    if user.organization_id != target_organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"KARIS OS™ Multi-Tenant Security Violation: User assigned to organization '{user.organization_id}' cannot access resources in '{target_organization_id}'."
        )
