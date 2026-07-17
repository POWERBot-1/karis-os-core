"""
KARIS OS™ :: FastAPI Router for COSMOX™ Universal AI Marketplace & KRT Economy (`Section 57 / Vertical 22`).
Exposes endpoints for Universal Wallet onboarding, AI Shopping/Pricing/Translation, Escrow Checkout (`Rule 2`),
Strict Logistics Escrow Release (`Rule 4`), Referral Network, Developer Platform, and Multi-Sig Treasury (`Rule 10`).
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.verticals.cosmox.service import cosmox_service, CosmoxService

router = APIRouter(prefix="/api/v1/cosmox", tags=["COSMOX Universal Marketplace"])

def get_cosmox_service() -> CosmoxService:
    return cosmox_service

# Request Schemas
class AccountOnboardRequest(BaseModel):
    identity_id: str
    account_type: str = "BUYER"
    initial_fiat_kes: float = 50000.0
    initial_krt: float = 2000.0

class ProductCreateRequest(BaseModel):
    seller_account_id: str
    product_name: str
    category: str
    base_price_krt: float
    inventory_count: int = 100
    ai_dynamic_pricing_enabled: bool = True

class OrderCheckoutRequest(BaseModel):
    buyer_account_id: str
    product_id: str
    quantity: int = 1

class LogisticsDispatchRequest(BaseModel):
    order_id: str
    driver_account_id: str
    origin: str = "Nairobi Inland Depot"
    destination: str = "Machakos Town Hub"
    distance_km: float = 45.0

class DeliveryConfirmRequest(BaseModel):
    delivery_id: str

class ReferralQualifyRequest(BaseModel):
    referrer_account_id: str
    referred_account_id: str
    referral_type: str = "INDIVIDUAL"

class DigitalServicePublishRequest(BaseModel):
    developer_account_id: str
    title: str
    service_type: str
    api_endpoint_url: str
    price_krt_per_access: float = 10.0

class DigitalServicePurchaseRequest(BaseModel):
    buyer_account_id: str
    service_id: str

class AIRecommendRequest(BaseModel):
    buyer_account_id: str
    recent_categories: list[str] = ["PHYSICAL_GOODS"]

class AITranslateRequest(BaseModel):
    text: str
    target_lang: str = "SW"

class MultisigTreasuryRequest(BaseModel):
    requester_account_id: str
    amount_krt: float
    purpose: str

class MultisigApproveRequest(BaseModel):
    approver_account_id: str
    request_id: str

# Endpoints
@router.post("/accounts/onboard", status_code=status.HTTP_201_CREATED)
def onboard_account(
    req: AccountOnboardRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    try:
        acc = service.onboard_cosmox_account(req.identity_id, req.account_type, req.initial_fiat_kes, req.initial_krt)
        return {"status": "SUCCESS", "account": acc.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/accounts/{account_id}")
def get_account(
    account_id: str,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    if account_id not in service.accounts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COSMOX Account not found.")
    return {"status": "SUCCESS", "account": service.accounts[account_id].model_dump()}

@router.post("/products/create", status_code=status.HTTP_201_CREATED)
def create_product(
    req: ProductCreateRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    try:
        prod = service.create_product(
            req.seller_account_id, req.product_name, req.category,
            req.base_price_krt, req.inventory_count, req.ai_dynamic_pricing_enabled
        )
        return {"status": "SUCCESS", "product": prod.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/orders/checkout", status_code=status.HTTP_201_CREATED)
def checkout_order(
    req: OrderCheckoutRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    try:
        order = service.checkout_marketplace_order(req.buyer_account_id, req.product_id, req.quantity)
        return {"status": "SUCCESS", "order": order.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/logistics/dispatch", status_code=status.HTTP_201_CREATED)
def dispatch_logistics(
    req: LogisticsDispatchRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    try:
        deliv = service.dispatch_logistics_delivery(
            req.order_id, req.driver_account_id, req.origin, req.destination, req.distance_km
        )
        return {"status": "SUCCESS", "delivery": deliv.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/logistics/confirm-delivery")
def confirm_delivery(
    req: DeliveryConfirmRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    try:
        order, deliv = service.confirm_delivery_and_settle_escrow(req.delivery_id)
        return {"status": "SUCCESS", "order_settled": order.model_dump(), "delivery_confirmed": deliv.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/referrals/qualify")
def qualify_referral(
    req: ReferralQualifyRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    try:
        ref = service.qualify_and_payout_referral(req.referrer_account_id, req.referred_account_id, req.referral_type)
        if ref.status != "REWARDED_CLEAN":
            return {"status": "REJECTED", "reason": ref.status, "referral": ref.model_dump()}
        return {"status": "SUCCESS", "referral": ref.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/digital-services/publish", status_code=status.HTTP_201_CREATED)
def publish_digital(
    req: DigitalServicePublishRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    try:
        ds = service.publish_digital_service(
            req.developer_account_id, req.title, req.service_type, req.api_endpoint_url, req.price_krt_per_access
        )
        return {"status": "SUCCESS", "digital_service": ds.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/digital-services/purchase", status_code=status.HTTP_201_CREATED)
def purchase_digital(
    req: DigitalServicePurchaseRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    try:
        res = service.purchase_digital_service(req.buyer_account_id, req.service_id)
        return {"status": "SUCCESS", "purchase_record": res}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/ai/recommend")
def recommend_products(
    req: AIRecommendRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    rep = 100
    if req.buyer_account_id in service.accounts:
        rep = service.accounts[req.buyer_account_id].reputation_score
    res = service.ai_engine.recommend_products(req.buyer_account_id, req.recent_categories, rep)
    return {"status": "SUCCESS", "ai_recommendations": res}

@router.post("/ai/translate")
def translate_text(
    req: AITranslateRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    res = service.ai_engine.translate_content(req.text, req.target_lang)
    return {"status": "SUCCESS", "ai_translation": res}

@router.post("/treasury/request-multisig", status_code=status.HTTP_201_CREATED)
def request_multisig(
    req: MultisigTreasuryRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    try:
        ms = service.request_multisig_treasury_disbursement(req.requester_account_id, req.amount_krt, req.purpose)
        return {"status": "SUCCESS", "multisig_request": ms.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/treasury/approve-multisig")
def approve_multisig(
    req: MultisigApproveRequest,
    service: CosmoxService = Depends(get_cosmox_service)
) -> Dict[str, Any]:
    try:
        ms = service.approve_multisig_treasury_request(req.approver_account_id, req.request_id)
        return {"status": "SUCCESS", "multisig_request": ms.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
