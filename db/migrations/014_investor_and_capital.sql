-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 014: Investor & Capital Management Engine
-- Enforces: Section 25 (Investor & Capital Management Engine)
-- ============================================================================

-- 1. CAPITAL FUNDING POOLS
CREATE TABLE IF NOT EXISTS investment_pools (
    pool_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    pool_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'POOL-AGRI-GROWTH-2026', 'POOL-WORKING-CAPITAL'
    pool_name VARCHAR(255) NOT NULL,
    pool_category VARCHAR(100) NOT NULL CHECK (pool_category IN (
        'AGRICULTURE_GROWTH_FUND', 'WORKING_CAPITAL_FUND', 'CREDIT_FUND',
        'LOGISTICS_EXPANSION_FUND', 'HEALTHCARE_FUND', 'EMERGENCY_RESERVE_FUND'
    )),
    target_capital_kes NUMERIC(20, 2) NOT NULL CHECK (target_capital_kes > 0),
    total_capital_raised_kes NUMERIC(20, 2) DEFAULT 0.00 NOT NULL,
    min_investment_kes NUMERIC(15, 2) DEFAULT 10000.00 NOT NULL,
    expected_annual_roi_pct NUMERIC(5, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN_FOR_INVESTMENT' CHECK (status IN (
        'OPEN_FOR_INVESTMENT', 'FULLY_FUNDED', 'ACTIVE_DEPLOYMENT', 'MATURED', 'CLOSED'
    )),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. INVESTOR PARTICIPATION & KYC VERIFICATION
CREATE TABLE IF NOT EXISTS investor_allocations (
    allocation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pool_id UUID NOT NULL REFERENCES investment_pools(pool_id) ON DELETE RESTRICT,
    investor_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    kyc_status VARCHAR(50) NOT NULL DEFAULT 'VERIFIED' CHECK (kyc_status IN ('PENDING_KYC', 'VERIFIED', 'REJECTED')),
    capital_invested_kes NUMERIC(20, 2) NOT NULL CHECK (capital_invested_kes > 0),
    investment_units_owned NUMERIC(20, 4) NOT NULL CHECK (investment_units_owned > 0),
    allocated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ledger_transaction_id UUID REFERENCES ledger_transactions(transaction_id)
);

-- 3. RETURN DISTRIBUTIONS AUDIT LOG
CREATE TABLE IF NOT EXISTS investment_return_distributions (
    distribution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pool_id UUID NOT NULL REFERENCES investment_pools(pool_id),
    allocation_id UUID NOT NULL REFERENCES investor_allocations(allocation_id),
    investor_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    return_amount_kes NUMERIC(15, 2) NOT NULL CHECK (return_amount_kes > 0),
    krt_bonus_reward NUMERIC(15, 2) DEFAULT 0.00,
    distribution_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ledger_entry_id UUID REFERENCES ledger_entries(entry_id)
);

CREATE INDEX idx_investor_allocations_pool ON investor_allocations(pool_id);
CREATE INDEX idx_investor_allocations_investor ON investor_allocations(investor_identity_id);
