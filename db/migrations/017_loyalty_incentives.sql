-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 017: Loyalty & Incentive Engine
-- Enforces: Section 26 (Loyalty & Incentive Engine)
-- ============================================================================

-- 1. LOYALTY PROMOTIONAL CAMPAIGNS
CREATE TABLE IF NOT EXISTS loyalty_campaigns (
    campaign_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    campaign_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'CAMP-MACHAKOS-HARVEST-2026', 'CAMP-MLOLONGO-2X'
    campaign_name VARCHAR(255) NOT NULL,
    description TEXT,
    target_stakeholder_type VARCHAR(50) NOT NULL CHECK (target_stakeholder_type IN (
        'CUSTOMERS', 'SUPPLIERS', 'RIDERS', 'SALES_AGENTS', 'CHVS', 'INVESTORS', 'ALL'
    )),
    reward_type VARCHAR(50) NOT NULL CHECK (reward_type IN (
        'LOYALTY_POINTS', 'KARIS_TOKENS_KRT', 'CASHBACK_KES', 'DISCOUNT_COUPON', 'FREE_DELIVERY'
    )),
    reward_multiplier NUMERIC(5, 2) DEFAULT 1.00 NOT NULL,
    bonus_fixed_amount NUMERIC(15, 2) DEFAULT 0.00 NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. LOYALTY REWARD GRANTS & REDEMPTION LOGS
CREATE TABLE IF NOT EXISTS loyalty_reward_grants (
    grant_id TEXT PRIMARY KEY,
    campaign_id TEXT REFERENCES loyalty_campaigns(campaign_id),
    recipient_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    trigger_event_id TEXT NOT NULL REFERENCES event_store(event_id),
    trigger_reason VARCHAR(100) NOT NULL, -- e.g., 'PURCHASE_COMPLETED', 'DELIVERY_COMPLETED', 'REFERRAL_CONFIRMED'
    reward_type VARCHAR(50) NOT NULL,
    points_or_tokens_awarded NUMERIC(15, 4) NOT NULL CHECK (points_or_tokens_awarded > 0),
    wallet_id TEXT REFERENCES wallets(wallet_id),
    ledger_entry_id TEXT REFERENCES ledger_entries(entry_id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_loyalty_campaigns_org_active ON loyalty_campaigns(organization_id, is_active);
CREATE INDEX idx_loyalty_reward_grants_recipient ON loyalty_reward_grants(recipient_identity_id, trigger_reason);
