-- ============================================================================
-- KARIS OS™ MIGRATION 049: POWER BOT X - THE AUTONOMOUS AI PREDICTION ECONOMY
-- ============================================================================
-- Establishes the database tables and constraints for Power BOT X:
-- 1. power_bot_fixtures: Track prediction matches, tactical form analysis & status
-- 2. power_bot_predictions: User prediction entries backed by KRT escrow (`Rule 9`)
-- 3. power_bot_leagues: Private, County (`Machakos vs Nairobi`), and National leagues
-- 4. power_bot_league_members: Membership & win-rate metrics inside prediction leagues
-- 5. power_bot_reputation_profiles: Non-financial reputation graph (`Reputation unlocks experiences`)
-- 6. power_bot_agent_campaigns: AI-generated localized marketing content (`Living AI Content Engine`)
-- 7. power_bot_digital_twin_snapshots: Real-time ecosystem simulation & self-evolving AI recommendations
-- ============================================================================

CREATE TABLE IF NOT EXISTS power_bot_fixtures (
    fixture_id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(64) NOT NULL,
    start_time_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'UPCOMING',
    odds_or_confidence VARCHAR(255),
    form_analysis_json TEXT,
    settlement_outcome VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS power_bot_predictions (
    prediction_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    fixture_id VARCHAR(64) NOT NULL REFERENCES power_bot_fixtures(fixture_id) ON DELETE RESTRICT,
    predicted_outcome VARCHAR(64) NOT NULL,
    stake_krt NUMERIC(15, 4) NOT NULL CHECK (stake_krt >= 0),
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING_SETTLEMENT',
    potential_payout_krt NUMERIC(15, 4) NOT NULL CHECK (potential_payout_krt >= 0),
    actual_payout_krt NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    reputation_earned INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS power_bot_leagues (
    league_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    league_type VARCHAR(32) NOT NULL DEFAULT 'PRIVATE',
    county VARCHAR(64),
    creator_user_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    member_count INTEGER NOT NULL DEFAULT 1,
    prize_pool_krt NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS power_bot_league_members (
    membership_id VARCHAR(64) PRIMARY KEY,
    league_id VARCHAR(64) NOT NULL REFERENCES power_bot_leagues(league_id) ON DELETE RESTRICT,
    user_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    reputation_score INTEGER NOT NULL DEFAULT 100,
    total_predictions INTEGER NOT NULL DEFAULT 0,
    win_rate NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    joined_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_power_bot_league_member UNIQUE (league_id, user_id)
);

CREATE TABLE IF NOT EXISTS power_bot_reputation_profiles (
    profile_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL UNIQUE REFERENCES identities(identity_id) ON DELETE RESTRICT,
    fair_participation_score INTEGER NOT NULL DEFAULT 100,
    account_longevity_days INTEGER NOT NULL DEFAULT 1,
    verified_identity_bonus INTEGER NOT NULL DEFAULT 50,
    community_engagement_score INTEGER NOT NULL DEFAULT 50,
    referral_count INTEGER NOT NULL DEFAULT 0,
    merchant_activity_score INTEGER NOT NULL DEFAULT 0,
    total_reputation_points INTEGER NOT NULL DEFAULT 200,
    tier VARCHAR(32) NOT NULL DEFAULT 'SCOUT',
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS power_bot_agent_campaigns (
    campaign_id VARCHAR(64) PRIMARY KEY,
    agent_user_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    content_type VARCHAR(64) NOT NULL,
    target_channel VARCHAR(32) NOT NULL DEFAULT 'WHATSAPP_STATUS',
    local_language VARCHAR(32) NOT NULL DEFAULT 'EN_SWAHILI_SHENG',
    media_payload_json TEXT NOT NULL,
    predicted_conversion_rate NUMERIC(5, 2) NOT NULL DEFAULT 15.50,
    actual_conversions INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS power_bot_digital_twin_snapshots (
    snapshot_id VARCHAR(64) PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    treasury_health_score NUMERIC(5, 2) NOT NULL DEFAULT 98.50,
    krt_circulation_total NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    active_predictions_count INTEGER NOT NULL DEFAULT 0,
    agent_network_size INTEGER NOT NULL DEFAULT 0,
    merchant_krt_velocity NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    fraud_alert_level VARCHAR(32) NOT NULL DEFAULT 'NORMAL',
    policy_simulation_parameters_json TEXT,
    ai_policy_recommendations_json TEXT,
    admin_approval_status VARCHAR(32) NOT NULL DEFAULT 'PENDING_RBAC_APPROVAL'
);

CREATE INDEX IF NOT EXISTS idx_power_bot_predictions_user ON power_bot_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_power_bot_predictions_fixture ON power_bot_predictions(fixture_id);
CREATE INDEX IF NOT EXISTS idx_power_bot_league_members_league ON power_bot_league_members(league_id);
CREATE INDEX IF NOT EXISTS idx_power_bot_reputation_user ON power_bot_reputation_profiles(user_id);
