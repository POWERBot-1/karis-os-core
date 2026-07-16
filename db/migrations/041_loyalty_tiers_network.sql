-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 041: Customer Loyalty Tier Auto-Upgrades & Cross-Merchant Network Clearing (Section 23.2 & 18)
-- ============================================================================

-- 1. CUSTOMER LIFECYCLE LOYALTY TIER RECORDS
CREATE TABLE IF NOT EXISTS customer_loyalty_tier_records (
    tier_record_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL UNIQUE REFERENCES identities(identity_id) ON DELETE CASCADE,
    current_tier VARCHAR(50) NOT NULL DEFAULT 'SILVER_STANDARD' CHECK (
        current_tier IN ('SILVER_STANDARD', 'GOLD_PREMIUM', 'PLATINUM_VIP', 'LIFETIME_CHAMPION_VIP')
    ),
    total_lifetime_spend_kes NUMERIC(20, 2) DEFAULT 0.00 NOT NULL,
    total_krt_balance_held NUMERIC(20, 4) DEFAULT 0.0000 NOT NULL,
    rebate_delivery_fee_pct NUMERIC(5, 2) DEFAULT 0.00 NOT NULL, -- e.g., 15.00% free delivery rebate for PLATINUM_VIP
    last_upgraded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. CROSS-MERCHANT NETWORK EFFECT REDEMPTION SETTLEMENTS
CREATE TABLE IF NOT EXISTS cross_merchant_network_redemptions (
    redemption_id TEXT PRIMARY KEY,
    redemption_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'NET-RED-2026-89A1'
    customer_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    source_organization_id TEXT NOT NULL REFERENCES organizations(organization_id), -- e.g., where KRT was earned (KARIS FARM)
    target_organization_id TEXT NOT NULL REFERENCES organizations(organization_id), -- e.g., where KRT is spent (KARIS Eatery)
    krt_tokens_redeemed NUMERIC(15, 4) NOT NULL CHECK (krt_tokens_redeemed > 0),
    kes_equivalent_value NUMERIC(15, 2) NOT NULL CHECK (kes_equivalent_value > 0),
    inter_org_ledger_tx_id TEXT REFERENCES ledger_transactions(transaction_id),
    clearing_status VARCHAR(50) NOT NULL DEFAULT 'CLEARED_SETTLED' CHECK (
        clearing_status IN ('CLEARED_SETTLED', 'PENDING_RECONCILIATION', 'REJECTED_INSUFFICIENT_KRT')
    ),
    settled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_loyalty_tiers_spend ON customer_loyalty_tier_records(current_tier, total_lifetime_spend_kes);
CREATE INDEX idx_network_redemptions_orgs ON cross_merchant_network_redemptions(source_organization_id, target_organization_id);
