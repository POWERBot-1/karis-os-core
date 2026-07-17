-- ============================================================================
-- KARIS OS™ MIGRATION 055: KARISFX GLOBAL FINANCIAL ECOSYSTEM & KRT ECONOMY (SECTION 56 / VERTICAL 21)
-- ============================================================================
-- Establishes database tables and constraints for Vertical 21 (KARISFX™):
-- 1. karisfx_accounts: Unified multi-asset trading accounts with KRT Foundation, multi-currency wallets, & reputation
-- 2. karisfx_orders_trades: Multi-Asset trading platform across 16 global asset classes with KRT fee discounts
-- 3. karisfx_staking_positions: KRT Staking modules unlocking up to 60% fee discounts, AI priority & governance rights
-- 4. karisfx_rewards_history: Reward Engine tracking 10 ecosystem activities with anti-wash-trading velocity checks
-- 5. karisfx_marketplace_items: Strategy & AI Marketplace (Strategies, Bots, Courses, Signals) monetized via KRT
-- 6. karisfx_marketplace_purchases: KRT double-entry checkouts with 85/15 split settlement between creator & treasury
-- 7. karisfx_governance_proposals: Decentralized KRT tokenholder governance proposals with AI Rule 10 impact analysis
-- 8. karisfx_governance_votes: Immutable KRT-weighted voting records (`FOR`, `AGAINST`, `ABSTAIN`)
-- 9. karisfx_social_copy_links: Copy trading, follow relationships, leaderboard performance & live PnL sync
-- 10. karisfx_developer_apps: Developer platform API monetization for AI bots & analytics plugins via KRT
-- 11. karisfx_compliance_aml_logs: Zero Trust continuous AML/FIU monitoring, KYC Tier 3 tracking & tax reporting
-- ============================================================================

