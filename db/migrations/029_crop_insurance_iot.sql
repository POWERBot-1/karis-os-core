-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 029: Parametric Crop Insurance & IoT Agri-Sensor Telemetry (Section 34.4 & 28.5)
-- ============================================================================

-- 1. PARAMETRIC CROP & LIVESTOCK INSURANCE POLICIES
CREATE TABLE IF NOT EXISTS crop_livestock_insurance_policies (
    policy_id TEXT PRIMARY KEY,
    policy_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'POL-AGRI-MACHAKOS-2026-01'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    insured_identity_id TEXT NOT NULL REFERENCES identities(identity_id) ON DELETE CASCADE,
    farm_id TEXT REFERENCES farms(farm_id),
    policy_type VARCHAR(50) NOT NULL CHECK (policy_type IN ('CROP_DROUGHT_INDEX', 'CROP_FLOOD_INDEX', 'LIVESTOCK_MORTALITY', 'HEALTH_PARAMETRIC', 'VEHICLE_LOGISTICS')),
    insured_acreage_or_head NUMERIC(10, 2) NOT NULL CHECK (insured_acreage_or_head > 0),
    premium_paid_kes NUMERIC(15, 2) NOT NULL CHECK (premium_paid_kes >= 0),
    max_coverage_payout_kes NUMERIC(15, 2) NOT NULL CHECK (max_coverage_payout_kes > 0),
    parametric_trigger_rule_json TEXT NOT NULL, -- e.g., {"trigger_metric": "SOIL_MOISTURE_PCT", "operator": "LT", "threshold": 20.0, "duration_hours": 72}
    policy_status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE_INSURED' CHECK (policy_status IN ('ACTIVE_INSURED', 'CLAIM_PAID_OUT', 'EXPIRED', 'CANCELLED')),
    effective_from TIMESTAMP NOT NULL,
    effective_until TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. IOT AGRICULTURAL SENSOR TELEMETRY RECORDS
CREATE TABLE IF NOT EXISTS iot_agricultural_sensor_telemetry (
    telemetry_id TEXT PRIMARY KEY,
    sensor_device_code VARCHAR(100) NOT NULL, -- e.g., 'IOT-MACHAKOS-SN-001'
    farm_id TEXT NOT NULL REFERENCES farms(farm_id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    soil_moisture_pct NUMERIC(5, 2) NOT NULL CHECK (soil_moisture_pct BETWEEN 0 AND 100),
    soil_temperature_celsius NUMERIC(5, 2) NOT NULL,
    ambient_temperature_celsius NUMERIC(5, 2) NOT NULL,
    rainfall_mm_last_24h NUMERIC(8, 2) DEFAULT 0.00 NOT NULL,
    battery_level_pct NUMERIC(5, 2) DEFAULT 100.00 NOT NULL,
    automated_action_triggered VARCHAR(255), -- e.g., 'IRRIGATION_VALVE_OPENED_2500L'
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. PARAMETRIC INSURANCE CLAIMS & AUTOMATED SETTLEMENT LOGS
CREATE TABLE IF NOT EXISTS parametric_insurance_claims (
    claim_id TEXT PRIMARY KEY,
    claim_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'CLAIM-AGRI-2026-89A'
    policy_id TEXT NOT NULL REFERENCES crop_livestock_insurance_policies(policy_id),
    insured_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    triggering_telemetry_id TEXT REFERENCES iot_agricultural_sensor_telemetry(telemetry_id),
    claim_amount_kes NUMERIC(15, 2) NOT NULL CHECK (claim_amount_kes > 0),
    trigger_reason_summary TEXT NOT NULL,
    claim_status VARCHAR(50) NOT NULL DEFAULT 'CLAIM_SUBMITTED' CHECK (
        claim_status IN ('CLAIM_SUBMITTED', 'PARAMETRIC_ASSESSMENT_VERIFIED', 'CLAIM_APPROVED_PAID', 'REJECTED_BELOW_THRESHOLD')
    ),
    ledger_transaction_id TEXT REFERENCES ledger_transactions(transaction_id),
    settled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_insurance_policies_farm ON crop_livestock_insurance_policies(farm_id, policy_status);
CREATE INDEX idx_iot_telemetry_farm_time ON iot_agricultural_sensor_telemetry(farm_id, recorded_at);
CREATE INDEX idx_parametric_claims_policy ON parametric_insurance_claims(policy_id, claim_status);
