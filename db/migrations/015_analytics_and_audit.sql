-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 015: Analytics Warehouse, AI Risk Alerts & System Audit Engine
-- Enforces: Section 27 (Analytics & Risk Engine) & Section 38 (Security, Privacy & Compliance)
-- ============================================================================

-- 1. AI RISK & FRAUD DETECTION ALERTS
CREATE TABLE IF NOT EXISTS risk_anomaly_alerts (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    actor_identity_id UUID REFERENCES identities(identity_id),
    anomaly_type VARCHAR(100) NOT NULL CHECK (anomaly_type IN (
        'TRANSACTION_VELOCITY_ABUSE', 'WALLET_DRAIN_ATTEMPT', 'CREDIT_LIMIT_EXCEEDED',
        'UNUSUAL_HARVEST_YIELD', 'PRICE_MANIPULATION', 'SUSPICIOUS_DEVICE_LOGIN', 'ABNORMAL_TREASURY_MINT'
    )),
    severity VARCHAR(50) NOT NULL DEFAULT 'HIGH' CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    risk_score NUMERIC(5, 2) NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    description TEXT NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    investigation_status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (
        investigation_status IN ('PENDING', 'UNDER_INVESTIGATION', 'FALSE_POSITIVE', 'CONFIRMED_FRAUD', 'RESOLVED')
    )
);

-- 2. ENTERPRISE KPI MATERIALIZED ANALYTICS VIEW
CREATE TABLE IF NOT EXISTS daily_vertical_analytics_summary (
    summary_date DATE NOT NULL,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    vertical_type VARCHAR(100) NOT NULL,
    total_orders_placed INT DEFAULT 0 NOT NULL,
    total_revenue_kes NUMERIC(20, 2) DEFAULT 0.00 NOT NULL,
    total_krt_minted NUMERIC(20, 2) DEFAULT 0.00 NOT NULL,
    total_deliveries_completed INT DEFAULT 0 NOT NULL,
    active_users_count INT DEFAULT 0 NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (summary_date, organization_id, vertical_type)
);

-- 3. SYSTEM AUDIT VERIFICATION SNAPSHOTS
CREATE TABLE IF NOT EXISTS cryptographic_audit_checkpoints (
    checkpoint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    last_verified_event_id UUID NOT NULL REFERENCES event_store(event_id),
    last_verified_ledger_hash VARCHAR(64) NOT NULL,
    total_events_checked BIGINT NOT NULL,
    total_ledger_entries_checked BIGINT NOT NULL,
    integrity_status VARCHAR(50) NOT NULL DEFAULT 'VERIFIED_CLEAN' CHECK (
        integrity_status IN ('VERIFIED_CLEAN', 'TAMPER_DETECTED', 'CORRUPT_CHAIN')
    ),
    verification_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_risk_anomaly_alerts_status ON risk_anomaly_alerts(investigation_status, severity);
