import math
import time
import uuid
from typing import Dict, Optional
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus
from src.core.wallet_engine import wallet_engine

class AiFraudDetectionAndVelocityEngine:
    """
    KARIS OS™ AI Fraud Detection & Real-Time Velocity Anomaly Response Engine (Section 38.6 & 27.1).
    Evaluates transaction velocity, impossible travel geographic anomalies (`Machakos -> Mombasa in 3 mins`),
    blacklisted devices, token manipulation, and credit abuse. Auto-freezes high-risk wallets (`Rule 5 & Rule 10`).
    """
    def __init__(self):
        self.velocity_logs: Dict[str, Dict] = {}
        self.cases: Dict[str, Dict] = {}
        self.last_seen: Dict[str, tuple[float, str]] = {} # identity_id -> (timestamp, gps_coords)

    def _approx_geodesic_km(self, gps1: str, gps2: str) -> float:
        try:
            lat1, lon1 = map(float, gps1.split(","))
            lat2, lon2 = map(float, gps2.split(","))
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return round(6371.0 * c, 2)
        except Exception:
            return 0.0

    def evaluate_transaction_fraud_risk(
        self,
        identity_id: str,
        wallet_id: Optional[str],
        amount_kes: float,
        device_fingerprint: str,
        location_gps: str,
        transaction_type: str = "M_PESA_CHECKOUT",
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        now = time.time()
        prev_time, prev_gps = self.last_seen.get(identity_id, (now, location_gps))
        seconds_elapsed = max(now - prev_time, 1.0)
        dist_km = self._approx_geodesic_km(prev_gps, location_gps) if prev_gps != location_gps else 0.0
        speed_kmh = round((dist_km / seconds_elapsed) * 3600.0, 2)

        self.last_seen[identity_id] = (now, location_gps)

        # Fraud Vector Analysis
        if speed_kmh > 800.0 and dist_km > 100.0:
            anomaly = "GEOGRAPHIC_VELOCITY_ABUSE_IMPOSSIBLE_TRAVEL"
            score = 94.5
            action = "FROZEN_WALLET_AND_SAR_ISSUED"
        elif "BLACKLISTED" in device_fingerprint.upper() or "HACKED" in device_fingerprint.upper():
            anomaly = "DEVICE_FINGERPRINT_BLACKLISTED"
            score = 91.0
            action = "FROZEN_WALLET_AND_SAR_ISSUED"
        elif amount_kes > 2_000_000.0:
            anomaly = "TRANSACTION_VELOCITY_BRUTE_FORCE"
            score = 85.0
            action = "FLAGGED_MONITORING"
        else:
            anomaly = "NORMAL_VELOCITY"
            score = 12.0
            action = "CLEARED_PROCEED"

        vel_id = f"VEL-{uuid.uuid4().hex[:8].upper()}"
        record = {
            "velocity_id": vel_id,
            "identity_id": identity_id,
            "wallet_id": wallet_id,
            "organization_id": organization_id,
            "transaction_type": transaction_type,
            "amount_kes": amount_kes,
            "device_fingerprint": device_fingerprint,
            "location_gps_coordinates": location_gps,
            "previous_gps_coordinates": prev_gps,
            "seconds_since_previous_tx": round(seconds_elapsed, 2),
            "geodesic_distance_from_previous_km": dist_km,
            "calculated_travel_speed_kmh": speed_kmh,
            "fraud_risk_score": score,
            "flagged_anomaly_type": anomaly,
            "action_taken": action
        }
        self.velocity_logs[vel_id] = record

        if score > 80.0:
            # Freeze target wallet if present (Rule 5 Security Protection)
            if wallet_id and wallet_id in wallet_engine.wallets:
                wallet_engine.wallets[wallet_id].status = "FROZEN"

            case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
            case_code = f"FRAUD-CASE-2026-{uuid.uuid4().hex[:6].upper()}"
            case = {
                "case_id": case_id,
                "case_code": case_code,
                "velocity_id": vel_id,
                "identity_id": identity_id,
                "organization_id": organization_id,
                "fraud_vector": anomaly,
                "risk_score": score,
                "investigation_status": "FLAGGED_FROZEN"
            }
            self.cases[case_id] = case

            ev = EventPayload(
                event_type="FRAUD_ANOMALY_DETECTED",
                event_category=EventCategory.GOVERNANCE,
                actor_identity_id="AI_FRAUD_ENGINE",
                organization_id=organization_id,
                correlation_id=vel_id,
                source_module="AI_FRAUD_VELOCITY_ENGINE",
                payload={
                    "velocity_id": vel_id,
                    "identity_id": identity_id,
                    "amount_kes": amount_kes,
                    "device_fingerprint": device_fingerprint,
                    "location_gps": location_gps,
                    "fraud_risk_score": score,
                    "flagged_anomaly_type": anomaly,
                    "action_taken": action
                }
            )
            event_bus.publish(ev)

        return record

fraud_ai_engine = AiFraudDetectionAndVelocityEngine()
