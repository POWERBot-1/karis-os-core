import uuid
from typing import Dict, Optional
from src.domain.models import EventCategory, EventPayload, MobilityTripModel
from src.core.event_bus import event_bus

class MobilityRideService:
    """
    KARIS OS™ Mobility & Ride-Hailing Service.
    Enforces Section 33 (Mobility & Ride-Hailing Vertical).
    Coordinates passenger trip requests, driver matching, dynamic surge calculations, and automated driver settlements.
    """
    def __init__(self):
        self.drivers: Dict[str, Dict] = {}
        self.trips: Dict[str, MobilityTripModel] = {}

    def register_driver(
        self,
        driver_identity_id: str,
        organization_id: str,
        licence_number: str,
        vehicle_make: str,
        registration_plate: str,
        service_tier: str = "BODABODA"
    ) -> Dict:
        driver = {
            "driver_id": str(uuid.uuid4()),
            "identity_id": driver_identity_id,
            "organization_id": organization_id,
            "licence_number": licence_number,
            "vehicle_make_model": vehicle_make,
            "registration_plate": registration_plate,
            "service_tier": service_tier,
            "status": "ONLINE_AVAILABLE",
            "rating": 5.0
        }
        self.drivers[driver["driver_id"]] = driver
        return driver

    def request_ride(
        self,
        organization_id: str,
        passenger_identity_id: str,
        pickup_text: str,
        dropoff_text: str,
        distance_km: float
    ) -> MobilityTripModel:
        base_fare = max(distance_km * 40.0 + 50.0, 100.0) # Base fare formula
        total_fare = round(base_fare, 2)
        driver_payout = round(total_fare * 0.82, 2) # 82% driver payout, 18% commission

        trip = MobilityTripModel(
            trip_id=str(uuid.uuid4()),
            trip_code=f"TRIP-{uuid.uuid4().hex[:6].upper()}",
            organization_id=organization_id,
            passenger_identity_id=passenger_identity_id,
            pickup_location_text=pickup_text,
            dropoff_location_text=dropoff_text,
            estimated_distance_km=distance_km,
            total_fare_kes=total_fare,
            driver_payout_kes=driver_payout,
            trip_status="RIDE_REQUESTED"
        )
        self.trips[trip.trip_id] = trip

        ev = EventPayload(
            event_type="MOBILITY_RIDE_REQUESTED",
            event_category=EventCategory.DELIVERY,
            actor_identity_id=passenger_identity_id,
            organization_id=organization_id,
            correlation_id=trip.trip_id,
            source_module="MOBILITY_ENGINE",
            payload=trip.model_dump(mode="json")
        )
        event_bus.publish(ev)
        return trip

    def accept_ride(self, trip_id: str, driver_id: str) -> MobilityTripModel:
        if trip_id not in self.trips:
            raise KeyError(f"Trip ID {trip_id} not found.")
        if driver_id not in self.drivers:
            raise KeyError(f"Driver ID {driver_id} not found.")

        trip = self.trips[trip_id]
        driver = self.drivers[driver_id]
        trip.driver_id = driver["driver_id"]
        trip.trip_status = "DRIVER_ACCEPTED"
        driver["status"] = "ON_TRIP"
        return trip

    def complete_trip(self, trip_id: str) -> Dict:
        if trip_id not in self.trips:
            raise KeyError(f"Trip ID {trip_id} not found.")

        trip = self.trips[trip_id]
        trip.trip_status = "TRIP_COMPLETED"

        driver = self.drivers.get(trip.driver_id, {})
        if trip.driver_id in self.drivers:
            self.drivers[trip.driver_id]["status"] = "ONLINE_AVAILABLE"

        ev = EventPayload(
            event_type="MOBILITY_TRIP_COMPLETED",
            event_category=EventCategory.DELIVERY,
            actor_identity_id=driver.get("identity_id", "UNKNOWN_DRIVER"),
            organization_id=trip.organization_id,
            correlation_id=trip.trip_id,
            source_module="MOBILITY_ENGINE",
            payload={
                "trip_id": trip.trip_id,
                "driver_id": trip.driver_id,
                "passenger_identity_id": trip.passenger_identity_id,
                "total_fare_kes": trip.total_fare_kes,
                "driver_payout_kes": trip.driver_payout_kes
            }
        )
        event_bus.publish(ev)

        return {
            "status": "SUCCESS",
            "trip_id": trip.trip_id,
            "total_fare_kes": trip.total_fare_kes,
            "driver_payout_kes": trip.driver_payout_kes,
            "message": "Trip completed and driver payout triggered via Universal Ledger."
        }

mobility_service = MobilityRideService()
