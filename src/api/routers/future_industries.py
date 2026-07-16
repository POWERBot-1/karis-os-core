from fastapi import APIRouter, status
from pydantic import BaseModel
from src.verticals.future_industries.service import future_industries_engine

router = APIRouter(prefix="/api/v1/future-industries", tags=["Future Industries Suite: Education, Tourism & Real Estate (Section 35.3)"])

class RegisterTuitionRequest(BaseModel):
    student_id: str = "USER-STUDENT-01"
    parent_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    institution_name: str = "Machakos Academy of Technology"
    term: str = "Term 3 2026"
    total_fee_kes: float = 45000.0
    organization_id: str = "ORG-KARIS-RETAIL"

class PayTuitionRequest(BaseModel):
    plan_id: str
    amount_paid_kes: float = 15000.0

class SafariBookingRequest(BaseModel):
    guest_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    lodge_name: str = "Machakos Luxury Eco-Safari Camp"
    nights: int = 3
    price_per_night_kes: float = 12000.0
    organization_id: str = "ORG-KARIS-RETAIL"

class CreateSyndicationRequest(BaseModel):
    property_code: str = "PROP-MLOLONGO-TOWERS-01"
    property_name: str = "Mlolongo Trade Towers"
    total_valuation_kes: float = 100_000_000.0
    total_units: float = 10000.0
    yield_pct: float = 13.8
    organization_id: str = "ORG-KARIS-RETAIL"

class AllocateSyndicationUnitsRequest(BaseModel):
    syndication_id: str
    investor_id: str = "8b6ff564-ce30-489e-8a02-75004ccd5516"
    units_purchased: float = 50.0

@router.post("/education/register-plan", status_code=status.HTTP_201_CREATED)
def register_tuition(req: RegisterTuitionRequest):
    return future_industries_engine.register_tuition_plan(
        req.student_id, req.parent_id, req.institution_name, req.term, req.total_fee_kes, req.organization_id
    )

@router.post("/education/pay-installment", status_code=status.HTTP_200_OK)
def pay_tuition(req: PayTuitionRequest):
    return future_industries_engine.pay_tuition_installment(req.plan_id, req.amount_paid_kes)

@router.post("/tourism/book-safari", status_code=status.HTTP_201_CREATED)
def book_safari(req: SafariBookingRequest):
    return future_industries_engine.book_safari_lodge(
        req.guest_id, req.lodge_name, req.nights, req.price_per_night_kes, req.organization_id
    )

@router.post("/real-estate/create-syndication", status_code=status.HTTP_201_CREATED)
def create_syndication(req: CreateSyndicationRequest):
    return future_industries_engine.create_property_syndication(
        req.property_code, req.property_name, req.total_valuation_kes, req.total_units, req.yield_pct, req.organization_id
    )

@router.post("/real-estate/allocate-units", status_code=status.HTTP_200_OK)
def allocate_units(req: AllocateSyndicationUnitsRequest):
    return future_industries_engine.allocate_fractional_units(req.syndication_id, req.investor_id, req.units_purchased)
