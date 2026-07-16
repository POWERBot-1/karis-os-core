from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.verticals.open_banking_cbdc.service import innovation_2_0_engine

router = APIRouter(prefix="/api/v1/innovation-2-0", tags=["KARIS OS 2.0 Vision (Section 48: CBDC, Open Banking, EAC & ESG)"])

class CbdcSettlementRequest(BaseModel):
    sender_institution_id: str
    recipient_institution_id: str
    amount: float
    cbdc_asset_code: str = "CBDC_KES"
    settlement_type: str = "WHOLESALE_INTERBANK"
    organization_id: str = "ORG-KARIS-RETAIL"

class OpenBankingConsentRequest(BaseModel):
    identity_id: str
    bank_institution_id: str
    bank_name: str
    account_masked: str
    consent_type: str = "ACCOUNT_INFORMATION_AIS"
    organization_id: str = "ORG-KARIS-RETAIL"

class CrossBorderRequest(BaseModel):
    sender_identity_id: str
    recipient_identity_id: str
    source_country: str = "KE"
    destination_country: str = "UG"
    source_currency: str = "KES"
    destination_currency: str = "UGX"
    source_amount: float = 10000.0
    organization_id: str = "ORG-KARIS-RETAIL"

class EsgCarbonRequest(BaseModel):
    organization_id: str
    target_resource_id: str
    target_resource_type: str = "PRODUCE_BATCH"
    scope_1_kg: float = 1.2
    scope_2_kg: float = 0.8
    scope_3_kg: float = 0.5

@router.post("/cbdc/settle", status_code=status.HTTP_200_OK)
def execute_cbdc(req: CbdcSettlementRequest):
    try:
        return innovation_2_0_engine.execute_cbdc_settlement(
            req.sender_institution_id, req.recipient_institution_id, req.amount,
            req.cbdc_asset_code, req.settlement_type, req.organization_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/open-banking/consent", status_code=status.HTTP_201_CREATED)
def grant_open_banking_consent(req: OpenBankingConsentRequest):
    return innovation_2_0_engine.grant_open_banking_consent(
        req.identity_id, req.bank_institution_id, req.bank_name, req.account_masked,
        req.consent_type, req.organization_id
    )

@router.post("/cross-border/initiate", status_code=status.HTTP_200_OK)
def initiate_cross_border(req: CrossBorderRequest):
    return innovation_2_0_engine.initiate_cross_border_eac_transfer(
        req.sender_identity_id, req.recipient_identity_id, req.source_country, req.destination_country,
        req.source_currency, req.destination_currency, req.source_amount, req.organization_id
    )

@router.post("/esg/record-carbon", status_code=status.HTTP_201_CREATED)
def record_esg_carbon(req: EsgCarbonRequest):
    return innovation_2_0_engine.record_esg_carbon_footprint(
        req.organization_id, req.target_resource_id, req.target_resource_type,
        req.scope_1_kg, req.scope_2_kg, req.scope_3_kg
    )
