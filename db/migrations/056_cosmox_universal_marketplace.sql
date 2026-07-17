-- ============================================================================
-- KARIS OS™ MIGRATION 056: COSMOX UNIVERSAL MARKETPLACE & KRT ECONOMY (SECTION 57 / VERTICAL 22)
-- ============================================================================
-- Establishes database tables and constraints for Vertical 22 (COSMOX™):
-- 1. cosmox_accounts: Universal wallets (`fiat, krt, rewards, escrow, merchant, driver`), account roles & reputation
-- 2. cosmox_products: Physical & digital marketplace items with AI dynamic pricing elasticity
-- 3. cosmox_orders: Double-entry order book with escrow hold (`Rule 2`), split commissions (85/15 or 90/10) & cashback
-- 4. cosmox_deliveries: Logistics & Route AI tracking with strict Rule 4 driver escrow release upon delivery confirmation
-- 5. cosmox_referrals: Configurable referral network (`INDIVIDUAL, MERCHANT, DELIVERY_PARTNER`) & KRT rewards
-- 6. cosmox_staking_positions: KRT Staking modules (30/90/180/365 days) unlocking fee discounts & governance rights
-- 7. cosmox_digital_services: Developer platform monetization (AI tools, software, courses, APIs) via KRT checkouts
-- 8. cosmox_tokenomics_vesting: Tokenomics vesting schedules, reserve allocation budgets & burn tracking
-- 9. cosmox_governance_proposals: Decentralized community proposals with Rule 10 AI impact analysis
-- 10. cosmox_governance_votes: Immutable KRT-weighted voting records (`FOR`, `AGAINST`, `ABSTAIN`)
-- 11. cosmox_multisig_treasury_requests: High-value treasury requests requiring multi-signature RBAC approval (`Rule 10`)
-- ============================================================================

