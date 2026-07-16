import uuid
from typing import Dict
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus

class PosAiQueueAndShrinkageEngine:
    """
    KARIS OS™ AI-Assisted POS Queue Congestion & Retail Shrinkage Detection Engine (Section 20.3 & 30.5).
    Monitors active cashier line lengths, predicts queue bottlenecks, commands Express Terminal activation,
    and investigates inventory shrinkage discrepancies.
    """
    def __init__(self):
        self.queue_logs: Dict[str, Dict] = {}
        self.shrinkage_audits: Dict[str, Dict] = {}

    def monitor_pos_queue(
        self,
        store_id: str,
        terminal_id: str,
        active_customers_in_line: int,
        estimated_wait_time_minutes: float,
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        """Monitors active POS lines. Commands Express Lane activation if threshold exceeded."""
        if active_customers_in_line > 12 or estimated_wait_time_minutes > 8.0:
            status = "CRITICAL_BOTTLENECK"
            action = "ALERT: Open Express Terminals POS-MLO-02 and POS-MLO-03 immediately to clear bottleneck!"
        elif active_customers_in_line > 6 or estimated_wait_time_minutes > 4.0:
            status = "QUEUE_CONGESTION_DETECTED"
            action = "Recommend opening Express Terminal POS-MLO-02 to distribute queue load."
        elif active_customers_in_line > 3:
            status = "MODERATE_QUEUE"
            action = "Normal monitoring active."
        else:
            status = "NORMAL_FLOW"
            action = "Optimal cashier flow."

        log_id = f"POS-Q-{uuid.uuid4().hex[:8].upper()}"
        record = {
            "log_id": log_id,
            "store_id": store_id,
            "terminal_id": terminal_id,
            "active_customers_in_line": active_customers_in_line,
            "estimated_wait_time_minutes": estimated_wait_time_minutes,
            "congestion_status": status,
            "ai_recommendation_action": action
        }
        self.queue_logs[log_id] = record

        if status in ("QUEUE_CONGESTION_DETECTED", "CRITICAL_BOTTLENECK"):
            ev = EventPayload(
                event_type="POS_QUEUE_CONGESTION_DETECTED",
                event_category=EventCategory.COMMERCE,
                actor_identity_id="AI_POS_AGENT",
                organization_id=organization_id,
                correlation_id=log_id,
                source_module="AI_POS_QUEUE_SHRINKAGE_ENGINE",
                payload=record
            )
            event_bus.publish(ev)

        return record

    def audit_inventory_shrinkage(
        self,
        store_id: str,
        product_id: str,
        expected_system_quantity: float,
        physical_recount_quantity: float,
        unit_price_kes: float = 150.0,
        reason: str = "UNRECORDED_SPOILAGE",
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        """Calculates physical shrinkage discrepancies and generates governance audit reports."""
        discrepancy = round(expected_system_quantity - physical_recount_quantity, 4)
        loss_kes = round(max(discrepancy, 0.0) * unit_price_kes, 2)
        
        shrink_id = f"SHRINK-{uuid.uuid4().hex[:8].upper()}"
        record = {
            "shrinkage_id": shrink_id,
            "store_id": store_id,
            "product_id": product_id,
            "expected_system_quantity": expected_system_quantity,
            "physical_recount_quantity": physical_recount_quantity,
            "discrepancy_quantity": discrepancy,
            "estimated_loss_kes": loss_kes,
            "shrinkage_reason": reason,
            "investigation_status": "FLAGGED_FOR_AUDIT" if loss_kes > 5000.0 else "RESOLVED"
        }
        self.shrinkage_audits[shrink_id] = record
        return record

pos_ai_engine = PosAiQueueAndShrinkageEngine()
