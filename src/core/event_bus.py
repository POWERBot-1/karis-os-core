import hashlib
import json
import threading
from typing import Callable, Dict, List
from src.domain.models import EventPayload

class UniversalEventBus:
    """
    KARIS OS™ Universal Event Bus & Immutable Event Store.
    Enforces Rule 1 (No Event -> No State Change), Rule 6, Rule 8, and Rule 9.
    """
    def __init__(self):
        self.event_store: List[EventPayload] = []
        self.subscribers: Dict[str, List[Callable[[EventPayload], None]]] = {}
        self._lock = threading.Lock()

    def _compute_cryptographic_hash(self, event: EventPayload) -> str:
        """Rule 9: Every event gets an immutable SHA-256 hash."""
        raw_data = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "correlation_id": event.correlation_id,
            "payload": event.payload,
            "timestamp": event.timestamp.isoformat()
        }
        encoded = json.dumps(raw_data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def subscribe(self, event_type: str, handler: Callable[[EventPayload], None]):
        """Register consumers (Rule Engine, Ledger Engine, Analytics, AI Gateway)."""
        with self._lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(handler)

    def publish(self, event: EventPayload) -> EventPayload:
        """
        Publishes an event, records it immutably in the store, and dispatches to subscribers.
        Rule 1: State changes only occur downstream after an event is published and stored.
        """
        with self._lock:
            # Calculate cryptographic hash for immutability and auditability
            event.cryptographic_hash = self._compute_cryptographic_hash(event)
            # Append to immutable store
            self.event_store.append(event)
            # Copy subscribers under lock
            handlers = list(self.subscribers.get(event.event_type, [])) + list(self.subscribers.get("*", []))
        
        # Dispatch to specific subscribers outside lock to avoid deadlock
        for handler in handlers:
            handler(event)
                
        return event

    def get_event_store(self) -> List[EventPayload]:
        with self._lock:
            return list(self.event_store)

# Global Singleton for in-memory / core engine simulation
event_bus = UniversalEventBus()
