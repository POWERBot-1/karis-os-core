import uuid
from typing import Dict
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus
from src.verticals.logistics.service import logistics_service

class MultiWarehouseAndWeatherDispatchEngine:
    """
    KARIS OS™ Multi-Warehouse Batch Serial Tracking & AI Weather-Aware Dispatch Engine (Section 15 & 21.5).
    Tracks crate serial numbers (`SN-AVO-CRATE-0001`) across multi-warehouse hubs,
    and auto-switches delivery vehicles from motorcycles to covered refrigerated vans during heavy storms (`Section 21.5`).
    """
    def __init__(self):
        self.serial_inventory: Dict[str, Dict] = {}
        self.weather_dispatches: Dict[str, Dict] = {}

    def register_warehouse_serial_crate(
        self,
        product_id: str,
        batch_id: str,
        warehouse_code: str = "WH-MACHAKOS-MAIN",
        organization_id: str = "ORG-KARIS-FARM",
        custodian_id: str = "268e1e85-a0b3-445d-827b-98e327af3bee"
    ) -> Dict:
        s_id = f"SER-ITEM-{uuid.uuid4().hex[:8].upper()}"
        barcode = f"SN-AVO-CRATE-2026-{uuid.uuid4().hex[:6].upper()}"

        record = {
            "serial_item_id": s_id,
            "serial_barcode": barcode,
            "product_id": product_id,
            "batch_id": batch_id,
            "organization_id": organization_id,
            "warehouse_location_code": warehouse_code,
            "current_custodian_identity_id": custodian_id,
            "item_status": "AVAILABLE_IN_WAREHOUSE",
            "traceability_qr_code": f"KARIS-TRACE-QR-{uuid.uuid4().hex[:8].upper()}"
        }
        self.serial_inventory[barcode] = record

        ev = EventPayload(
            event_type="WAREHOUSE_SERIAL_ITEM_TRANSFERRED",
            event_category=EventCategory.COMMERCE,
            actor_identity_id=custodian_id,
            organization_id=organization_id,
            correlation_id=s_id,
            source_module="MULTI_WAREHOUSE_SERIAL_TRACKING_ENGINE",
            payload={
                "serial_item_id": s_id,
                "serial_barcode": barcode,
                "product_id": product_id,
                "warehouse_location_code": warehouse_code,
                "item_status": "AVAILABLE_IN_WAREHOUSE"
            }
        )
        event_bus.publish(ev)
        return record

    def optimize_weather_aware_logistics_dispatch(
        self,
        order_id: str,
        pickup_gps: str = "Machakos Hub",
        dropoff_gps: str = "Mlolongo Estate",
        distance_km: float = 8.0,
        weather_condition: str = "HEAVY_RAINFALL_STORM",
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        """Section 21.5: AI Dispatcher evaluates weather storm and automatically upgrades vehicle to covered refrigerated truck."""
        if weather_condition == "HEAVY_RAINFALL_STORM":
            vehicle = "REFRIGERATED_TRUCK"
            rationale = "ALERT: Heavy storm rainfall detected in Machakos corridor. Switched from two-wheeler motorcycle to covered refrigerated truck to protect Grade-A Avocado cargo!"
            surge = 1.35
        elif weather_condition == "EXTREME_HEAT_SURGE":
            vehicle = "REFRIGERATED_TRUCK"
            rationale = "Extreme heat surge detected (>34C). Switched to refrigerated transport."
            surge = 1.20
        else:
            vehicle = "MOTORCYCLE"
            rationale = "Clear sunny weather. Optimal two-wheeler dispatch."
            surge = 1.00

        # Request base dispatch from logistics service
        base_dispatch = logistics_service.request_delivery_dispatch(organization_id, order_id, pickup_gps, dropoff_gps, distance_km)
        final_fee = round(base_dispatch.delivery_fee_kes * surge, 2)

        w_id = f"W-DISP-{uuid.uuid4().hex[:8].upper()}"
        record = {
            "weather_dispatch_id": w_id,
            "dispatch_id": base_dispatch.dispatch_id,
            "order_id": order_id,
            "pickup_gps": pickup_gps,
            "dropoff_gps": dropoff_gps,
            "weather_condition": weather_condition,
            "selected_vehicle_type": vehicle,
            "ai_weather_rationale": rationale,
            "weather_surge_multiplier": surge,
            "final_delivery_fee_kes": final_fee
        }
        self.weather_dispatches[w_id] = record
        return record

warehouse_weather_engine = MultiWarehouseAndWeatherDispatchEngine()
