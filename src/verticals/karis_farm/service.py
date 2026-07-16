import uuid
from typing import Dict, List, Optional
from src.domain.models import EventCategory, EventPayload, ProduceBatchModel
from src.core.event_bus import event_bus

class KarisFarmService:
    """
    KARIS OS™ Flagship Vertical: KARIS FARM™ Service.
    Enforces Section 28 (Agriculture & KARIS FARM Vertical).
    Manages Farm Operations, Crop Planning, Harvest Tracking, and Produce Traceability.
    """
    def __init__(self):
        self.farms: Dict[str, Dict] = {}
        self.crop_plans: Dict[str, Dict] = {}
        self.produce_batches: Dict[str, ProduceBatchModel] = {}
        self.traceability_records: Dict[str, Dict] = {}

    def register_farm(
        self,
        farmer_identity_id: str,
        organization_id: str,
        farm_name: str,
        region_county: str,
        total_acreage: float,
        cooperative_identity_id: Optional[str] = None
    ) -> Dict:
        farm_id = str(uuid.uuid4())
        farm = {
            "farm_id": farm_id,
            "organization_id": organization_id,
            "farmer_identity_id": farmer_identity_id,
            "cooperative_identity_id": cooperative_identity_id,
            "farm_name": farm_name,
            "region_county": region_county,
            "total_acreage": total_acreage,
            "certification_status": "GAP_CERTIFIED"
        }
        self.farms[farm_id] = farm

        # Emit FARM_REGISTERED event
        event = EventPayload(
            event_type="FARM_REGISTERED",
            event_category=EventCategory.AGRICULTURE,
            actor_identity_id=farmer_identity_id,
            organization_id=organization_id,
            correlation_id=farm_id,
            source_module="KARIS_FARM_ENGINE",
            payload=farm
        )
        event_bus.publish(event)
        return farm

    def log_harvest(
        self,
        farm_id: str,
        crop_type: str,
        quantity_kg: float,
        quality_grade: str,
        unit_cost_kes: float,
        plan_id: Optional[str] = None
    ) -> ProduceBatchModel:
        if farm_id not in self.farms:
            raise KeyError(f"Farm with ID {farm_id} not registered in KARIS FARM.")

        farm = self.farms[farm_id]
        batch_id = str(uuid.uuid4())
        batch_number = f"BATCH-FARM-{crop_type[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
        qr_code = f"KARIS-TRACE-QR-{batch_id[:8].upper()}"

        batch = ProduceBatchModel(
            batch_id=batch_id,
            product_id=f"PROD-{crop_type[:4].upper()}-001",
            organization_id=farm["organization_id"],
            supplier_identity_id=farm["farmer_identity_id"],
            batch_number=batch_number,
            quantity_available=quantity_kg,
            unit_cost=unit_cost_kes,
            quality_grade=quality_grade,
            traceability_qr_code=qr_code
        )
        self.produce_batches[batch_id] = batch

        # Store Traceability Lineage
        self.traceability_records[qr_code] = {
            "traceability_id": str(uuid.uuid4()),
            "batch_id": batch_id,
            "farm_id": farm_id,
            "farm_name": farm["farm_name"],
            "region_county": farm["region_county"],
            "farmer_identity_id": farm["farmer_identity_id"],
            "crop_type": crop_type,
            "harvest_quantity_kg": quantity_kg,
            "quality_grade": quality_grade,
            "traceability_qr_code": qr_code,
            "cooperative_identity_id": farm.get("cooperative_identity_id")
        }

        # Emit AGRICULTURE_HARVEST_COMPLETED event
        harvest_event = EventPayload(
            event_type="AGRICULTURE_HARVEST_COMPLETED",
            event_category=EventCategory.AGRICULTURE,
            actor_identity_id=farm["farmer_identity_id"],
            organization_id=farm["organization_id"],
            correlation_id=batch_id,
            source_module="KARIS_FARM_ENGINE",
            payload={
                "harvest_id": str(uuid.uuid4()),
                "farm_id": farm_id,
                "plan_id": plan_id or str(uuid.uuid4()),
                "crop_type": crop_type,
                "quantity_kg": quantity_kg,
                "quality_grade": quality_grade,
                "batch_number": batch_number,
                "traceability_qr_code": qr_code
            }
        )
        event_bus.publish(harvest_event)
        return batch

    def get_traceability_by_qr(self, qr_code: str) -> Optional[Dict]:
        return self.traceability_records.get(qr_code)

karis_farm_service = KarisFarmService()
