from fastapi import APIRouter, status
from pydantic import BaseModel
from src.verticals.logistics.route_weather_ai import warehouse_weather_engine

router = APIRouter(prefix="/api/v1/logistics/ai", tags=["Multi-Warehouse Serial Tracking & AI Weather-Aware Dispatch (Section 15 & 21.5)"])

class SerialCrateRequest(BaseModel):
    product_id: str = "PROD-AVO-01"
    batch_id: str = "BATCH-FARM-HAS-1BF01C"
    warehouse_code: str = "WH-MACHAKOS-MAIN"
    organization_id: str = "ORG-KARIS-FARM"
    custodian_id: str = "268e1e85-a0b3-445d-827b-98e327af3bee"

class WeatherDispatchRequest(BaseModel):
    order_id: str = "ORD-WEATHER-101"
    pickup_gps: str = "Machakos Hub"
    dropoff_gps: str = "Mlolongo Estate"
    distance_km: float = 8.0
    weather_condition: str = "HEAVY_RAINFALL_STORM"
    organization_id: str = "ORG-KARIS-RETAIL"

@router.post("/serial-tracking", status_code=status.HTTP_201_CREATED)
def register_serial_crate(req: SerialCrateRequest):
    return warehouse_weather_engine.register_warehouse_serial_crate(
        req.product_id, req.batch_id, req.warehouse_code, req.organization_id, req.custodian_id
    )

@router.post("/weather-dispatch", status_code=status.HTTP_201_CREATED)
def execute_weather_dispatch(req: WeatherDispatchRequest):
    """Section 21.5: AI Dispatcher evaluates storm conditions and auto-switches from two-wheelers to covered refrigerated trucks."""
    return warehouse_weather_engine.optimize_weather_aware_logistics_dispatch(
        req.order_id, req.pickup_gps, req.dropoff_gps, req.distance_km, req.weather_condition, req.organization_id
    )
