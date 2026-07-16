from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from src.verticals.karis_loop.service import karis_loop_service, KarisLoopService

router = APIRouter(prefix="/api/v1/karis-loop", tags=["KARIS LOOP™ Social Intelligence Layer (`Section 54 - Vertical 19`)"])

def get_loop_service() -> KarisLoopService:
    return karis_loop_service

class RegisterProfileRequest(BaseModel):
    user_identity_id: str
    organization_id: str = "ORG-KARIS-RETAIL"
    handle_username: str = "creator_david"
    display_name: str = "David Kamau"
    account_type: str = "CREATOR_USER"

class CreateCommunityRequest(BaseModel):
    name: str = "Machakos County Farmers Guild"
    community_type: str = "REGIONAL_AGRI_GUILD"
    region_county: str = "Machakos County"
    creator_identity_id: str = "USER-KAMAU-01"
    organization_id: str = "ORG-KARIS-RETAIL"

class CreatePostRequest(BaseModel):
    creator_identity_id: str
    community_id: str
    content_type: str = "SHORT_VIDEO"
    caption_text: str
    media_payload_json: str = '{"video_url": "/assets/videos/loop_avo.mp4", "aspect_ratio": "9:16"}'
    linked_product_id: Optional[str] = "PROD-AVO-01"
    shoppable_price_kes: float = 350.0

class TipCreatorRequest(BaseModel):
    tipper_identity_id: str
    creator_identity_id: str
    post_id: str
    amount_krt: float = 50.0

class ShoppableCheckoutRequest(BaseModel):
    buyer_identity_id: str
    post_id: str
    linked_product_id: str = "PROD-AVO-01"
    merchant_organization_id: str = "ORG-KARIS-RETAIL"
    amount_kes_or_krt: float = 350.0
    payment_method: str = "KRT_WALLET"

class AICaptionRequest(BaseModel):
    product_title: str = "Grade-A Hass Avocados"
    shoppable_price_kes: float = 350.0
    target_language: str = "SWAHILI_SHENG"

@router.post("/profiles")
def reg_profile(req: RegisterProfileRequest, svc: KarisLoopService = Depends(get_loop_service)):
    prof = svc.register_profile(req.user_identity_id, req.organization_id, req.handle_username, req.display_name, req.account_type)
    return {"status": "PROFILE_REGISTERED", "profile": prof.model_dump()}

@router.post("/communities")
def create_comm(req: CreateCommunityRequest, svc: KarisLoopService = Depends(get_loop_service)):
    comm = svc.create_community(req.name, req.community_type, req.region_county, req.creator_identity_id, req.organization_id)
    return {"status": "COMMUNITY_CREATED", "community": comm.model_dump()}

@router.post("/posts")
def create_post(req: CreatePostRequest, svc: KarisLoopService = Depends(get_loop_service)):
    post = svc.create_post(req.creator_identity_id, req.community_id, req.content_type, req.caption_text, req.media_payload_json, req.linked_product_id, req.shoppable_price_kes)
    return {"status": "POST_PUBLISHED", "post": post.model_dump()}

@router.post("/tip")
def tip_creator(req: TipCreatorRequest, svc: KarisLoopService = Depends(get_loop_service)):
    try:
        return svc.tip_creator(req.tipper_identity_id, req.creator_identity_id, req.post_id, req.amount_krt)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/shoppable-checkout")
def shoppable_checkout(req: ShoppableCheckoutRequest, svc: KarisLoopService = Depends(get_loop_service)):
    try:
        return svc.checkout_shoppable_product(req.buyer_identity_id, req.post_id, req.linked_product_id, req.merchant_organization_id, req.amount_kes_or_krt, req.payment_method)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ai/caption")
def gen_caption(req: AICaptionRequest, svc: KarisLoopService = Depends(get_loop_service)):
    caption_res = svc.ai_copilot.generate_localized_caption(req.product_title, req.shoppable_price_kes, req.target_language)
    return {"status": "CAPTION_GENERATED", "ai_caption_package": caption_res}
