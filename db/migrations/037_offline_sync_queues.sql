-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 037: Mobile App & POS Terminal Offline Synchronization (Section 41.5 & 20.2)
-- ============================================================================

CREATE TABLE IF NOT EXISTS offline_sync_queues (
    offline_batch_id TEXT PRIMARY KEY,
    device_terminal_code VARCHAR(100) NOT NULL, -- e.g., 'POS-MLO-01', 'MOBILE-APP-KAMAU-01'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    cashier_or_user_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    offline_transactions_json TEXT NOT NULL, -- Array of offline checkout/inventory events
    total_transactions_in_batch INT NOT NULL CHECK (total_transactions_in_batch > 0),
    sync_status VARCHAR(50) NOT NULL DEFAULT 'PENDING_SYNC' CHECK (
        sync_status IN ('PENDING_SYNC', 'SYNCHRONIZED_SUCCESS', 'CONFLICT_REQUIRES_RECONCILIATION', 'FAILED_REJECTED')
    ),
    reconciliation_summary TEXT,
    client_device_timestamp TIMESTAMP NOT NULL,
    synchronized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_offline_sync_terminal_status ON offline_sync_queues(device_terminal_code, sync_status);