CREATE TABLE IF NOT EXISTS karisfx_accounts (
    account_id VARCHAR(64) PRIMARY KEY,
    identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    account_number VARCHAR(64) UNIQUE NOT NULL,
    account_tier VARCHAR(64) NOT NULL DEFAULT 'STANDARD',
    kyc_status VARCHAR(64) NOT NULL DEFAULT 'VERIFIED_TIER_3',
    krt_wallet_id VARCHAR(64) NOT NULL,
    kes_wallet_id VARCHAR(64) NOT NULL,
    usd_wallet_id VARCHAR(64) NOT NULL,
    eur_wallet_id VARCHAR(64) NOT NULL,
    gbp_wallet_id VARCHAR(64) NOT NULL,
    stablecoin_wallet_id VARCHAR(64) NOT NULL,
    rewards_wallet_id VARCHAR(64) NOT NULL,
    treasury_account_ref VARCHAR(128) NOT NULL,
    reputation_score INTEGER NOT NULL DEFAULT 100,
    mfa_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    device_trust_score NUMERIC(5, 2) NOT NULL DEFAULT 99.50,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karisfx_orders_trades (
    trade_id VARCHAR(64) PRIMARY KEY,
    account_id VARCHAR(64) NOT NULL REFERENCES karisfx_accounts(account_id) ON DELETE RESTRICT,
    asset_class VARCHAR(64) NOT NULL,
    symbol VARCHAR(64) NOT NULL,
    side VARCHAR(16) NOT NULL,
    order_type VARCHAR(32) NOT NULL DEFAULT 'MARKET',
    requested_units NUMERIC(18, 6) NOT NULL,
    execution_price NUMERIC(18, 6) NOT NULL,
    total_value_usd NUMERIC(18, 4) NOT NULL,
    leverage NUMERIC(6, 2) NOT NULL DEFAULT 1.00,
    base_fee_krt NUMERIC(15, 4) NOT NULL,
    fee_discount_pct NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    final_fee_krt NUMERIC(15, 4) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'EXECUTED_SETTLED',
    ledger_entry_id VARCHAR(64),
    executed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karisfx_staking_positions (
    staking_id VARCHAR(64) PRIMARY KEY,
    account_id VARCHAR(64) NOT NULL REFERENCES karisfx_accounts(account_id) ON DELETE RESTRICT,
    staking_tier VARCHAR(32) NOT NULL,
    staked_amount_krt NUMERIC(18, 4) NOT NULL,
    lockup_duration_days INTEGER NOT NULL,
    apy_pct NUMERIC(5, 2) NOT NULL,
    fee_discount_pct NUMERIC(5, 2) NOT NULL,
    ai_premium_unlocked BOOLEAN NOT NULL DEFAULT TRUE,
    governance_voting_power NUMERIC(18, 4) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    staked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    unlocks_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS karisfx_rewards_history (
    reward_id VARCHAR(64) PRIMARY KEY,
    account_id VARCHAR(64) NOT NULL REFERENCES karisfx_accounts(account_id) ON DELETE RESTRICT,
    activity_type VARCHAR(64) NOT NULL,
    reward_amount_krt NUMERIC(15, 4) NOT NULL,
    anti_abuse_status VARCHAR(64) NOT NULL DEFAULT 'VERIFIED_CLEAN',
    verification_hash VARCHAR(128) NOT NULL,
    awarded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karisfx_marketplace_items (
    item_id VARCHAR(64) PRIMARY KEY,
    creator_account_id VARCHAR(64) NOT NULL REFERENCES karisfx_accounts(account_id) ON DELETE RESTRICT,
    item_type VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    price_krt NUMERIC(15, 4) NOT NULL,
    historical_win_rate_pct NUMERIC(5, 2) DEFAULT NULL,
    sharpe_ratio NUMERIC(5, 2) DEFAULT NULL,
    total_subscribers INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(32) NOT NULL DEFAULT 'PUBLISHED',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karisfx_marketplace_purchases (
    purchase_id VARCHAR(64) PRIMARY KEY,
    item_id VARCHAR(64) NOT NULL REFERENCES karisfx_marketplace_items(item_id) ON DELETE RESTRICT,
    buyer_account_id VARCHAR(64) NOT NULL REFERENCES karisfx_accounts(account_id) ON DELETE RESTRICT,
    price_paid_krt NUMERIC(15, 4) NOT NULL,
    creator_payout_krt NUMERIC(15, 4) NOT NULL,
    treasury_fee_krt NUMERIC(15, 4) NOT NULL,
    ledger_entry_id VARCHAR(64) NOT NULL,
    purchased_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karisfx_governance_proposals (
    proposal_id VARCHAR(64) PRIMARY KEY,
    creator_account_id VARCHAR(64) NOT NULL REFERENCES karisfx_accounts(account_id) ON DELETE RESTRICT,
    category VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    ai_impact_summary TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE_VOTING',
    votes_for_krt NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    votes_against_krt NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    quorum_required_krt NUMERIC(18, 4) NOT NULL DEFAULT 100000.0000,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    voting_ends_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS karisfx_governance_votes (
    vote_id VARCHAR(64) PRIMARY KEY,
    proposal_id VARCHAR(64) NOT NULL REFERENCES karisfx_governance_proposals(proposal_id) ON DELETE RESTRICT,
    voter_account_id VARCHAR(64) NOT NULL REFERENCES karisfx_accounts(account_id) ON DELETE RESTRICT,
    vote_choice VARCHAR(16) NOT NULL,
    voting_power_krt NUMERIC(18, 4) NOT NULL,
    voted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karisfx_social_copy_links (
    copy_link_id VARCHAR(64) PRIMARY KEY,
    follower_account_id VARCHAR(64) NOT NULL REFERENCES karisfx_accounts(account_id) ON DELETE RESTRICT,
    master_trader_account_id VARCHAR(64) NOT NULL REFERENCES karisfx_accounts(account_id) ON DELETE RESTRICT,
    allocation_krt NUMERIC(18, 4) NOT NULL,
    copy_ratio NUMERIC(5, 2) NOT NULL DEFAULT 1.00,
    max_drawdown_stop_pct NUMERIC(5, 2) NOT NULL DEFAULT 15.00,
    total_pnl_krt NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karisfx_developer_apps (
    app_id VARCHAR(64) PRIMARY KEY,
    developer_account_id VARCHAR(64) NOT NULL REFERENCES karisfx_accounts(account_id) ON DELETE RESTRICT,
    app_name VARCHAR(255) NOT NULL,
    app_type VARCHAR(64) NOT NULL,
    api_key_hash VARCHAR(128) NOT NULL,
    monetization_fee_krt_per_call NUMERIC(10, 4) NOT NULL DEFAULT 1.0000,
    total_calls_served INTEGER NOT NULL DEFAULT 0,
    total_krt_earned NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karisfx_compliance_aml_logs (
    log_id VARCHAR(64) PRIMARY KEY,
    account_id VARCHAR(64) NOT NULL REFERENCES karisfx_accounts(account_id) ON DELETE RESTRICT,
    event_type VARCHAR(64) NOT NULL,
    transaction_amount_usd NUMERIC(18, 4) NOT NULL,
    aml_risk_score NUMERIC(5, 2) NOT NULL,
    jurisdiction_code VARCHAR(16) NOT NULL DEFAULT 'KE-EAC',
    cbk_fiu_flagged BOOLEAN NOT NULL DEFAULT FALSE,
    audit_notes TEXT NOT NULL,
    logged_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
