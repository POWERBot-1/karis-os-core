import uuid
from datetime import datetime, timezone
from typing import Dict
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus

class AiSupplyChainBottleneckEngine:
    """
    KARIS OS™ AI-Powered Supply Chain Bottleneck & Dynamic Route Bypass Engine (Section 27.4 & 13.4).
    Monitors transit delays and inventory backlogs across East African distribution corridors (`Machakos-Nairobi Highway`),
    detecting bottlenecks and calculating dynamic route bypass plans under Rule 10 human approval gates.
    """
    def __init__(self):
        self.bottlenecks: Dict[str, Dict] = {}

    def analyze_network_supply_chain_bottlenecks(
        self,
        corridor_code: str = "CORRIDOR-MACHAKOS-NAIROBI-A104",
        active_transit_delay_hours: float = 8.5,
        backlogged_crates_count: int = 650,
        organization_id: str = "ORG-KARIS-FARM"
    ) -> Dict:
        if active_transit_delay_hours > 6.0 and backlogged_crates_count > 500:
            status = "CRITICAL_TRANSIT_BOTTLENECK_DETECTED"
            action = "ALERT: Highway A104 gridlock delay (8.5h). Re-routing incoming refrigerated trucks via Kangundo bypass (`BYPASS_VIA_KANGUNDO_ROUTE`) to Mlolongo Edge Hub."
        elif active_transit_delay_hours > 3.0:
            status = "MODERATE_CONGESTION"
            action = "Recommend staggering truck dispatch times by 45 minutes."
        else:
            status = "NORMAL_FLOW"
            action = "Corridor transit speeds nominal."

        b_id = f"BOTTLENECK-{uuid.uuid4().hex[:8].upper()}"
        record = {
            "bottleneck_id": b_id,
            "organization_id": organization_id,
            "warehouse_or_corridor_code": corridor_code,
            "active_transit_delay_hours": active_transit_delay_hours,
            "backlogged_crates_count": backlogged_crates_count,
            "bottleneck_status": status,
            "ai_recommended_bypass_action": action,
            "approval_status": "PENDING_HUMAN_APPROVAL",
            "detected_at": datetime.now(timezone.utc).isoformat()
        }
        self.bottlenecks[b_id] = record

        if status == "CRITICAL_TRANSIT_BOTTLENECK_DETECTED":
            ev = EventPayload(
                event_type="SUPPLY_CHAIN_BOTTLENECK_DETECTED",
                event_category=EventCategory.DELIVERY,
                actor_identity_id="AI_SUPPLY_CHAIN_AGENT",
                organization_id=organization_id,
                correlation_id=b_id,
                source_module="AI_SUPPLY_CHAIN_BOTTLENECK_ENGINE",
                payload={
                    "bottleneck_id": b_id,
                    "corridor_code": corridor_code,
                    "transit_delay_hours": active_transit_delay_hours,
                    "backlogged_crates": backlogged_crates_count,
                    "recommended_bypass_action": action,
                    "status": status
                }
            )
            event_bus.publish(ev)

        return record

supply_chain_bottleneck_engine = AiSupplyChainBottleneckEngine()
