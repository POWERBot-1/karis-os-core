-- ============================================================================
-- KARIS OS™ MIGRATION 050: KARIS ENERGY & SMART SOLAR GRID™ (SECTION 50)
-- ============================================================================
-- Establishes the database tables and constraints for Vertical 15:
-- 1. energy_solar_installations: Track PAYG solar home systems, battery banks & solar pumps
-- 2. energy_smart_meter_telemetry: IoT telemetry logging daily kWh generation, battery % & feed-in
-- 3. energy_payg_installments: PAYG token installments paid in KRT / KES (`Rule 2 & 9`)
-- 4. energy_microgrid_peer_transfers: P2P microgrid solar energy trading between farmers/buildings
-- ============================================================================

CREATE TABLE IF NOT EXISTS energy_solar_installations (
    installation_id VARCHAR(64) PRIMARY KEY,
    owner_user_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(organization_id) ON DELETE RESTRICT,
    device_serial_number VARCHAR(128) NOT NULL UNIQUE,
    device_type VARCHAR(64) NOT NULL DEFAULT 'SOLAR_IRRIGATION_PUMP',
    gps_location VARCHAR(128) NOT NULL DEFAULT '(-1.3850, 36.9400)',
    rated_capacity_watts NUMERIC(10, 2) NOT NULL DEFAULT 1500.00,
    payg_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE_UNLOCKED',
    daily_token_rate_krt NUMERIC(15, 4) NOT NULL DEFAULT 50.0000,
    battery_charge_pct NUMERIC(5, 2) NOT NULL DEFAULT 100.00,
    total_kwh_generated NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS energy_smart_meter_telemetry (
    telemetry_id VARCHAR(64) PRIMARY KEY,
    installation_id VARCHAR(64) NOT NULL REFERENCES energy_solar_installations(installation_id) ON DELETE RESTRICT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    kwh_generated_today NUMERIC(10, 4) NOT NULL DEFAULT 0.0000,
    kwh_consumed_today NUMERIC(10, 4) NOT NULL DEFAULT 0.0000,
    battery_voltage_v NUMERIC(6, 2) NOT NULL DEFAULT 24.50,
    soil_moisture_pct NUMERIC(5, 2) NOT NULL DEFAULT 45.00,
    microgrid_feed_in_kwh NUMERIC(10, 4) NOT NULL DEFAULT 0.0000,
    status VARCHAR(32) NOT NULL DEFAULT 'NORMAL'
);

CREATE TABLE IF NOT EXISTS energy_payg_installments (
    installment_id VARCHAR(64) PRIMARY KEY,
    installation_id VARCHAR(64) NOT NULL REFERENCES energy_solar_installations(installation_id) ON DELETE RESTRICT,
    payer_user_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    amount_krt NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    amount_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    payment_method VARCHAR(32) NOT NULL DEFAULT 'KRT_WALLET',
    days_unlocked INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(32) NOT NULL DEFAULT 'SETTLED_UNLOCKED',
    settled_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS energy_microgrid_peer_transfers (
    transfer_id VARCHAR(64) PRIMARY KEY,
    seller_user_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    buyer_user_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    kwh_traded NUMERIC(10, 4) NOT NULL CHECK (kwh_traded > 0),
    price_per_kwh_krt NUMERIC(10, 4) NOT NULL DEFAULT 12.5000,
    total_amount_krt NUMERIC(15, 4) NOT NULL CHECK (total_amount_krt > 0),
    audit_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_energy_solar_owner ON energy_solar_installations(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_energy_telemetry_inst ON energy_smart_meter_telemetry(installation_id);
CREATE INDEX IF NOT EXISTS idx_energy_payg_inst ON energy_payg_installments(installation_id);
CREATE INDEX IF NOT EXISTS idx_energy_peer_transfers_seller ON energy_microgrid_peer_transfers(seller_user_id);
