-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 022: AI Emergency Medical Ambulance Dispatching & Fleet Proximity (Section 32.8 & 33.5)
-- ============================================================================

CREATE TABLE IF NOT EXISTS emergency_ambulance_units (
    ambulance_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    unit_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'AMB-MACHAKOS-ALS-01'
    vehicle_registration VARCHAR(50) UNIQUE NOT NULL,
    life_support_tier VARCHAR(50) NOT NULL CHECK (
        life_support_tier IN ('BASIC_LIFE_SUPPORT_BLS', 'ADVANCED_LIFE_SUPPORT_ALS', 'NEONATAL_ICU_MOBILE')
    ),
    current_gps_coordinates VARCHAR(100) NOT NULL, -- e.g., '-1.3564,36.9321'
    assigned_paramedic_identity_id TEXT REFERENCES identities(identity_id),
    oxygen_cylinder_level_pct NUMERIC(5, 2) DEFAULT 100.00 NOT NULL,
    defibrillator_equipped BOOLEAN DEFAULT TRUE NOT NULL,
    readiness_status VARCHAR(50) NOT NULL DEFAULT 'AVAILABLE_ON_STANDBY' CHECK (
        readiness_status IN ('AVAILABLE_ON_STANDBY', 'DISPATCHED_EN_ROUTE', 'PATIENT_ON_BOARD', 'AT_HOSPITAL', 'MAINTENANCE')
    ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_ambulance_units_status_tier ON emergency_ambulance_units(readiness_status, life_support_tier);
