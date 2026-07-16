from typing import Dict, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.security.policy_control import operational_policy_engine

router = APIRouter(prefix="/api/v1/governance/controls", tags=["Operational Governance Policies, API Keys & Tax Rules (Section 43 & 47)"])

class CreatePolicyRequest(BaseModel):
    organization_id: str = "ORG-KARIS-RETAIL"
    code: str = "POL-GOV-RESERVE-RATIO-20PCT"
    name: str = "Treasury Liquidity Reserve Backing"
    category: str = "TREASURY_LIQUIDITY_RESERVE"
    params_json: str = '{"min_fiat_backing_pct": 20.0}'
    enforcement_mode: str = "STRICT_BLOCKING"

class IssueKeyRequest(BaseModel):
    identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    organization_id: str = "ORG-KARIS-RETAIL"
    key_name: str = "Machakos Supermarket POS Terminal Key"
    scopes: List[str] = ["ORDERS:WRITE", "LEDGER:READ", "TRACEABILITY:READ"]

class RevokeKeyRequest(BaseModel):
    key_id: str
    revoker_identity_id: str = "ADMIN-01"

class CreateTaxRuleRequest(BaseModel):
    organization_id: str = "ORG-KARIS-RETAIL"
    jurisdiction: str = "KE"
    code: str = "TAX-KE-VAT-16"
    name: str = "Kenya Standard VAT"
    rate_pct: float = 16.0
    is_withholding: bool = False

@router.get("/policies", response_model=List[Dict])
def get_policies():
    return list(operational_policy_engine.policies.values())

@router.post("/policies", status_code=status.HTTP_201_CREATED)
def create_policy(req: CreatePolicyRequest):
    return operational_policy_engine.create_governance_policy(
        req.organization_id, req.code, req.name, req.category, req.params_json, req.enforcement_mode
    )

@router.get("/api-keys", response_model=List[Dict])
def get_api_keys():
    return [
        {k: v for k, v in rec.items() if k != "raw_api_secret_once"}
        for rec in operational_policy_engine.api_keys.values()
    ]

@router.post("/api-keys", status_code=status.HTTP_201_CREATED)
def issue_api_key(req: IssueKeyRequest):
    """Issues cryptographic enterprise API key (`KARIS_LIVE_...`) with SHA-256 secret hashing (`Section 38.4`)."""
    return operational_policy_engine.issue_api_key(req.identity_id, req.organization_id, req.key_name, req.scopes)

@router.post("/api-keys/revoke", status_code=status.HTTP_200_OK)
def revoke_api_key(req: RevokeKeyRequest):
    try:
        return operational_policy_engine.revoke_api_key(req.key_id, req.revoker_identity_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/tax-rules", response_model=List[Dict])
def get_tax_rules():
    return list(operational_policy_engine.tax_rules.values())

@router.post("/tax-rules", status_code=status.HTTP_201_CREATED)
def create_tax_rule(req: CreateTaxRuleRequest):
    return operational_policy_engine.create_tax_rule(
        req.organization_id, req.jurisdiction, req.code, req.name, req.rate_pct, req.is_withholding
    )
