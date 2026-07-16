-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 002: Universal Ledger & Multi-Asset Wallet Engine
-- Enforces: Rule 5 (No direct wallet edits), Rule 8 (Timestamped), Rule 9 (Immutable)
-- Section 4 (Digital Economy Layer), Section 5 (Multi-Asset Wallets), Section 10 (Universal Ledger)
-- ============================================================================

-- 1. WALLETS TABLE
-- Every identity automatically owns isolated wallets per asset class across organizations.
CREATE TABLE IF NOT EXISTS wallets (
    wallet_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identity_id UUID NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE RESTRICT,
    wallet_type VARCHAR(50) NOT NULL CHECK (wallet_type IN (
        'KES_WALLET', 'KRT_WALLET', 'CREDIT_WALLET', 'LOYALTY_WALLET',
        'INVESTMENT_WALLET', 'SETTLEMENT_WALLET', 'RESERVE_WALLET',
        'LIQUIDITY_WALLET', 'REWARD_POOL', 'OPERATIONS_WALLET', 'EMERGENCY_RESERVE'
    )),
    asset_type VARCHAR(20) NOT NULL CHECK (asset_type IN ('KES', 'KRT', 'LOYALTY', 'CREDIT', 'INVESTMENT')),
    balance NUMERIC(20, 6) DEFAULT 0.000000 NOT NULL,
    locked_balance NUMERIC(20, 6) DEFAULT 0.000000 NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'FROZEN', 'LOCKED', 'CLOSED')),
    version BIGINT DEFAULT 1 NOT NULL, -- Optimistic locking to prevent race conditions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(identity_id, organization_id, wallet_type, asset_type)
);

-- 2. UNIVERSAL LEDGER TRANSACTIONS (Parent grouping for double-entry movements)
CREATE TABLE IF NOT EXISTS ledger_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL, -- Links directly to the Universal Event Bus
    correlation_id UUID NOT NULL,
    transaction_type VARCHAR(100) NOT NULL, -- e.g., 'PURCHASE_SETTLEMENT', 'KRT_REWARD_GRANT', 'LOAN_DISBURSEMENT'
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    vertical VARCHAR(100) NOT NULL, -- e.g., 'KARIS_FARM', 'KARIS_EATERY'
    initiated_by_identity_id UUID REFERENCES identities(identity_id),
    description TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    audit_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of (previous_hash + payload + timestamp)
    digital_signature TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'CONFIRMED' CHECK (status IN ('PENDING', 'CONFIRMED', 'REVERSED'))
);

-- 3. UNIVERSAL LEDGER ENTRIES (Append-Only Double-Entry Items)
-- Rule: Total Debits MUST exactly equal Total Credits for each transaction and asset type.
CREATE TABLE IF NOT EXISTS ledger_entries (
    entry_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES ledger_transactions(transaction_id) ON DELETE RESTRICT,
    asset_type VARCHAR(20) NOT NULL CHECK (asset_type IN ('KES', 'KRT', 'LOYALTY', 'CREDIT', 'INVESTMENT')),
    debit_wallet_id UUID NOT NULL REFERENCES wallets(wallet_id) ON DELETE RESTRICT,
    credit_wallet_id UUID NOT NULL REFERENCES wallets(wallet_id) ON DELETE RESTRICT,
    amount NUMERIC(20, 6) NOT NULL CHECK (amount > 0),
    currency VARCHAR(10) NOT NULL,
    exchange_rate NUMERIC(15, 6) DEFAULT 1.000000 NOT NULL,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    event_id UUID NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    audit_hash VARCHAR(64) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'CONFIRMED' CHECK (status IN ('CONFIRMED', 'REVERSED')),
    CONSTRAINT chk_different_wallets CHECK (debit_wallet_id != credit_wallet_id)
);

-- 4. WALLET OPERATION AUDIT LOGS
CREATE TABLE IF NOT EXISTS wallet_operations_log (
    operation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID NOT NULL REFERENCES wallets(wallet_id) ON DELETE RESTRICT,
    ledger_entry_id UUID REFERENCES ledger_entries(entry_id),
    operation_type VARCHAR(50) NOT NULL CHECK (operation_type IN (
        'CREDIT', 'DEBIT', 'FREEZE', 'LOCK', 'UNLOCK', 'RESERVE', 'RELEASE', 'EXPIRE'
    )),
    amount NUMERIC(20, 6) NOT NULL,
    previous_balance NUMERIC(20, 6) NOT NULL,
    new_balance NUMERIC(20, 6) NOT NULL,
    previous_locked NUMERIC(20, 6) NOT NULL,
    new_locked NUMERIC(20, 6) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    audit_hash VARCHAR(64) NOT NULL
);

-- 5. IMMUTABILITY ENFORCEMENT TRIGGERS (Rule 9: Nothing is deleted or overwritten in the ledger)
CREATE OR REPLACE FUNCTION prevent_ledger_mutation()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'KARIS OS™ Rule 9 Violation: Universal Ledger entries cannot be updated or deleted. Use reversing entries instead.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_immutable_ledger_entries_update
    BEFORE UPDATE OR DELETE ON ledger_entries
    FOR EACH ROW EXECUTE FUNCTION prevent_ledger_mutation();

CREATE TRIGGER trg_immutable_ledger_transactions_update
    BEFORE UPDATE OR DELETE ON ledger_transactions
    FOR EACH ROW EXECUTE FUNCTION prevent_ledger_mutation();

-- Indexing for high-throughput double-entry queries
CREATE INDEX idx_wallets_identity_org ON wallets(identity_id, organization_id);
CREATE INDEX idx_ledger_entries_transaction ON ledger_entries(transaction_id);
CREATE INDEX idx_ledger_entries_debit ON ledger_entries(debit_wallet_id);
CREATE INDEX idx_ledger_entries_credit ON ledger_entries(credit_wallet_id);
CREATE INDEX idx_ledger_entries_timestamp ON ledger_entries(timestamp);
