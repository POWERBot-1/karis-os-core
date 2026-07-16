-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 034: Automated Enterprise API SDK Client Generation Logs (Section 46.2)
-- ============================================================================

CREATE TABLE IF NOT EXISTS sdk_generation_logs (
    generation_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    requested_by_identity_id TEXT REFERENCES identities(identity_id),
    sdk_language VARCHAR(50) NOT NULL CHECK (sdk_language IN ('PYTHON_ASYNC_SYNC', 'TYPESCRIPT_NODE_BROWSER')),
    platform_version VARCHAR(50) NOT NULL,
    total_endpoints_wrapped INT NOT NULL CHECK (total_endpoints_wrapped > 0),
    total_domain_models_exported INT NOT NULL CHECK (total_domain_models_exported > 0),
    package_filename VARCHAR(255) NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_sdk_generation_lang_time ON sdk_generation_logs(sdk_language, generated_at);
