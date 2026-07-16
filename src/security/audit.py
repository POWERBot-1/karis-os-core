import json
import hashlib
from typing import Dict, List
from src.core.ledger_engine import ledger_engine
from src.core.event_bus import event_bus

class CryptographicAuditEngine:
    """
    KARIS OS™ Cryptographic Audit Engine (Section 38.5 & Rule 9).
    Scans the Universal Double-Entry Ledger and Universal Event Store to verify
    unbroken SHA-256 hash chaining and tamper-evidence.
    """
    def verify_ledger_chain(self) -> Dict:
        entries = ledger_engine.get_entries()
        if not entries:
            return {"status": "VERIFIED_CLEAN", "entries_checked": 0, "message": "Ledger is empty."}

        last_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        for i, entry in enumerate(entries, 1):
            # Recompute expected hash
            data = {
                "previous_hash": last_hash,
                "transaction_id": entry.transaction_id,
                "debit_wallet_id": entry.debit_wallet_id,
                "credit_wallet_id": entry.credit_wallet_id,
                "amount": entry.amount,
                "timestamp": entry.timestamp.isoformat()
            }
            encoded = json.dumps(data, sort_keys=True).encode("utf-8")
            expected_hash = hashlib.sha256(encoded).hexdigest()

            if entry.audit_hash != expected_hash:
                return {
                    "status": "TAMPER_DETECTED",
                    "entries_checked": i,
                    "failed_entry_id": entry.entry_id,
                    "expected_hash": expected_hash,
                    "stored_hash": entry.audit_hash,
                    "message": f"CRITICAL: Ledger entry {entry.entry_id} hash chain mismatch!"
                }
            last_hash = entry.audit_hash

        return {
            "status": "VERIFIED_CLEAN",
            "entries_checked": len(entries),
            "latest_audit_hash": last_hash,
            "message": "Universal Double-Entry Ledger SHA-256 chain is 100% intact."
        }

    def verify_event_store_integrity(self) -> Dict:
        events = event_bus.get_event_store()
        if not events:
            return {"status": "VERIFIED_CLEAN", "events_checked": 0, "message": "Event store is empty."}

        for i, ev in enumerate(events, 1):
            raw_data = {
                "event_id": ev.event_id,
                "event_type": ev.event_type,
                "correlation_id": ev.correlation_id,
                "payload": ev.payload,
                "timestamp": ev.timestamp.isoformat()
            }
            encoded = json.dumps(raw_data, sort_keys=True).encode("utf-8")
            expected_hash = hashlib.sha256(encoded).hexdigest()

            if ev.cryptographic_hash != expected_hash:
                return {
                    "status": "TAMPER_DETECTED",
                    "events_checked": i,
                    "failed_event_id": ev.event_id,
                    "expected_hash": expected_hash,
                    "stored_hash": ev.cryptographic_hash,
                    "message": f"CRITICAL: Event store record {ev.event_id} cryptographic hash mismatch!"
                }

        return {
            "status": "VERIFIED_CLEAN",
            "events_checked": len(events),
            "latest_event_hash": events[-1].cryptographic_hash if events else None,
            "message": "Universal Event Bus Store cryptographic hashes are 100% verified."
        }

audit_engine = CryptographicAuditEngine()