CREATE TABLE IF NOT EXISTS cosmox_accounts (
    account_id VARCHAR(64) PRIMARY KEY,
    identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    account_number VARCHAR(64) UNIQUE NOT NULL,
    account_type VARCHAR(64) NOT NULL DEFAULT 'BUYER', -- BUYER, MERCHANT, DRIVER, DEVELOPER
    kyc_status VARCHAR(64) NOT NULL DEFAULT 'VERIFIED_TIER_3',
    fiat_wallet_id VARCHAR(64) NOT NULL,
    krt_wallet_id VARCHAR(64) NOT NULL,
    rewards_wallet_id VARCHAR(64) NOT NULL,
    escrow_wallet_id VARCHAR(64) NOT NULL,
    merchant_wallet_id VARCHAR(64) NOT NULL,
    driver_wallet_id VARCHAR(64) NOT NULL,
    reputation_score INTEGER NOT NULL DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cosmox_products (
    product_id VARCHAR(64) PRIMARY KEY,
    seller_account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(64) NOT NULL DEFAULT 'PHYSICAL_GOODS',
    base_price_krt NUMERIC(15, 4) NOT NULL,
    base_price_fiat NUMERIC(15, 4) NOT NULL,
    currency VARCHAR(16) NOT NULL DEFAULT 'KES',
    inventory_count INTEGER NOT NULL DEFAULT 100,
    ai_dynamic_pricing_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    current_price_krt NUMERIC(15, 4) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cosmox_orders (
    order_id VARCHAR(64) PRIMARY KEY,
    buyer_account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    seller_account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    product_id VARCHAR(64) NOT NULL REFERENCES cosmox_products(product_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price_krt NUMERIC(15, 4) NOT NULL,
    total_price_krt NUMERIC(15, 4) NOT NULL,
    seller_payout_krt NUMERIC(15, 4) NOT NULL,
    platform_commission_krt NUMERIC(15, 4) NOT NULL,
    cashback_reward_krt NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    payment_method VARCHAR(32) NOT NULL DEFAULT 'KRT_WALLET',
    escrow_status VARCHAR(64) NOT NULL DEFAULT 'ESCROWED_PENDING_DELIVERY', -- ESCROWED_PENDING_DELIVERY, RELEASED_SETTLED, REFUNDED
    ledger_entry_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cosmox_deliveries (
    delivery_id VARCHAR(64) PRIMARY KEY,
    order_id VARCHAR(64) NOT NULL REFERENCES cosmox_orders(order_id) ON DELETE RESTRICT,
    driver_account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    origin_address VARCHAR(255) NOT NULL,
    destination_address VARCHAR(255) NOT NULL,
    distance_km NUMERIC(6, 2) NOT NULL DEFAULT 5.00,
    ai_optimized_route TEXT NOT NULL,
    driver_payout_fiat NUMERIC(15, 4) NOT NULL,
    driver_bonus_krt NUMERIC(15, 4) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ASSIGNED_IN_TRANSIT', -- ASSIGNED_IN_TRANSIT, DELIVERY_CONFIRMED, ESCROW_RELEASED
    escrow_ledger_hash VARCHAR(128) NOT NULL DEFAULT '',
    dispatched_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS cosmox_referrals (
    referral_id VARCHAR(64) PRIMARY KEY,
    referrer_account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    referred_account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    referral_type VARCHAR(64) NOT NULL DEFAULT 'INDIVIDUAL', -- INDIVIDUAL, MERCHANT, DELIVERY_PARTNER
    reward_krt NUMERIC(15, 4) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING_QUALIFICATION', -- PENDING_QUALIFICATION, REWARDED_CLEAN, BLOCKED
    ledger_entry_id VARCHAR(64) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cosmox_staking_positions (
    staking_id VARCHAR(64) PRIMARY KEY,
    account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    staking_tier VARCHAR(32) NOT NULL DEFAULT 'SILVER',
    staked_amount_krt NUMERIC(18, 4) NOT NULL,
    lockup_duration_days INTEGER NOT NULL DEFAULT 90,
    apy_pct NUMERIC(5, 2) NOT NULL,
    fee_discount_pct NUMERIC(5, 2) NOT NULL,
    voting_power_krt NUMERIC(18, 4) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    staked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    unlocks_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS cosmox_digital_services (
    service_id VARCHAR(64) PRIMARY KEY,
    developer_account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    service_type VARCHAR(64) NOT NULL DEFAULT 'AI_TOOL', -- AI_TOOL, SOFTWARE, API, COURSE, DIGITAL_PRODUCT
    api_endpoint_url VARCHAR(255) NOT NULL,
    price_krt_per_access NUMERIC(15, 4) NOT NULL DEFAULT 10.0000,
    total_subscribers INTEGER NOT NULL DEFAULT 0,
    total_krt_earned NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    status VARCHAR(32) NOT NULL DEFAULT 'PUBLISHED',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cosmox_tokenomics_vesting (
    vesting_id VARCHAR(64) PRIMARY KEY,
    beneficiary_account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    vesting_type VARCHAR(64) NOT NULL DEFAULT 'ECOSYSTEM_INCENTIVE_GRANT',
    total_krt_allocated NUMERIC(18, 4) NOT NULL,
    released_krt NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    duration_months INTEGER NOT NULL DEFAULT 12,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE_VESTING',
    start_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_release_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cosmox_governance_proposals (
    proposal_id VARCHAR(64) PRIMARY KEY,
    creator_account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    category VARCHAR(64) NOT NULL DEFAULT 'MARKETPLACE_POLICY',
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    ai_impact_summary TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE_VOTING',
    votes_for_krt NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    votes_against_krt NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    voting_ends_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS cosmox_governance_votes (
    vote_id VARCHAR(64) PRIMARY KEY,
    proposal_id VARCHAR(64) NOT NULL REFERENCES cosmox_governance_proposals(proposal_id) ON DELETE RESTRICT,
    voter_account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    vote_choice VARCHAR(16) NOT NULL,
    voting_power_krt NUMERIC(18, 4) NOT NULL,
    voted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cosmox_multisig_treasury_requests (
    request_id VARCHAR(64) PRIMARY KEY,
    requester_account_id VARCHAR(64) NOT NULL REFERENCES cosmox_accounts(account_id) ON DELETE RESTRICT,
    amount_krt NUMERIC(18, 4) NOT NULL,
    purpose TEXT NOT NULL,
    ai_risk_score NUMERIC(5, 2) NOT NULL DEFAULT 15.00,
    required_approvals INTEGER NOT NULL DEFAULT 2,
    current_approvals INTEGER NOT NULL DEFAULT 0,
    approver_ids_json TEXT NOT NULL DEFAULT '[]',
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING_MULTISIG', -- PENDING_MULTISIG, APPROVED_DISBURSED, REJECTED
    ledger_entry_id VARCHAR(64) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
