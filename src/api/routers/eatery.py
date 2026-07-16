from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.verticals.eatery.service import eatery_service

router = APIRouter(prefix="/api/v1/eatery", tags=["Eatery & Food Services Vertical (KDS)"])

class RegisterEateryRequest(BaseModel):
    organization_id: str
    eatery_name: str
    business_type: str = "CLOUD_KITCHEN"
    address: str = "Machakos Eatery Hub"

class AddMenuItemRequest(BaseModel):
    eatery_id: str
    sku: str
    name: str
    price_kes: float
    preparation_time_mins: int = 20

class SubmitKdsRequest(BaseModel):
    eatery_id: str
    order_id: str
    table_number: str = "DELIVERY_ORDER"

class FlagMealReadyRequest(BaseModel):
    kds_id: str
    chef_identity_id: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_eatery(req: RegisterEateryRequest):
    return eatery_service.register_eatery(req.organization_id, req.eatery_name, req.business_type, req.address)

@router.post("/menu-items", status_code=status.HTTP_201_CREATED)
def add_menu_item(req: AddMenuItemRequest):
    return eatery_service.add_menu_item(req.eatery_id, req.sku, req.name, req.price_kes, req.preparation_time_mins)

@router.post("/kds/submit", status_code=status.HTTP_201_CREATED)
def submit_to_kds(req: SubmitKdsRequest):
    return eatery_service.submit_to_kds(req.eatery_id, req.order_id, req.table_number)

@router.post("/kds/ready", status_code=status.HTTP_200_OK)
def flag_meal_ready(req: FlagMealReadyRequest):
    try:
        return eatery_service.flag_meal_ready(req.kds_id, req.chef_identity_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
