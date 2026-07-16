-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 031: Enterprise Privacy Controls, Consent Management & GDPR/DPA Anonymization (Section 38.7)
-- ============================================================================

-- 1. GRANULAR PRIVACY CONSENT RECORDS
CREATE TABLE IF NOT EXISTS privacy_consent_records (
    consent_record_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL REFERENCES identities(identity_id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    consent_category VARCHAR(100) NOT NULL CHECK (consent_category IN (
        'MARKETING_COMMUNICATIONS', 'HEALTHCARE_EMR_DATA_SHARING', 'AI_BEHAVIORAL_SCORING',
        'OPEN_BANKING_FINANCIAL_ACCESS', 'THIRD_PARTY_PARTNER_OFFERS', 'BIOMETRIC_KYC_PROCESSING'
    )),
    is_granted BOOLEAN NOT NULL DEFAULT TRUE,
    granted_or_revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(identity_id, organization_id, consent_category)
);

-- 2. PRIVACY DATA EXPORT REQUESTS (Section 38.7 Data Export)
CREATE TABLE IF NOT EXISTS privacy_data_export_requests (
    export_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    requested_by_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    export_format VARCHAR(20) NOT NULL DEFAULT 'JSON_STRUCTURED' CHECK (export_format IN ('JSON_STRUCTURED', 'CSV_ARCHIVE', 'PDF_REPORT')),
    total_records_compiled BIGINT NOT NULL,
    export_status VARCHAR(50) NOT NULL DEFAULT 'COMPLETED' CHECK (export_status IN ('PENDING_COMPILATION', 'COMPLETED', 'EXPIRED')),
    file_download_url TEXT,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. RIGHT-TO-BE-FORGOTTEN ANONYMIZATION AUDIT LOGS (Section 38.7 & Rule 9 Compliance)
CREATE TABLE IF NOT EXISTS privacy_anonymization_audit_logs (
    anonymization_id TEXT PRIMARY KEY,
    original_identity_id TEXT NOT NULL,
    anonymized_alias_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'ANONYMIZED-USER-89A1B2C3'
    reason_code VARCHAR(100) NOT NULL CHECK (reason_code IN ('GDPR_RIGHT_TO_BE_FORGOTTEN', 'KENYA_DPA_DELETION_REQUEST', 'ACCOUNT_TERMINATED')),
    tables_scrubbed_json TEXT NOT NULL, -- e.g., ["identities", "patient_profiles", "crm_customer_profiles"]
    ledger_integrity_status VARCHAR(50) NOT NULL DEFAULT 'LEDGER_HASHES_PRESERVED_INTACT',
    executed_by_identity_id TEXT REFERENCES identities(identity_id),
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_privacy_consent_identity ON privacy_consent_records(identity_id, is_granted);
CREATE INDEX idx_privacy_anonymization_alias ON privacy_anonymization_audit_logs(anonymized_alias_code);
