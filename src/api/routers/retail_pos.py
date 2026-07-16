from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.domain.models import OrderItemModel
from src.verticals.retail_pos.service import retail_pos_service

router = APIRouter(prefix="/api/v1/retail-pos", tags=["Omnichannel POS & Supermarket Vertical"])

class RegisterStoreRequest(BaseModel):
    organization_id: str
    store_name: str
    terminal_code: str
    branch_type: str = "SUPERMARKET"

class OpenSessionRequest(BaseModel):
    terminal_code: str
    cashier_identity_id: str
    opening_cash_kes: float = 10000.0

class PosCheckoutRequest(BaseModel):
    session_id: str
    store_id: str
    customer_identity_id: str
    supplier_identity_id: str
    items: List[OrderItemModel]
    payment_method: str = "MIXED_PAYMENT"
    krt_discount_used: float = 0.0

@router.post("/stores", status_code=status.HTTP_201_CREATED)
def register_store(req: RegisterStoreRequest):
    return retail_pos_service.register_store_and_terminal(
        req.organization_id, req.store_name, req.terminal_code, req.branch_type
    )

@router.post("/sessions/open", status_code=status.HTTP_201_CREATED)
def open_session(req: OpenSessionRequest):
    return retail_pos_service.open_pos_session(req.terminal_code, req.cashier_identity_id, req.opening_cash_kes)

@router.post("/checkout", status_code=status.HTTP_200_OK)
def pos_checkout(req: PosCheckoutRequest):
    try:
        return retail_pos_service.process_pos_checkout(
            req.session_id, req.store_id, req.customer_identity_id, req.supplier_identity_id,
            req.items, req.payment_method, req.krt_discount_used
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
