-- ============================================================================
-- KARIS OS™ MIGRATION 053: KARIS LOOP™ SOCIAL INTELLIGENCE LAYER (SECTION 54)
-- ============================================================================
-- Establishes database tables and constraints for Vertical 19 (Karis Loop™):
-- 1. karis_loop_profiles: User, creator, and verified business profiles (`7 Graphs`)
-- 2. karis_loop_communities: Public/private/regional/business communities & treasury pools
-- 3. karis_loop_posts: 14 content types (`Video/Stories/Product Posts`) with shoppable SKU links
-- 4. karis_loop_tips_and_transactions: Reconciled KRT tips & shoppable checkouts (`Rule 9`)
-- 5. karis_loop_messages: Unified direct/group/AI assistant chat & smart notifications (`Rule 6`)
-- ============================================================================

CREATE TABLE IF NOT EXISTS karis_loop_profiles (
    profile_id VARCHAR(64) PRIMARY KEY,
    user_identity_id VARCHAR(64) NOT NULL UNIQUE REFERENCES identities(identity_id) ON DELETE RESTRICT,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(organization_id) ON DELETE RESTRICT,
    handle_username VARCHAR(128) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(32) NOT NULL DEFAULT 'CREATOR_USER',
    verified_status VARCHAR(32) NOT NULL DEFAULT 'VERIFIED_KYC_TIER_3',
    creator_tier VARCHAR(32) NOT NULL DEFAULT 'RISING_CREATOR',
    reputation_score INTEGER NOT NULL DEFAULT 150,
    total_krt_tips_received NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karis_loop_communities (
    community_id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(organization_id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    community_type VARCHAR(32) NOT NULL DEFAULT 'REGIONAL_AGRI_GUILD',
    region_county VARCHAR(64) NOT NULL DEFAULT 'Machakos County',
    creator_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    member_count INTEGER NOT NULL DEFAULT 1,
    treasury_krt_pool NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    moderation_mode VARCHAR(32) NOT NULL DEFAULT 'AI_ASSISTED_HUMAN_REVIEW',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karis_loop_posts (
    post_id VARCHAR(64) PRIMARY KEY,
    creator_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    community_id VARCHAR(64) NOT NULL REFERENCES karis_loop_communities(community_id) ON DELETE RESTRICT,
    content_type VARCHAR(32) NOT NULL DEFAULT 'SHORT_VIDEO',
    feed_category VARCHAR(32) NOT NULL DEFAULT 'FOR_YOU_TRENDING',
    caption_text TEXT NOT NULL,
    media_payload_json TEXT NOT NULL,
    linked_product_id VARCHAR(64),
    shoppable_price_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    likes_count INTEGER NOT NULL DEFAULT 0,
    tips_krt_total NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    ai_moderation_status VARCHAR(32) NOT NULL DEFAULT 'APPROVED_CLEAN',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karis_loop_tips_and_transactions (
    tip_id VARCHAR(64) PRIMARY KEY,
    post_id VARCHAR(64) NOT NULL REFERENCES karis_loop_posts(post_id) ON DELETE RESTRICT,
    tipper_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    creator_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    amount_krt NUMERIC(15, 4) NOT NULL CHECK (amount_krt > 0),
    transaction_type VARCHAR(32) NOT NULL DEFAULT 'CREATOR_TIP_KRT',
    reconciled_ledger_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karis_loop_messages (
    message_id VARCHAR(64) PRIMARY KEY,
    sender_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    receiver_identity_or_group_id VARCHAR(64) NOT NULL,
    chat_type VARCHAR(32) NOT NULL DEFAULT 'DIRECT_MESSAGE',
    message_body TEXT NOT NULL,
    ai_translated_text TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'DELIVERED',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_loop_profiles_user ON karis_loop_profiles(user_identity_id);
CREATE INDEX IF NOT EXISTS idx_loop_posts_creator ON karis_loop_posts(creator_identity_id);
CREATE INDEX IF NOT EXISTS idx_loop_posts_community ON karis_loop_posts(community_id);
CREATE INDEX IF NOT EXISTS idx_loop_tips_post ON karis_loop_tips_and_transactions(post_id);
CREATE INDEX IF NOT EXISTS idx_loop_messages_sender ON karis_loop_messages(sender_identity_id);
