from fastapi import APIRouter, status
from pydantic import BaseModel
from src.security.tax_override_engine import tax_override_engine

router = APIRouter(prefix="/api/v1/governance/tax", tags=["Declarative Tax Holidays & Dynamic Tariff Overrides (Section 43.1 & 43.2)"])

class TaxHolidayEvalRequest(BaseModel):
    organization_id: str = "ORG-KARIS-FARM"
    product_category: str = "AGRICULTURAL_INPUTS_SEEDS_FERTILIZERS"
    base_amount_kes: float = 100000.0
    standard_tax_pct: float = 16.0

@router.post("/holiday-evaluate", status_code=status.HTTP_200_OK)
def evaluate_tax_holiday(req: TaxHolidayEvalRequest):
    """Evaluates whether an order qualifies for a statutory agricultural tax holiday (`0% VAT`), overriding standard 16% VAT dynamically (`Rule 7`)."""
    return tax_override_engine.evaluate_and_apply_tax_override(
        req.organization_id, req.product_category, req.base_amount_kes, req.standard_tax_pct
    )
