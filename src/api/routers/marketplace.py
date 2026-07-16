from typing import Dict, List
from fastapi import APIRouter, status
from pydantic import BaseModel
from src.verticals.marketplace.service import marketplace_split_engine

router = APIRouter(prefix="/api/v1/marketplace/orders", tags=["Multi-Vendor Marketplace & Split-Commission Settlement (Section 14.3 & 17.2)"])

class MarketplaceSplitRequest(BaseModel):
    customer_identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    vendor_items: List[Dict] = [
        {"vendor_id": "268e1e85-a0b3-445d-827b-98e327af3bee", "amount_kes": 5000.0, "commission_pct": 15.0},
        {"vendor_id": "8b6ff564-ce30-489e-8a02-75004ccd5516", "amount_kes": 3000.0, "commission_pct": 15.0}
    ]
    payment_reference: str = "QG37XXXXXXXX"
    organization_id: str = "ORG-KARIS-RETAIL"

@router.post("/split-checkout", status_code=status.HTTP_201_CREATED)
def checkout_split_order(req: MarketplaceSplitRequest):
    """Executes multi-vendor split-commissions (`85% net to vendor, 15% platform fee`) via atomic multi-leg transfers (`Rule 2 & 5`)."""
    return marketplace_split_engine.execute_multi_vendor_split_settlement(
        req.customer_identity_id, req.vendor_items, req.payment_reference, req.organization_id
    )
