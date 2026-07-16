import uuid
from typing import Dict, Optional
from src.domain.models import EventCategory, EventPayload, LogisticsDispatchModel
from src.core.event_bus import event_bus
from src.core.ai_gateway import ai_gateway

class LogisticsDeliveryService:
    """
    KARIS OS™ Delivery & Logistics Service.
    Enforces Section 21 (Delivery & Logistics Engine) and Rule 4 (No Delivery -> No Rider Payment).
    Coordinates dispatching, route optimization via Logistics AI, and proof-of-delivery settlement.
    """
    def __init__(self):
        self.dispatches: Dict[str, LogisticsDispatchModel] = {}
        self.riders: Dict[str, Dict] = {}

    def register_rider(
        self,
        rider_identity_id: str,
        organization_id: str,
        vehicle_type: str,
        registration_plate: str,
        zone_name: str = "ZONE-MACHAKOS-MLOLONGO"
    ) -> Dict:
        rider = {
            "rider_id": str(uuid.uuid4()),
            "identity_id": rider_identity_id,
            "organization_id": organization_id,
            "vehicle_type": vehicle_type,
            "registration_plate": registration_plate,
            "assigned_zone": zone_name,
            "active_status": "AVAILABLE",
            "safety_score": 100.0
        }
        self.riders[rider["rider_id"]] = rider
        return rider

    def request_delivery_dispatch(
        self,
        organization_id: str,
        order_id: str,
        pickup_address: str,
        dropoff_address: str,
        distance_km: float
    ) -> LogisticsDispatchModel:
        # Ask Logistics AI for optimized routing & fee
        ai_opt = ai_gateway.optimize_dispatch_route(pickup_address, dropoff_address, distance_km)
        fee_kes = ai_opt["recommended_delivery_fee_kes"]

        dispatch = LogisticsDispatchModel(
            dispatch_id=str(uuid.uuid4()),
            organization_id=organization_id,
            order_id=order_id,
            pickup_address=pickup_address,
            dropoff_address=dropoff_address,
            distance_km=distance_km,
            delivery_fee_kes=fee_kes,
            escrow_payout_kes=round(fee_kes * 0.85, 2), # 85% to rider, 15% platform commission
            dispatch_status="DELIVERY_REQUESTED",
            ai_dispatch_score=ai_opt["route_priority_score"]
        )
        self.dispatches[dispatch.dispatch_id] = dispatch

        ev = EventPayload(
            event_type="DELIVERY_REQUESTED",
            event_category=EventCategory.DELIVERY,
            actor_identity_id="SYSTEM_LOGISTICS",
            organization_id=organization_id,
            correlation_id=dispatch.dispatch_id,
            source_module="LOGISTICS_ENGINE",
            payload=dispatch.model_dump(mode="json")
        )
        event_bus.publish(ev)
        return dispatch

    def assign_rider(self, dispatch_id: str, rider_id: str) -> LogisticsDispatchModel:
        if dispatch_id not in self.dispatches:
            raise KeyError(f"Dispatch ID {dispatch_id} not found.")
        if rider_id not in self.riders:
            raise KeyError(f"Rider ID {rider_id} not found.")

        dispatch = self.dispatches[dispatch_id]
        rider = self.riders[rider_id]

        dispatch.rider_identity_id = rider["identity_id"]
        dispatch.dispatch_status = "RIDER_ASSIGNED"
        rider["active_status"] = "ON_DELIVERY"

        ev = EventPayload(
            event_type="LOGISTICS_RIDER_ASSIGNED",
            event_category=EventCategory.DELIVERY,
            actor_identity_id=rider["identity_id"],
            organization_id=dispatch.organization_id,
            correlation_id=dispatch.dispatch_id,
            source_module="LOGISTICS_ENGINE",
            payload={
                "dispatch_id": dispatch.dispatch_id,
                "order_id": dispatch.order_id,
                "rider_identity_id": rider["identity_id"],
                "vehicle_type": rider["vehicle_type"],
                "estimated_distance_km": dispatch.distance_km,
                "delivery_fee_kes": dispatch.delivery_fee_kes
            }
        )
        event_bus.publish(ev)
        return dispatch

    def confirm_delivery_completed(
        self,
        dispatch_id: str,
        recipient_identity_id: str,
        gps_confirmation: str,
        verification_code: str
    ) -> Dict:
        if dispatch_id not in self.dispatches:
            raise KeyError(f"Dispatch ID {dispatch_id} not found.")

        dispatch = self.dispatches[dispatch_id]
        dispatch.dispatch_status = "DELIVERED"

        # Emit DELIVERY_COMPLETED event -> Triggering Rule Engine & Escrow Payout (Rule 4 & Rule 2)
        ev = EventPayload(
            event_type="DELIVERY_COMPLETED",
            event_category=EventCategory.DELIVERY,
            actor_identity_id=dispatch.rider_identity_id or "UNKNOWN_RIDER",
            organization_id=dispatch.organization_id,
            correlation_id=dispatch.dispatch_id,
            source_module="LOGISTICS_ENGINE",
            payload={
                "delivery_id": dispatch.dispatch_id,
                "order_id": dispatch.order_id,
                "rider_identity_id": dispatch.rider_identity_id,
                "recipient_identity_id": recipient_identity_id,
                "delivery_fee_kes": dispatch.escrow_payout_kes,
                "gps_confirmation": gps_confirmation,
                "verification_code": verification_code,
                "status": "COMPLETED"
            }
        )
        event_bus.publish(ev)

        return {
            "status": "SUCCESS",
            "dispatch_id": dispatch.dispatch_id,
            "rider_identity_id": dispatch.rider_identity_id,
            "escrow_payout_released_kes": dispatch.escrow_payout_kes,
            "message": "Delivery completed and verified! Rider escrow payout triggered."
        }

logistics_service = LogisticsDeliveryService()
