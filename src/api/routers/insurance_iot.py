from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.verticals.financial_services.insurance_engine import parametric_insurance_iot_engine

router = APIRouter(prefix="/api/v1/financial/insurance", tags=["Parametric Crop/Livestock Insurance & IoT Telemetry (Section 34.4 & 28.5)"])

class IssuePolicyRequest(BaseModel):
    insured_id: str = "268e1e85-a0b3-445d-827b-98e327af3bee"
    farm_id: str = "FARM-ID-MACHAKOS-01"
    organization_id: str = "ORG-KARIS-FARM"
    policy_type: str = "CROP_DROUGHT_INDEX"
    insured_acreage: float = 15.0
    premium_kes: float = 5000.0
    max_payout_kes: float = 50000.0

class LogIotTelemetryRequest(BaseModel):
    sensor_code: str = "IOT-MACHAKOS-SN-001"
    farm_id: str = "FARM-ID-MACHAKOS-01"
    soil_moisture_pct: float = 14.5 # Drought condition (<20%)
    soil_temp_celsius: float = 26.0
    ambient_temp_celsius: float = 31.0
    rainfall_24h_mm: float = 0.0
    organization_id: str = "ORG-KARIS-FARM"

@router.post("/policies", status_code=status.HTTP_201_CREATED)
def issue_policy(req: IssuePolicyRequest):
    return parametric_insurance_iot_engine.issue_parametric_policy(
        req.insured_id, req.farm_id, req.organization_id, req.policy_type,
        req.insured_acreage, req.premium_kes, req.max_payout_kes
    )

@router.post("/iot/telemetry", status_code=status.HTTP_201_CREATED)
def log_iot_telemetry(req: LogIotTelemetryRequest):
    return parametric_insurance_iot_engine.log_iot_sensor_telemetry(
        req.sensor_code, req.farm_id, req.soil_moisture_pct, req.soil_temp_celsius,
        req.ambient_temp_celsius, req.rainfall_24h_mm, req.organization_id
    )
