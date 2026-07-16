-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 027: AI Fraud Detection & Transaction Velocity Anomaly Engine (Section 38.6)
-- ============================================================================

-- 1. REAL-TIME FRAUD VELOCITY MONITORING LOGS
CREATE TABLE IF NOT EXISTS fraud_velocity_monitoring_logs (
    velocity_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL REFERENCES identities(identity_id) ON DELETE CASCADE,
    wallet_id TEXT REFERENCES wallets(wallet_id),
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    transaction_type VARCHAR(50) NOT NULL,
    amount_kes NUMERIC(20, 2) NOT NULL,
    device_fingerprint VARCHAR(100) NOT NULL,
    location_gps_coordinates VARCHAR(100) NOT NULL, -- e.g., '-1.3564,36.9321'
    previous_gps_coordinates VARCHAR(100),
    seconds_since_previous_tx NUMERIC(10, 2),
    geodesic_distance_from_previous_km NUMERIC(10, 2),
    calculated_travel_speed_kmh NUMERIC(10, 2),
    fraud_risk_score NUMERIC(5, 2) NOT NULL CHECK (fraud_risk_score BETWEEN 0 AND 100),
    flagged_anomaly_type VARCHAR(100) CHECK (flagged_anomaly_type IN (
        'NORMAL_VELOCITY', 'GEOGRAPHIC_VELOCITY_ABUSE_IMPOSSIBLE_TRAVEL',
        'TRANSACTION_VELOCITY_BRUTE_FORCE', 'DEVICE_FINGERPRINT_BLACKLISTED',
        'TOKEN_MANIPULATION_ATTEMPT', 'CREDIT_DRAW_ABUSE'
    )),
    action_taken VARCHAR(100) NOT NULL CHECK (action_taken IN (
        'CLEARED_PROCEED', 'FLAGGED_MONITORING', 'FROZEN_WALLET_AND_SAR_ISSUED'
    )),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. FRAUD INVESTIGATION CASES (Risk Operations)
CREATE TABLE IF NOT EXISTS fraud_investigation_cases (
    case_id TEXT PRIMARY KEY,
    case_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'FRAUD-CASE-2026-89A1'
    velocity_id TEXT NOT NULL REFERENCES fraud_velocity_monitoring_logs(velocity_id),
    identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    fraud_vector VARCHAR(100) NOT NULL,
    risk_score NUMERIC(5, 2) NOT NULL,
    investigation_status VARCHAR(50) NOT NULL DEFAULT 'FLAGGED_FROZEN' CHECK (
        investigation_status IN ('FLAGGED_FROZEN', 'UNDER_INVESTIGATION', 'CONFIRMED_FRAUD_REVOKED', 'CLEARED_RESTORED')
    ),
    investigated_by_identity_id TEXT REFERENCES identities(identity_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_fraud_velocity_identity_time ON fraud_velocity_monitoring_logs(identity_id, recorded_at);
CREATE INDEX idx_fraud_cases_status_score ON fraud_investigation_cases(investigation_status, risk_score);
