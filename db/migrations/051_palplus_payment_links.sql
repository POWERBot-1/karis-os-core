-- ============================================================================
-- KARIS OS™ MIGRATION 051: PALPLUS & HOSTED PAYMENT LINKS ENGINE (SECTION 51)
-- ============================================================================
-- Establishes the database tables for hosted checkout URLs and temporary links:
-- 1. hosted_payment_links: Track temporary and permanent hosted payment URLs (`link.palpluss.com`)
-- 2. payment_link_transactions: Track reconciled PalPlus webhooks & double-entry hashes (`Rule 9`)
-- ============================================================================

CREATE TABLE IF NOT EXISTS hosted_payment_links (
    payment_link_id VARCHAR(64) PRIMARY KEY,
    provider VARCHAR(32) NOT NULL DEFAULT 'PALPLUS',
    external_link_url VARCHAR(255) NOT NULL UNIQUE,
    merchant_organization_id VARCHAR(64) NOT NULL REFERENCES organizations(organization_id) ON DELETE RESTRICT,
    created_by_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    target_order_id VARCHAR(64),
    amount_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE_TEMPORARY_LINK',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS payment_link_transactions (
    transaction_id VARCHAR(64) PRIMARY KEY,
    payment_link_id VARCHAR(64) NOT NULL REFERENCES hosted_payment_links(payment_link_id) ON DELETE RESTRICT,
    payer_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    amount_kes NUMERIC(15, 4) NOT NULL CHECK (amount_kes > 0),
    payment_method VARCHAR(32) NOT NULL DEFAULT 'PALPLUS_MPESA_EXPRESS',
    external_receipt_number VARCHAR(128) NOT NULL UNIQUE,
    reconciled_ledger_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payment_links_org ON hosted_payment_links(merchant_organization_id);
CREATE INDEX IF NOT EXISTS idx_payment_links_tx_link ON payment_link_transactions(payment_link_id);
