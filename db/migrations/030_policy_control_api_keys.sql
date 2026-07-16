-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 030: Operational Governance Policies, API Keys & Dynamic Tax Rules (Section 43 & 47)
-- ============================================================================

-- 1. PLATFORM OPERATIONAL GOVERNANCE POLICIES
CREATE TABLE IF NOT EXISTS platform_governance_policies (
    policy_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    policy_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'POL-GOV-RESERVE-RATIO-20PCT'
    policy_name VARCHAR(255) NOT NULL,
    policy_category VARCHAR(100) NOT NULL CHECK (policy_category IN (
        'TREASURY_LIQUIDITY_RESERVE', 'CREDIT_LENDING_THRESHOLD', 'MULTI_TENANT_ISOLATION',
        'DATA_RETENTION_PRIVACY', 'API_RATE_LIMITING', 'TAX_COMPLIANCE'
    )),
    policy_parameters_json TEXT NOT NULL,
    enforcement_mode VARCHAR(50) NOT NULL DEFAULT 'STRICT_BLOCKING' CHECK (enforcement_mode IN ('STRICT_BLOCKING', 'AUDIT_WARNING', 'ADVISORY_ONLY')),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. ENTERPRISE API KEYS LIFECYCLE MANAGEMENT (Section 38.4 & 43.2)
CREATE TABLE IF NOT EXISTS enterprise_api_keys (
    key_id TEXT PRIMARY KEY,
    key_prefix VARCHAR(20) UNIQUE NOT NULL, -- e.g., 'KARIS_LIVE_A8F2...'
    secret_key_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of exact API secret
    identity_id TEXT NOT NULL REFERENCES identities(identity_id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    key_name VARCHAR(100) NOT NULL, -- e.g., 'Machakos Supermarket POS Terminal Key'
    scopes_json TEXT NOT NULL DEFAULT '["ORDERS:WRITE", "LEDGER:READ"]',
    rate_limit_requests_per_minute INT DEFAULT 200 NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'REVOKED', 'EXPIRED', 'ROTATED')),
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    last_used_at TIMESTAMP
);

-- 3. DECLARATIVE DYNAMIC TAX RULES (Section 43.2)
CREATE TABLE IF NOT EXISTS dynamic_tax_rules (
    tax_rule_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    jurisdiction_code VARCHAR(10) NOT NULL DEFAULT 'KE' CHECK (jurisdiction_code IN ('KE', 'UG', 'TZ', 'RW', 'INTL')),
    tax_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'TAX-KE-VAT-16', 'TAX-KE-WHT-5'
    tax_name VARCHAR(255) NOT NULL,
    applicable_product_types_json TEXT NOT NULL DEFAULT '["ALL"]',
    tax_rate_pct NUMERIC(5, 2) NOT NULL CHECK (tax_rate_pct >= 0),
    is_withholding BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_enterprise_api_keys_prefix ON enterprise_api_keys(key_prefix, status);
CREATE INDEX idx_dynamic_tax_rules_jurisdiction ON dynamic_tax_rules(jurisdiction_code, is_active);
