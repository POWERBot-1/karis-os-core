from fastapi import APIRouter, status
from pydantic import BaseModel
from src.security.regulatory_reporting import regulatory_compliance_engine

router = APIRouter(prefix="/api/v1/governance/regulatory", tags=["Automated Regulatory Compliance & Multi-Jurisdictional Reporting (Section 35.4 & 38.8)"])

class RegulatoryReportRequest(BaseModel):
    jurisdiction_code: str = "KE"
    report_type: str = "CENTRAL_BANK_AML_FIU_SUMMARY"
    organization_id: str = "ORG-KARIS-RETAIL"
    generator_identity_id: str = "SYSTEM_COMPLIANCE_OFFICER"

@router.post("/generate-report", status_code=status.HTTP_201_CREATED)
def generate_regulatory_report(req: RegulatoryReportRequest):
    """Compiles verifiable inspection reports across multi-tier KYC, AML SARs, eTIMS tax invoices, and double-entry transfers."""
    return regulatory_compliance_engine.generate_jurisdictional_regulatory_report(
        req.jurisdiction_code, req.report_type, req.organization_id, req.generator_identity_id
    )
