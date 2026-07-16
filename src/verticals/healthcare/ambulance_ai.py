import math
import uuid
from typing import Dict, Optional
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus

class EmergencyAmbulanceAIEngine:
    """
    KARIS OS™ AI Emergency Medical Ambulance Dispatching Engine (Section 32.8 & 33.5).
    Evaluates real-time GPS coordinates and oxygen life-support capacity (`ALS` vs `BLS`)
    to dispatch the nearest life-saving medical unit within milliseconds.
    """
    def __init__(self):
        self.ambulances: Dict[str, Dict] = {}
        self._seed_default_ambulances()

    def _seed_default_ambulances(self):
        self.register_ambulance_unit("ORG-KARIS-HEALTH", "AMB-MACHAKOS-ALS-01", "KCA-901M", "ADVANCED_LIFE_SUPPORT_ALS", "-1.3564,36.9321", "PARAMEDIC-01")
        self.register_ambulance_unit("ORG-KARIS-HEALTH", "AMB-MLOLONGO-BLS-02", "KCB-882Z", "BASIC_LIFE_SUPPORT_BLS", "-1.3800,36.9400", "PARAMEDIC-02")

    def register_ambulance_unit(
        self,
        organization_id: str,
        unit_code: str,
        registration: str,
        tier: str,
        gps_coords: str,
        paramedic_id: Optional[str] = None
    ) -> Dict:
        amb_id = f"AMB-UNIT-{uuid.uuid4().hex[:6].upper()}"
        unit = {
            "ambulance_id": amb_id,
            "organization_id": organization_id,
            "unit_code": unit_code,
            "vehicle_registration": registration,
            "life_support_tier": tier,
            "current_gps_coordinates": gps_coords,
            "assigned_paramedic_identity_id": paramedic_id,
            "oxygen_cylinder_level_pct": 100.0,
            "defibrillator_equipped": True,
            "readiness_status": "AVAILABLE_ON_STANDBY"
        }
        self.ambulances[amb_id] = unit
        return unit

    def _approx_distance_km(self, gps1: str, gps2: str) -> float:
        try:
            lat1, lon1 = map(float, gps1.split(","))
            lat2, lon2 = map(float, gps2.split(","))
            # Haversine geodesic approximation
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return round(6371.0 * c, 2)
        except Exception:
            return 5.0 # Default fallback distance

    def dispatch_nearest_emergency_unit(
        self,
        pickup_gps: str,
        required_tier: str = "BASIC_LIFE_SUPPORT_BLS",
        organization_id: str = "ORG-KARIS-HEALTH",
        patient_id: Optional[str] = "PATIENT-EMERGENCY-01"
    ) -> Dict:
        """Matches and dispatches nearest active ambulance with sufficient oxygen and life support."""
        available = [
            u for u in self.ambulances.values()
            if u["readiness_status"] == "AVAILABLE_ON_STANDBY" and u["oxygen_cylinder_level_pct"] > 30.0
        ]
        
        # Filter ALS if required
        if required_tier == "ADVANCED_LIFE_SUPPORT_ALS":
            available = [u for u in available if u["life_support_tier"] == "ADVANCED_LIFE_SUPPORT_ALS"]

        if not available:
            # Fallback to any available unit if ALS requested but busy
            available = [u for u in self.ambulances.values() if u["readiness_status"] == "AVAILABLE_ON_STANDBY"]
            if not available:
                raise RuntimeError("CRITICAL: No emergency ambulances currently available on standby!")

        # Sort by distance
        available.sort(key=lambda u: self._approx_distance_km(pickup_gps, u["current_gps_coordinates"]))
        selected = available[0]
        selected["readiness_status"] = "DISPATCHED_EN_ROUTE"

        distance = self._approx_distance_km(pickup_gps, selected["current_gps_coordinates"])
        eta_minutes = round(distance * 2.2 + 3.0, 1) # Emergency siren traffic velocity
        emergency_id = f"EMERG-{uuid.uuid4().hex[:8].upper()}"

        record = {
            "emergency_id": emergency_id,
            "ambulance_id": selected["ambulance_id"],
            "unit_code": selected["unit_code"],
            "life_support_tier": selected["life_support_tier"],
            "pickup_gps": pickup_gps,
            "assigned_paramedic": selected["assigned_paramedic_identity_id"],
            "estimated_distance_km": distance,
            "estimated_arrival_minutes": eta_minutes,
            "status": "AMBULANCE_DISPATCHED"
        }

        ev = EventPayload(
            event_type="AMBULANCE_DISPATCHED",
            event_category=EventCategory.HEALTHCARE,
            actor_identity_id=selected["assigned_paramedic_identity_id"] or "SYSTEM_AI_PARAMEDIC",
            organization_id=organization_id,
            correlation_id=emergency_id,
            source_module="AI_EMERGENCY_AMBULANCE_ENGINE",
            payload={
                "emergency_id": emergency_id,
                "ambulance_id": selected["ambulance_id"],
                "unit_code": selected["unit_code"],
                "life_support_tier": selected["life_support_tier"],
                "pickup_gps": pickup_gps,
                "estimated_arrival_minutes": eta_minutes
            }
        )
        event_bus.publish(ev)
        return record

ambulance_ai_engine = EmergencyAmbulanceAIEngine()
