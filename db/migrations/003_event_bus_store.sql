-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 003: Universal Event Bus & Immutable Event Store
-- Enforces: Rule 1 (No Event -> No State Change), Rule 6, Rule 8, Rule 9
-- Section 9 (Universal Event Bus) & Section 37 (Database & Event Store)
-- ============================================================================

-- 1. IMMUTABLE EVENT STORE TABLE
-- The canonical record of all platform actions. System state can be reconstructed by replaying events.
CREATE TABLE IF NOT EXISTS event_store (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL, -- e.g., 'ORDER_CREATED', 'PAYMENT_CONFIRMED', 'TOKEN_GRANTED'
    event_category VARCHAR(50) NOT NULL CHECK (event_category IN (
        'IDENTITY', 'COMMERCE', 'PAYMENT', 'WALLET', 'CURRENCY', 'DELIVERY',
        'INVESTMENT', 'HEALTHCARE', 'MOBILITY', 'AGRICULTURE', 'TREASURY', 'GOVERNANCE'
    )),
    actor_identity_id UUID REFERENCES identities(identity_id),
    organization_id UUID REFERENCES organizations(organization_id),
    correlation_id UUID NOT NULL,
    parent_event_id UUID REFERENCES event_store(event_id),
    source_module VARCHAR(100) NOT NULL, -- e.g., 'API_GATEWAY', 'COMMERCE_ENGINE', 'WALLET_ENGINE'
    payload JSONB NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    risk_score NUMERIC(5, 2) DEFAULT 0.00,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    digital_signature TEXT,
    cryptographic_hash VARCHAR(64) NOT NULL
);

-- 2. EVENT BUS SUBSCRIBER DISPATCH STATUS TABLE
-- Tracks consumer delivery (Rule Engine, Ledger, Analytics, Notifications, AI Processing)
CREATE TABLE IF NOT EXISTS event_dispatch_status (
    dispatch_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES event_store(event_id) ON DELETE RESTRICT,
    consumer_name VARCHAR(100) NOT NULL, -- e.g., 'RULE_ENGINE', 'LEDGER_ENGINE', 'AI_GATEWAY'
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSED', 'FAILED', 'DEAD_LETTER')),
    retry_count INT DEFAULT 0 NOT NULL,
    last_error TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(event_id, consumer_name)
);

-- 3. IMMUTABILITY ENFORCEMENT TRIGGER FOR EVENT STORE
CREATE OR REPLACE FUNCTION prevent_event_store_mutation()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'KARIS OS™ Rule 9 Violation: Events in the Universal Event Store are immutable and cannot be updated or deleted.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_immutable_event_store
    BEFORE UPDATE OR DELETE ON event_store
    FOR EACH ROW EXECUTE FUNCTION prevent_event_store_mutation();

-- High-performance indexing for event bus processing and correlation tracing
CREATE INDEX idx_event_store_type ON event_store(event_type);
CREATE INDEX idx_event_store_correlation ON event_store(correlation_id);
CREATE INDEX idx_event_store_actor ON event_store(actor_identity_id);
CREATE INDEX idx_event_store_org ON event_store(organization_id);
CREATE INDEX idx_event_store_timestamp ON event_store(timestamp);
CREATE INDEX idx_event_dispatch_status_pending ON event_dispatch_status(consumer_name, status) WHERE status = 'PENDING';
