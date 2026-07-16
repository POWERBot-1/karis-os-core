from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.verticals.logistics.service import logistics_service

router = APIRouter(prefix="/api/v1/logistics", tags=["Delivery & Logistics Vertical"])

class RegisterRiderRequest(BaseModel):
    rider_identity_id: str
    organization_id: str
    vehicle_type: str
    registration_plate: str
    zone_name: str = "ZONE-MACHAKOS-MLOLONGO"

class RequestDispatchRequest(BaseModel):
    organization_id: str
    order_id: str
    pickup_address: str
    dropoff_address: str
    distance_km: float

class AssignRiderRequest(BaseModel):
    dispatch_id: str
    rider_id: str

class ConfirmDeliveryRequest(BaseModel):
    dispatch_id: str
    recipient_identity_id: str
    gps_confirmation: str
    verification_code: str

@router.post("/riders", status_code=status.HTTP_201_CREATED)
def register_rider(req: RegisterRiderRequest):
    return logistics_service.register_rider(
        req.rider_identity_id, req.organization_id, req.vehicle_type, req.registration_plate, req.zone_name
    )

@router.post("/dispatches", status_code=status.HTTP_201_CREATED)
def request_dispatch(req: RequestDispatchRequest):
    return logistics_service.request_delivery_dispatch(
        req.organization_id, req.order_id, req.pickup_address, req.dropoff_address, req.distance_km
    )

@router.post("/assign", status_code=status.HTTP_200_OK)
def assign_rider(req: AssignRiderRequest):
    try:
        return logistics_service.assign_rider(req.dispatch_id, req.rider_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/confirm-delivery", status_code=status.HTTP_200_OK)
def confirm_delivery(req: ConfirmDeliveryRequest):
    try:
        return logistics_service.confirm_delivery_completed(
            req.dispatch_id, req.recipient_identity_id, req.gps_confirmation, req.verification_code
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
