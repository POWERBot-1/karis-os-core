"""
KARIS OS™ :: FastAPI Router for KARIS BorderX™ East African Customs & Trade Engine (`Section 58 / Vertical 23`).
Exposes endpoints for 9 Multi-Currency Wallets Onboarding, AI HS Classification, Smart Duty Calculator,
Customs Declaration & Settlement (`Rule 5 & Rule 9`), Trade Finance (`Rule 3`), Smart Border Queue, and Document AI.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.verticals.borderx.service import borderx_service, BorderXService

router = APIRouter(prefix="/api/v1/borderx", tags=["KARIS BorderX Customs & Trade Engine"])

def get_borderx_service() -> BorderXService:
    return borderx_service

# Request Schemas
class AccountOnboardRequest(BaseModel):
    identity_id: str
    entity_type: str = "IMPORTER"
    initial_kes: float = 1300000.0
    initial_usd: float = 10000.0
    initial_krt: float = 10000.0

class DeclarationFileRequest(BaseModel):
    trader_account_id: str
    agent_account_id: str
    declaration_type: str = "IMPORTS"
    origin_code: str = "CN"
    destination_code: str = "KE"
    border_post_code: str = "BUSIA_EAC"
    commodity_category: str = "ELECTRONICS"
    commodity_description: str = "Solar Inverter Components"
    cif_value_usd: float = 10000.0
    market_benchmark_cif_usd: float = 0.0

class DutyCalculateRequest(BaseModel):
    cif_value_usd: float
    hs_category: str = "ELECTRONICS"
    pay_fees_in_krt: bool = True
    krt_staking_discount_pct: float = 0.0

class DutySettleRequest(BaseModel):
    declaration_id: str
    pay_fees_in_krt: bool = True

class TradeFinanceApplyRequest(BaseModel):
    borrower_account_id: str
    facility_type: str = "WORKING_CAPITAL"
    requested_amount_usd: float = 25000.0
    cif_collateral_value_usd: float = 50000.0

class ShipmentDispatchRequest(BaseModel):
    declaration_id: str
    transporter_account_id: str
    transport_mode: str = "TRUCKS"
    container_number: str = "TEMU-882190-4"
    seal_number: str = "KRA-SEAL-2026-99"
    target_border_post: str = "BUSIA_EAC"

class DocumentGenerateRequest(BaseModel):
    declaration_id: str
    document_type: str = "COMMERCIAL_INVOICE"

class AITradeAssistantRequest(BaseModel):
    query_text: str = "How much duty for 500 bags of potatoes?"

# Endpoints
@router.post("/accounts/onboard", status_code=status.HTTP_201_CREATED)
def onboard_account(
    req: AccountOnboardRequest,
    service: BorderXService = Depends(get_borderx_service)
) -> Dict[str, Any]:
    try:
        acc = service.onboard_borderx_account(req.identity_id, req.entity_type, req.initial_kes, req.initial_usd, req.initial_krt)
        return {"status": "SUCCESS", "account": acc.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/accounts/{account_id}")
def get_account(
    account_id: str,
    service: BorderXService = Depends(get_borderx_service)
) -> Dict[str, Any]:
    if account_id not in service.accounts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BorderX Account not found.")
    return {"status": "SUCCESS", "account": service.accounts[account_id].model_dump()}

@router.post("/declarations/file", status_code=status.HTTP_201_CREATED)
def file_declaration(
    req: DeclarationFileRequest,
    service: BorderXService = Depends(get_borderx_service)
) -> Dict[str, Any]:
    try:
        decl = service.file_customs_declaration(
            req.trader_account_id, req.agent_account_id, req.declaration_type,
            req.origin_code, req.destination_code, req.border_post_code,
            req.commodity_category, req.commodity_description, req.cif_value_usd, req.market_benchmark_cif_usd
        )
        return {"status": "SUCCESS", "declaration": decl.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/declarations/calculate-duty")
def calculate_duty(
    req: DutyCalculateRequest,
    service: BorderXService = Depends(get_borderx_service)
) -> Dict[str, Any]:
    hs_spec = service.ai_engine.hs_catalog.get(req.hs_category.upper(), {"duty_pct": 25.0, "vat_pct": 16.0, "railway_levy_pct": 1.5, "idf_pct": 2.5, "rdl_pct": 1.5})
    res = service.duty_calculator.calculate_duty(
        cif_value_usd=req.cif_value_usd,
        duty_pct=hs_spec["duty_pct"],
        vat_pct=hs_spec["vat_pct"],
        railway_levy_pct=hs_spec["railway_levy_pct"],
        idf_pct=hs_spec["idf_pct"],
        rdl_pct=hs_spec["rdl_pct"],
        pay_fees_in_krt=req.pay_fees_in_krt,
        krt_staking_discount_pct=req.krt_staking_discount_pct
    )
    return {"status": "SUCCESS", "duty_breakdown": res}

@router.post("/declarations/settle-duty")
def settle_duty(
    req: DutySettleRequest,
    service: BorderXService = Depends(get_borderx_service)
) -> Dict[str, Any]:
    try:
        pmt = service.calculate_and_settle_duty(req.declaration_id, req.pay_fees_in_krt)
        return {"status": "SUCCESS", "duty_payment": pmt.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/finance/apply", status_code=status.HTTP_201_CREATED)
def apply_finance(
    req: TradeFinanceApplyRequest,
    service: BorderXService = Depends(get_borderx_service)
) -> Dict[str, Any]:
    try:
        fac = service.apply_for_trade_finance(req.borrower_account_id, req.facility_type, req.requested_amount_usd, req.cif_collateral_value_usd)
        return {"status": "SUCCESS", "trade_finance_facility": fac.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/logistics/dispatch", status_code=status.HTTP_201_CREATED)
def dispatch_shipment(
    req: ShipmentDispatchRequest,
    service: BorderXService = Depends(get_borderx_service)
) -> Dict[str, Any]:
    try:
        shp = service.dispatch_shipment_to_border(
            req.declaration_id, req.transporter_account_id, req.transport_mode,
            req.container_number, req.seal_number, req.target_border_post
        )
        return {"status": "SUCCESS", "shipment": shp.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/documents/generate", status_code=status.HTTP_201_CREATED)
def generate_document(
    req: DocumentGenerateRequest,
    service: BorderXService = Depends(get_borderx_service)
) -> Dict[str, Any]:
    try:
        doc = service.generate_digital_document(req.declaration_id, req.document_type)
        return {"status": "SUCCESS", "digital_document": doc.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/ai/trade-assistant")
def query_ai_assistant(
    req: AITradeAssistantRequest,
    service: BorderXService = Depends(get_borderx_service)
) -> Dict[str, Any]:
    res = service.ai_engine.ai_trade_assistant(req.query_text)
    return {"status": "SUCCESS", "ai_trade_advisory": res}
