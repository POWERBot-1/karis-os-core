-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 039: Regulatory Compliance & Multi-Jurisdictional Reporting (Section 35.4 & 38.8)
-- ============================================================================

CREATE TABLE IF NOT EXISTS regulatory_compliance_reports (
    report_id TEXT PRIMARY KEY,
    report_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'REG-KE-CBK-AML-2026-Q3'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    jurisdiction_code VARCHAR(10) NOT NULL CHECK (jurisdiction_code IN ('KE', 'UG', 'TZ', 'RW', 'INTL')),
    report_type VARCHAR(100) NOT NULL CHECK (report_type IN (
        'CENTRAL_BANK_AML_FIU_SUMMARY', 'KRA_ANNUAL_TAX_RECONCILIATION',
        'HEALTHCARE_DPA_PRIVACY_AUDIT', 'MULTI_TENANT_LEDGER_INTEGRITY_SUMMARY'
    )),
    reporting_period_start DATE NOT NULL,
    reporting_period_end DATE NOT NULL,
    compiled_metrics_json TEXT NOT NULL,
    total_records_audited BIGINT NOT NULL,
    compliance_status VARCHAR(50) NOT NULL DEFAULT '100PCT_VERIFIED_COMPLIANT' CHECK (
        compliance_status IN ('100PCT_VERIFIED_COMPLIANT', 'DISCREPANCIES_DETECTED', 'UNDER_AUDIT')
    ),
    generated_by_identity_id TEXT REFERENCES identities(identity_id),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_regulatory_reports_jurisdiction ON regulatory_compliance_reports(jurisdiction_code, report_type);
