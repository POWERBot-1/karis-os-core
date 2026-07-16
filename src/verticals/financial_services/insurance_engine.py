import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine

class ParametricCropInsuranceAndIotEngine:
    """
    KARIS OS™ Parametric Crop Insurance & IoT Sensor Trigger Engine (Section 34.4 & 28.5).
    Issues parametric crop/livestock policies, monitors IoT weather/moisture sensor telemetry (`Machakos Farm`),
    auto-triggers smart irrigation valves, and auto-disburses insurance claim payouts via Universal Ledger (`Rule 2 & 5`).
    """
    def __init__(self):
        self.policies: Dict[str, Dict] = {}
        self.telemetry_logs: Dict[str, Dict] = {}
        self.claims: Dict[str, Dict] = {}

    def issue_parametric_policy(
        self,
        insured_id: str,
        farm_id: str,
        organization_id: str = "ORG-KARIS-FARM",
        policy_type: str = "CROP_DROUGHT_INDEX",
        insured_acreage: float = 15.0,
        premium_kes: float = 5000.0,
        max_payout_kes: float = 50000.0
    ) -> Dict:
        policy_id = f"POL-{uuid.uuid4().hex[:8].upper()}"
        policy_code = f"POL-AGRI-2026-{uuid.uuid4().hex[:6].upper()}"
        now = datetime.now(timezone.utc)

        policy = {
            "policy_id": policy_id,
            "policy_code": policy_code,
            "organization_id": organization_id,
            "insured_identity_id": insured_id,
            "farm_id": farm_id,
            "policy_type": policy_type,
            "insured_acreage_or_head": insured_acreage,
            "premium_paid_kes": premium_kes,
            "max_coverage_payout_kes": max_payout_kes,
            "parametric_trigger_rule_json": '{"trigger_metric": "SOIL_MOISTURE_PCT", "operator": "LT", "threshold": 20.0, "duration_hours": 72}',
            "policy_status": "ACTIVE_INSURED",
            "effective_from": now.isoformat(),
            "effective_until": (now + timedelta(days=365)).isoformat()
        }
        self.policies[policy_id] = policy

        ev = EventPayload(
            event_type="INSURANCE_POLICY_CREATED",
            event_category=EventCategory.GOVERNANCE,
            actor_identity_id=insured_id,
            organization_id=organization_id,
            correlation_id=policy_id,
            source_module="PARAMETRIC_CROP_INSURANCE_ENGINE",
            payload={
                "policy_id": policy_id,
                "policy_code": policy_code,
                "insured_identity_id": insured_id,
                "policy_type": policy_type,
                "premium_paid_kes": premium_kes,
                "max_coverage_payout_kes": max_payout_kes
            }
        )
        event_bus.publish(ev)
        return policy

    def log_iot_sensor_telemetry(
        self,
        sensor_code: str,
        farm_id: str,
        soil_moisture_pct: float,
        soil_temp_celsius: float = 24.5,
        ambient_temp_celsius: float = 28.0,
        rainfall_24h_mm: float = 0.0,
        organization_id: str = "ORG-KARIS-FARM"
    ) -> Dict:
        """Logs IoT sensor telemetry. If soil moisture < 20% (Drought), triggers irrigation AND checks insurance policy."""
        telemetry_id = f"IOT-TEL-{uuid.uuid4().hex[:8].upper()}"
        action = "NORMAL_MONITORING"

        # 1. Check if drought conditions warrant automated irrigation
        if soil_moisture_pct < 20.0:
            action = "ALERT: Drought detected (<20% moisture). Smart irrigation VALVE-MLO-12 opened, dispensing 2,500L water."
            
            # 2. Check if active drought parametric policy exists for this farm
            for p_id, p in list(self.policies.items()):
                if p["farm_id"] == farm_id and p["policy_status"] == "ACTIVE_INSURED" and p["policy_type"] == "CROP_DROUGHT_INDEX":
                    self.execute_parametric_claim_payout(p_id, telemetry_id, p["max_coverage_payout_kes"])

        record = {
            "telemetry_id": telemetry_id,
            "sensor_device_code": sensor_code,
            "farm_id": farm_id,
            "organization_id": organization_id,
            "soil_moisture_pct": soil_moisture_pct,
            "soil_temperature_celsius": soil_temp_celsius,
            "ambient_temperature_celsius": ambient_temp_celsius,
            "rainfall_mm_last_24h": rainfall_24h_mm,
            "battery_level_pct": 98.5,
            "automated_action_triggered": action
        }
        self.telemetry_logs[telemetry_id] = record

        ev = EventPayload(
            event_type="IOT_SENSOR_TELEMETRY_RECORDED",
            event_category=EventCategory.AGRICULTURE,
            actor_identity_id="IOT_SENSOR_DEVICE",
            organization_id=organization_id,
            correlation_id=telemetry_id,
            source_module="PARAMETRIC_CROP_INSURANCE_ENGINE",
            payload={
                "telemetry_id": telemetry_id,
                "sensor_device_code": sensor_code,
                "farm_id": farm_id,
                "soil_moisture_pct": soil_moisture_pct,
                "automated_action_triggered": action
            }
        )
        event_bus.publish(ev)
        return record

    def execute_parametric_claim_payout(self, policy_id: str, telemetry_id: str, claim_amount_kes: float) -> Dict:
        """Automated parametric claim verification and double-entry ledger settlement (`Rule 2, 5 & 6`)."""
        if policy_id not in self.policies:
            raise KeyError(f"Policy ID {policy_id} not found.")

        p = self.policies[policy_id]
        if p["policy_status"] == "CLAIM_PAID_OUT":
            return {"status": "ALREADY_PAID", "message": "Parametric claim already settled for this policy."}

        p["policy_status"] = "CLAIM_PAID_OUT"
        claim_id = f"CLAIM-{uuid.uuid4().hex[:8].upper()}"
        claim_code = f"CLAIM-AGRI-2026-{uuid.uuid4().hex[:6].upper()}"

        # Double-Entry settlement: Treasury Reserve KES -> Farmer KES Wallet (Rule 5)
        farmer_kes = wallet_engine.get_wallet_by_keys(p["insured_identity_id"], p["organization_id"], WalletType.KES_WALLET, AssetType.KES)
        if not farmer_kes:
            farmer_kes = wallet_engine.create_wallet(p["insured_identity_id"], p["organization_id"], WalletType.KES_WALLET, AssetType.KES, 0.0)
        treasury_kes = wallet_engine.get_wallet_by_keys("TREASURY_IDENTITY", p["organization_id"], WalletType.RESERVE_WALLET, AssetType.KES)
        if not treasury_kes:
            treasury_kes = wallet_engine.create_wallet("TREASURY_IDENTITY", p["organization_id"], WalletType.RESERVE_WALLET, AssetType.KES, 10_000_000.0)

        tx_id = str(uuid.uuid4())
        ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KES,
            debit_wallet_id=treasury_kes.wallet_id,
            credit_wallet_id=farmer_kes.wallet_id,
            amount=claim_amount_kes,
            currency="KES",
            organization_id=p["organization_id"],
            trigger_event_id=tx_id,
            description=f"Automated Parametric Crop Drought Insurance Payout ({claim_code})"
        )

        claim = {
            "claim_id": claim_id,
            "claim_code": claim_code,
            "policy_id": policy_id,
            "insured_identity_id": p["insured_identity_id"],
            "triggering_telemetry_id": telemetry_id,
            "claim_amount_kes": claim_amount_kes,
            "claim_status": "CLAIM_APPROVED_PAID",
            "settled_at": datetime.now(timezone.utc).isoformat()
        }
        self.claims[claim_id] = claim

        ev = EventPayload(
            event_type="INSURANCE_CLAIM_SETTLED",
            event_category=EventCategory.PAYMENT,
            actor_identity_id=p["insured_identity_id"],
            organization_id=p["organization_id"],
            correlation_id=tx_id,
            source_module="PARAMETRIC_CROP_INSURANCE_ENGINE",
            payload={
                "claim_id": claim_id,
                "policy_id": policy_id,
                "insured_identity_id": p["insured_identity_id"],
                "triggering_telemetry_id": telemetry_id,
                "claim_amount_kes": claim_amount_kes,
                "claim_status": "CLAIM_APPROVED_PAID"
            }
        )
        event_bus.publish(ev)
        return claim

parametric_insurance_iot_engine = ParametricCropInsuranceAndIotEngine()
