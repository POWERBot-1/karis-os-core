-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 044: Universal Double-Entry Ledger Reconciliation Sweeps (Section 37.4 & 10.4)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ledger_reconciliation_sweeps (
    sweep_id TEXT PRIMARY KEY,
    sweep_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'RECON-SWEEP-20260716-01'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    total_wallets_audited INT NOT NULL CHECK (total_wallets_audited >= 0),
    total_ledger_entries_audited INT NOT NULL CHECK (total_ledger_entries_audited >= 0),
    discrepancies_detected_count INT DEFAULT 0 NOT NULL,
    total_reversing_adjustments_kes NUMERIC(20, 2) DEFAULT 0.00 NOT NULL,
    reconciliation_status VARCHAR(50) NOT NULL DEFAULT '100PCT_MATHEMATICALLY_RECONCILED' CHECK (
        reconciliation_status IN ('100PCT_MATHEMATICALLY_RECONCILED', 'DISCREPANCIES_CORRECTED_VIA_REVERSING_ENTRY', 'UNDER_AUDIT')
    ),
    executed_by_identity_id TEXT REFERENCES identities(identity_id),
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_ledger_recon_org_status ON ledger_reconciliation_sweeps(organization_id, reconciliation_status, executed_at);
