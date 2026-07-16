-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 021: Disaster Recovery Point-in-Time Snapshots (Section 44.4 & 47.2)
-- ============================================================================

CREATE TABLE IF NOT EXISTS disaster_recovery_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    snapshot_type VARCHAR(50) NOT NULL DEFAULT 'POINT_IN_TIME_PITR' CHECK (
        snapshot_type IN ('POINT_IN_TIME_PITR', 'DAILY_AUTOMATED', 'PRE_DEPLOYMENT_CHECKPOINT', 'EMERGENCY_BACKUP')
    ),
    latest_event_id TEXT NOT NULL REFERENCES event_store(event_id),
    latest_ledger_hash VARCHAR(64) NOT NULL,
    total_events_captured BIGINT NOT NULL,
    total_ledger_entries_captured BIGINT NOT NULL,
    total_wallets_captured BIGINT NOT NULL,
    snapshot_file_path TEXT NOT NULL,
    sha256_checksum VARCHAR(64) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'VERIFIED_CLEAN' CHECK (
        status IN ('VERIFIED_CLEAN', 'CORRUPT_CHECKSUM', 'ARCHIVED')
    ),
    created_by_identity_id TEXT REFERENCES identities(identity_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_disaster_recovery_type_status ON disaster_recovery_snapshots(snapshot_type, status);
