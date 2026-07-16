from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.verticals.mobility.service import mobility_service

router = APIRouter(prefix="/api/v1/mobility", tags=["Mobility & Ride-Hailing Vertical"])

class RegisterDriverRequest(BaseModel):
    driver_identity_id: str
    organization_id: str
    licence_number: str
    vehicle_make: str
    registration_plate: str
    service_tier: str = "BODABODA"

class RequestRideRequest(BaseModel):
    organization_id: str
    passenger_identity_id: str
    pickup_text: str
    dropoff_text: str
    distance_km: float

class AcceptRideRequest(BaseModel):
    trip_id: str
    driver_id: str

@router.post("/drivers", status_code=status.HTTP_201_CREATED)
def register_driver(req: RegisterDriverRequest):
    return mobility_service.register_driver(
        req.driver_identity_id, req.organization_id, req.licence_number, req.vehicle_make, req.registration_plate, req.service_tier
    )

@router.post("/trips/request", status_code=status.HTTP_201_CREATED)
def request_ride(req: RequestRideRequest):
    return mobility_service.request_ride(
        req.organization_id, req.passenger_identity_id, req.pickup_text, req.dropoff_text, req.distance_km
    )

@router.post("/trips/accept", status_code=status.HTTP_200_OK)
def accept_ride(req: AcceptRideRequest):
    try:
        return mobility_service.accept_ride(req.trip_id, req.driver_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/trips/{trip_id}/complete", status_code=status.HTTP_200_OK)
def complete_trip(trip_id: str):
    try:
        return mobility_service.complete_trip(trip_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
