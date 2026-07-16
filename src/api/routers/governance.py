from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.security.governance_compliance import governance_engine

router = APIRouter(prefix="/api/v1/governance", tags=["Operational Governance, AML/KYC & KRA Tax Invoices (Section 38.8 & 47)"])

class KycVerifyRequest(BaseModel):
    identity_id: str
    organization_id: str = "ORG-KARIS-RETAIL"
    national_id: str
    kra_pin: str
    tier: str = "TIER_2_STANDARD"

class AmlCheckRequest(BaseModel):
    identity_id: str
    organization_id: str = "ORG-KARIS-RETAIL"
    amount_kes: float
    transaction_type: str = "M_PESA_CHECKOUT"

class KraInvoiceRequest(BaseModel):
    organization_id: str = "ORG-KARIS-RETAIL"
    order_id: str
    buyer_identity_id: str
    seller_identity_id: str
    seller_kra_pin: str
    taxable_amount_kes: float

@router.post("/kyc/verify", status_code=status.HTTP_201_CREATED)
def complete_kyc(req: KycVerifyRequest):
    return governance_engine.complete_kyc_verification(
        req.identity_id, req.organization_id, req.national_id, req.kra_pin, req.tier
    )

@router.post("/aml/check", status_code=status.HTTP_200_OK)
def check_aml(req: AmlCheckRequest):
    return governance_engine.check_aml_transaction_velocity(
        req.identity_id, req.organization_id, req.amount_kes, req.transaction_type
    )

@router.post("/kra/etims/issue", status_code=status.HTTP_201_CREATED)
def issue_etims_invoice(req: KraInvoiceRequest):
    return governance_engine.issue_kra_etims_tax_invoice(
        req.organization_id, req.order_id, req.buyer_identity_id, req.seller_identity_id,
        req.seller_kra_pin, req.taxable_amount_kes
    )
