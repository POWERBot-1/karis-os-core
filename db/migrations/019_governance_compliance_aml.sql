-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 019: Operational Governance, AML/KYC & KRA eTIMS Tax Invoices
-- Enforces: Section 38.8 (Compliance Framework) & Section 47 (Operational Governance)
-- ============================================================================

-- 1. MULTI-TIER KYC VERIFICATION RECORDS
CREATE TABLE IF NOT EXISTS kyc_verification_records (
    kyc_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL UNIQUE REFERENCES identities(identity_id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    verification_tier VARCHAR(50) NOT NULL DEFAULT 'TIER_1_BASIC' CHECK (
        verification_tier IN ('TIER_1_BASIC', 'TIER_2_STANDARD', 'TIER_3_ADVANCED', 'REJECTED')
    ),
    national_id_or_passport VARCHAR(100) UNIQUE,
    kra_pin VARCHAR(50) UNIQUE, -- Kenyan Revenue Authority PIN (e.g., A001234567Z)
    biometric_face_hash VARCHAR(64),
    aml_sanction_check_status VARCHAR(50) NOT NULL DEFAULT 'CLEARED' CHECK (
        aml_sanction_check_status IN ('CLEARED', 'FLAGGED_WATCHLIST', 'UNDER_INVESTIGATION')
    ),
    verified_by_identity_id TEXT REFERENCES identities(identity_id),
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. DECLARATIVE AML / CTF MONITORING RULES
CREATE TABLE IF NOT EXISTS aml_monitoring_rules (
    aml_rule_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    rule_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'AML-SMURFING-VELOCITY-01', 'AML-SANCTION-CHECK'
    rule_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    risk_threshold_kes NUMERIC(20, 2) NOT NULL,
    time_window_minutes INT NOT NULL,
    action_on_trigger VARCHAR(50) NOT NULL CHECK (action_on_trigger IN ('FREEZE_WALLET_AND_SAR', 'FLAG_FOR_REVIEW', 'BLOCK_TRANSACTION')),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. SUSPICIOUS ACTIVITY REPORTS (SAR)
CREATE TABLE IF NOT EXISTS aml_suspicious_activity_reports (
    sar_id TEXT PRIMARY KEY,
    sar_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'SAR-20260716-89B1'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    flagged_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    triggering_rule_code VARCHAR(100) NOT NULL,
    flagged_amount_kes NUMERIC(20, 2) NOT NULL,
    risk_score NUMERIC(5, 2) NOT NULL,
    narrative_summary TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'REPORTED_CBK_FIU' CHECK (
        status IN ('REPORTED_CBK_FIU', 'INTERNAL_REVIEW', 'CLEARED_FALSE_POSITIVE', 'CONFIRMED_MONEY_LAUNDERING')
    ),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. KRA eTIMS ELECTRONIC TAX INVOICES (Section 38.8 & 47)
-- Generates digital tax invoices per commercial checkout with exact VAT (16%) and control numbers.
CREATE TABLE IF NOT EXISTS kra_etims_tax_invoices (
    etims_invoice_id TEXT PRIMARY KEY,
    etims_control_number VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'KRA-ETIMS-2026-89A1B2C3'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    order_id TEXT NOT NULL UNIQUE REFERENCES orders(order_id),
    buyer_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    buyer_kra_pin VARCHAR(50),
    seller_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    seller_kra_pin VARCHAR(50) NOT NULL,
    taxable_amount_kes NUMERIC(15, 2) NOT NULL CHECK (taxable_amount_kes >= 0),
    vat_rate_pct NUMERIC(5, 2) DEFAULT 16.00 NOT NULL,
    vat_amount_kes NUMERIC(15, 2) NOT NULL CHECK (vat_amount_kes >= 0),
    total_invoice_amount_kes NUMERIC(15, 2) NOT NULL CHECK (total_invoice_amount_kes >= 0),
    digital_tax_stamp TEXT NOT NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_kyc_verification_status ON kyc_verification_records(verification_tier, aml_sanction_check_status);
CREATE INDEX idx_aml_sar_identity ON aml_suspicious_activity_reports(flagged_identity_id, status);
CREATE INDEX idx_kra_etims_order ON kra_etims_tax_invoices(order_id);
