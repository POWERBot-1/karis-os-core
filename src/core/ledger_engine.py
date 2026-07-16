import hashlib
import json
import threading
import uuid
from typing import List
from src.domain.models import AssetType, EventCategory, EventPayload, LedgerEntryModel
from src.core.event_bus import event_bus
from src.core.wallet_engine import wallet_engine

class UniversalLedgerEngine:
    """
    KARIS OS™ Universal Ledger Engine.
    Enforces Rule 5 (No direct wallet edits), Rule 8 (Timestamped), and Rule 9 (Immutable & Cryptographically Hashed).
    Every financial or reward movement across any vertical passes through this engine.
    """
    def __init__(self):
        self.entries: List[LedgerEntryModel] = []
        self.last_hash: str = "0000000000000000000000000000000000000000000000000000000000000000"
        self._lock = threading.Lock()

    def _compute_audit_hash(self, transaction_id: str, debit_wallet_id: str, credit_wallet_id: str, amount: float, timestamp_iso: str) -> str:
        data = {
            "previous_hash": self.last_hash,
            "transaction_id": transaction_id,
            "debit_wallet_id": debit_wallet_id,
            "credit_wallet_id": credit_wallet_id,
            "amount": amount,
            "timestamp": timestamp_iso
        }
        encoded = json.dumps(data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def record_transaction(
        self,
        transaction_id: str,
        asset_type: AssetType,
        debit_wallet_id: str,
        credit_wallet_id: str,
        amount: float,
        currency: str,
        organization_id: str,
        trigger_event_id: str,
        description: str
    ) -> LedgerEntryModel:
        """
        Validates double-entry movement, updates wallet engine balances, appends immutable ledger record,
        and publishes LEDGER_ENTRY_RECORDED to the Event Bus. Thread-safe atomic execution.
        """
        if amount <= 0:
            raise ValueError("KARIS OS™ Ledger Error: Transaction amount must be strictly greater than zero.")

        with self._lock:
            # 1. Execute wallet movement using secure token authorization (enforcing Rule 5)
            wallet_engine.execute_ledger_movement(
                debit_wallet_id=debit_wallet_id,
                credit_wallet_id=credit_wallet_id,
                amount=amount,
                caller_token="UNIVERSAL_LEDGER_ENGINE_AUTHORIZATION"
            )

            # 2. Compute cryptographic audit hash (enforcing Rule 9)
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            audit_hash = self._compute_audit_hash(
                transaction_id=transaction_id,
                debit_wallet_id=debit_wallet_id,
                credit_wallet_id=credit_wallet_id,
                amount=amount,
                timestamp_iso=now.isoformat()
            )
            self.last_hash = audit_hash

            # 3. Create immutable ledger entry model
            entry = LedgerEntryModel(
                transaction_id=transaction_id,
                asset_type=asset_type,
                debit_wallet_id=debit_wallet_id,
                credit_wallet_id=credit_wallet_id,
                amount=amount,
                currency=currency,
                organization_id=organization_id,
                event_id=trigger_event_id,
                timestamp=now,
                audit_hash=audit_hash
            )
            self.entries.append(entry)

        # 4. Emit LEDGER_ENTRY_RECORDED event outside lock so subscribers can run cleanly
        ledger_event = EventPayload(
            event_type="LEDGER_ENTRY_RECORDED",
            event_category=EventCategory.TREASURY,
            actor_identity_id="SYSTEM_LEDGER_ENGINE",
            organization_id=organization_id,
            correlation_id=transaction_id,
            source_module="UNIVERSAL_LEDGER_ENGINE",
            payload={
                "entry_id": entry.entry_id,
                "transaction_id": transaction_id,
                "asset_type": asset_type.value,
                "debit_wallet_id": debit_wallet_id,
                "credit_wallet_id": credit_wallet_id,
                "amount": amount,
                "currency": currency,
                "description": description,
                "audit_hash": audit_hash
            }
        )
        event_bus.publish(ledger_event)

        return entry

    def get_entries(self) -> List[LedgerEntryModel]:
        return self.entries

# Global Singleton for core simulation
ledger_engine = UniversalLedgerEngine()
