from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.verticals.karis_expansion_suite.service import expansion_suite_service, KarisExpansionSuiteService

router = APIRouter(prefix="/api/v1/expansion-suite", tags=["KARIS INNOVATION EXPANSION SUITE: Pharma / Prop-Share / Edu-Pay (Section 52)"])

def get_expsuite_service() -> KarisExpansionSuiteService:
    return expansion_suite_service

class LogPharmaBatchRequest(BaseModel):
    product_id: str
    organization_id: str = "ORG-HEALTH-CLINIC"
    storage_min: float = 2.0
    storage_max: float = 8.0

class LogPharmaTelemetryRequest(BaseModel):
    batch_id: str
    temperature_celsius: float
    humidity_pct: float = 55.0
    gps_location: str = "(-1.3850, 36.9400)"

class CreateSyndicationRequest(BaseModel):
    organization_id: str = "ORG-KARIS-PROP"
    title: str = "Machakos Commercial Hub"
    location: str = "Machakos County"
    total_shares: int = 1000
    share_price_kes: float = 10000.0

class AllocateSharesRequest(BaseModel):
    syndication_id: str
    investor_id: str
    shares: int

class DistributeDividendsRequest(BaseModel):
    syndication_id: str
    total_rental_pool_krt: float

class CreateTuitionPlanRequest(BaseModel):
    student_id: str
    institution_org_id: str = "ORG-COLLEGE-MACHAKOS"
    term: str = "Term 3 2026"
    total_tuition_kes: float = 45000.0

class PayTuitionRequest(BaseModel):
    plan_id: str
    payer_id: str
    amount_kes: float
    external_ref: str = "PALPLUS-EDU-01"

@router.post("/pharma/batches")
def log_batch(req: LogPharmaBatchRequest, svc: KarisExpansionSuiteService = Depends(get_expsuite_service)):
    batch = svc.log_pharma_batch(req.product_id, req.organization_id, req.storage_min, req.storage_max)
    return {"status": "BATCH_LOGGED", "batch": batch.model_dump()}

@router.post("/pharma/telemetry")
def log_telemetry(req: LogPharmaTelemetryRequest, svc: KarisExpansionSuiteService = Depends(get_expsuite_service)):
    try:
        return svc.log_pharma_temperature_telemetry(req.batch_id, req.temperature_celsius, req.humidity_pct, req.gps_location)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/prop-share/syndications")
def create_synd(req: CreateSyndicationRequest, svc: KarisExpansionSuiteService = Depends(get_expsuite_service)):
    synd = svc.create_syndication(req.organization_id, req.title, req.location, req.total_shares, req.share_price_kes)
    return {"status": "SYNDICATION_CREATED", "syndication": synd.model_dump()}

@router.post("/prop-share/allocate")
def alloc_shares(req: AllocateSharesRequest, svc: KarisExpansionSuiteService = Depends(get_expsuite_service)):
    try:
        alloc = svc.allocate_shares(req.syndication_id, req.investor_id, req.shares)
        return {"status": "SHARES_ALLOCATED", "allocation": alloc.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/prop-share/distribute-dividends")
def dist_divs(req: DistributeDividendsRequest, svc: KarisExpansionSuiteService = Depends(get_expsuite_service)):
    try:
        return svc.distribute_monthly_rental_dividends(req.syndication_id, req.total_rental_pool_krt)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/edu-pay/plans")
def create_plan(req: CreateTuitionPlanRequest, svc: KarisExpansionSuiteService = Depends(get_expsuite_service)):
    plan = svc.create_tuition_plan(req.student_id, req.institution_org_id, req.term, req.total_tuition_kes)
    return {"status": "PLAN_CREATED", "plan": plan.model_dump()}

@router.post("/edu-pay/installments")
def pay_inst(req: PayTuitionRequest, svc: KarisExpansionSuiteService = Depends(get_expsuite_service)):
    try:
        return svc.pay_tuition_installment(req.plan_id, req.payer_id, req.amount_kes, req.external_ref)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
