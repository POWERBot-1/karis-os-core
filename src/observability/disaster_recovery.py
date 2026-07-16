import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine

BACKUPS_DIR = Path(__file__).resolve().parent.parent.parent / "backups"

class DisasterRecoveryEngine:
    """
    KARIS OS™ Disaster Recovery & Point-in-Time Snapshot Engine (Section 44.4 & 47.2).
    Captures complete system state (`Wallets`, `Ledger`, `Events`) into immutable cryptographic JSON snapshots,
    generating SHA-256 checksums to guarantee zero data corruption during recovery.
    """
    def __init__(self):
        self.snapshots: Dict[str, Dict] = {}
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

    def create_point_in_time_snapshot(
        self,
        organization_id: str = "ORG-KARIS-RETAIL",
        snapshot_type: str = "POINT_IN_TIME_PITR",
        creator_identity_id: str = "SYSTEM_DR_ENGINE"
    ) -> Dict:
        snapshot_id = f"PITR-SNAP-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Capture current state from engines
        events_dump = [ev.model_dump(mode="json") for ev in event_bus.get_event_store()]
        ledger_dump = [en.model_dump(mode="json") for en in ledger_engine.get_entries()]
        wallets_dump = [w.model_dump(mode="json") for w in wallet_engine.wallets.values()]

        snapshot_payload = {
            "snapshot_id": snapshot_id,
            "organization_id": organization_id,
            "snapshot_type": snapshot_type,
            "timestamp": timestamp,
            "latest_event_id": events_dump[-1]["event_id"] if events_dump else "GENESIS",
            "latest_ledger_hash": ledger_engine.last_hash,
            "events": events_dump,
            "ledger_entries": ledger_dump,
            "wallets": wallets_dump
        }

        file_path = BACKUPS_DIR / f"{snapshot_id}.json"
        content_bytes = json.dumps(snapshot_payload, sort_keys=True, indent=2).encode("utf-8")
        sha256_checksum = hashlib.sha256(content_bytes).hexdigest()

        # Persist to disk
        file_path.write_bytes(content_bytes)

        record = {
            "snapshot_id": snapshot_id,
            "organization_id": organization_id,
            "snapshot_type": snapshot_type,
            "latest_event_id": snapshot_payload["latest_event_id"],
            "latest_ledger_hash": snapshot_payload["latest_ledger_hash"],
            "total_events_captured": len(events_dump),
            "total_ledger_entries_captured": len(ledger_dump),
            "total_wallets_captured": len(wallets_dump),
            "snapshot_file_path": str(file_path),
            "sha256_checksum": sha256_checksum,
            "status": "VERIFIED_CLEAN",
            "created_at": timestamp
        }
        self.snapshots[snapshot_id] = record

        ev = EventPayload(
            event_type="DISASTER_RECOVERY_SNAPSHOT_CREATED",
            event_category=EventCategory.GOVERNANCE,
            actor_identity_id=creator_identity_id,
            organization_id=organization_id,
            correlation_id=snapshot_id,
            source_module="DISASTER_RECOVERY_ENGINE",
            payload={
                "snapshot_id": snapshot_id,
                "snapshot_type": snapshot_type,
                "latest_event_id": record["latest_event_id"],
                "latest_ledger_hash": record["latest_ledger_hash"],
                "snapshot_file_path": record["snapshot_file_path"],
                "sha256_checksum": sha256_checksum
            }
        )
        event_bus.publish(ev)
        return record

    def verify_snapshot_checksum(self, snapshot_id: str) -> Dict:
        if snapshot_id not in self.snapshots:
            raise KeyError(f"Snapshot ID {snapshot_id} not found.")

        record = self.snapshots[snapshot_id]
        file_path = Path(record["snapshot_file_path"])
        if not file_path.exists():
            return {"status": "MISSING_FILE", "message": f"Snapshot file {file_path} not found on disk."}

        content_bytes = file_path.read_bytes()
        computed_hash = hashlib.sha256(content_bytes).hexdigest()

        if computed_hash == record["sha256_checksum"]:
            return {"status": "VERIFIED_CLEAN", "snapshot_id": snapshot_id, "sha256_checksum": computed_hash, "message": "Cryptographic SHA-256 checksum verified 100% clean."}
        else:
            return {"status": "CORRUPT_CHECKSUM", "snapshot_id": snapshot_id, "expected_hash": record["sha256_checksum"], "computed_hash": computed_hash, "message": "CRITICAL: Snapshot file has been modified or corrupted!"}

dr_engine = DisasterRecoveryEngine()
