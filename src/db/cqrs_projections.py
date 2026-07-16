import threading
from typing import Dict, List
from src.domain.models import EventPayload
from src.core.event_bus import event_bus

class CqrsReadModelEngine:
    """
    KARIS OS™ CQRS & Event-Driven Read Model Projections Engine (Section 37.3).
    Separates transactional writes (`Universal Ledger / Write Models`) from high-speed analytical reads (`CQRS Projections`).
    Subscribes to all domain events on the Universal Event Bus and asynchronously updates projection read models.
    """
    def __init__(self):
        self.vertical_order_summary: Dict[str, Dict] = {}
        self.esg_carbon_summary: Dict[str, float] = {"total_kg_co2": 0.0, "krt_green_tokens_minted": 0.0}
        self.recent_activity_stream: List[Dict] = []
        self._lock = threading.Lock()

        # Subscribe to Event Bus
        event_bus.subscribe("*", self._on_event_received)

    def _on_event_received(self, event: EventPayload):
        with self._lock:
            # Append to recent activity stream read model
            self.recent_activity_stream.append({
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "category": event.event_category.value,
                "module": event.source_module,
                "correlation_id": event.correlation_id,
                "crypto_hash": event.cryptographic_hash
            })
            if len(self.recent_activity_stream) > 100:
                self.recent_activity_stream.pop(0)

            # Update vertical summary read model on commerce/payment events
            if event.event_type in ("COMMERCE_ORDER_CREATED", "POS_CHECKOUT_COMPLETED", "MOBILITY_TRIP_COMPLETED"):
                org = event.organization_id
                if org not in self.vertical_order_summary:
                    self.vertical_order_summary[org] = {"total_orders": 0, "total_revenue_kes": 0.0}
                self.vertical_order_summary[org]["total_orders"] += 1
                
                amt = event.payload.get("total_kes_amount") or event.payload.get("total_fare_kes") or 0.0
                self.vertical_order_summary[org]["total_revenue_kes"] += float(amt)

            # Update ESG summary read model on carbon events
            if event.event_type == "ESG_CARBON_CREDIT_MINTED":
                co2 = event.payload.get("total_carbon_footprint_kg_co2", 0.0)
                krt_g = event.payload.get("krt_green_tokens_minted", 0.0)
                self.esg_carbon_summary["total_kg_co2"] = round(self.esg_carbon_summary["total_kg_co2"] + float(co2), 4)
                self.esg_carbon_summary["krt_green_tokens_minted"] = round(self.esg_carbon_summary["krt_green_tokens_minted"] + float(krt_g), 4)

    def get_projections_dashboard(self) -> Dict:
        with self._lock:
            return {
                "cqrs_read_model_status": "ONLINE_ACTIVE_SYNC",
                "vertical_order_summary": self.vertical_order_summary,
                "esg_carbon_summary": self.esg_carbon_summary,
                "stream_buffer_size": len(self.recent_activity_stream)
            }

cqrs_projections_engine = CqrsReadModelEngine()
