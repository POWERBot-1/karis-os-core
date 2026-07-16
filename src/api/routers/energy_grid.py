import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.core.event_bus import event_bus, UniversalEventBus
from src.core.ledger_engine import ledger_engine, UniversalLedgerEngine
from src.core.wallet_engine import wallet_engine, MultiAssetWalletEngine
from src.verticals.karis_energy.service import karis_energy_service, KarisEnergyService

router = APIRouter(prefix="/api/v1/energy-grid", tags=["KARIS OS :: KARIS ENERGY & SMART SOLAR GRID™ (Section 50 - Vertical 15)"])

def get_energy_service() -> KarisEnergyService:
    return karis_energy_service

class RegisterUnitRequest(BaseModel):
    owner_user_id: str
    organization_id: str = "ORG-KARIS-FARM-MAIN"
    device_serial_number: str
    device_type: str = "SOLAR_IRRIGATION_PUMP"
    rated_capacity_watts: float = 1500.0
    daily_token_rate_krt: float = 50.0

class LogTelemetryRequest(BaseModel):
    installation_id: str
    kwh_generated_today: float
    kwh_consumed_today: float
    battery_voltage_v: float = 25.2
    soil_moisture_pct: float = 48.0
    microgrid_feed_in_kwh: float = 0.0

class PAYGInstallmentRequest(BaseModel):
    installation_id: str
    payer_user_id: str
    amount_krt: float
    payment_method: str = "KRT_WALLET"

class PeerTradeRequest(BaseModel):
    seller_user_id: str
    buyer_user_id: str
    organization_id: str = "ORG-KARIS-FARM-MAIN"
    kwh_traded: float
    price_per_kwh_krt: float = 12.5

@router.post("/installations")
def register_solar_unit(req: RegisterUnitRequest, svc: KarisEnergyService = Depends(get_energy_service)):
    inst = svc.register_solar_unit(req.owner_user_id, req.organization_id, req.device_serial_number, req.device_type, req.rated_capacity_watts, req.daily_token_rate_krt)
    return {"status": "SOLAR_UNIT_REGISTERED", "installation": inst.model_dump()}

@router.post("/telemetry")
def log_telemetry(req: LogTelemetryRequest, svc: KarisEnergyService = Depends(get_energy_service)):
    try:
        res = svc.log_smart_meter_telemetry(req.installation_id, req.kwh_generated_today, req.kwh_consumed_today, req.battery_voltage_v, req.soil_moisture_pct, req.microgrid_feed_in_kwh)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/payg")
def pay_payg_installment(req: PAYGInstallmentRequest, svc: KarisEnergyService = Depends(get_energy_service)):
    try:
        res = svc.pay_payg_installment(req.installation_id, req.payer_user_id, req.amount_krt, req.payment_method)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/peer-trade")
def peer_trade(req: PeerTradeRequest, svc: KarisEnergyService = Depends(get_energy_service)):
    try:
        trade = svc.execute_peer_energy_trade(req.seller_user_id, req.buyer_user_id, req.organization_id, req.kwh_traded, req.price_per_kwh_krt)
        return {"status": "PEER_TRADE_SETTLED", "trade": trade.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
