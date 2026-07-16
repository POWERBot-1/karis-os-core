-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 048: Declarative Tax Holidays & Dynamic Tariff Overrides (Section 43 & 47)
-- ============================================================================

CREATE TABLE IF NOT EXISTS declarative_tax_holidays_and_tariffs (
    holiday_id TEXT PRIMARY KEY,
    holiday_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'HOLIDAY-KE-AGRI-EXEMPT-2026'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    jurisdiction_code VARCHAR(10) NOT NULL DEFAULT 'KE',
    product_category VARCHAR(100) NOT NULL, -- e.g., 'AGRICULTURAL_INPUTS_SEEDS_FERTILIZERS'
    holiday_name VARCHAR(255) NOT NULL,
    override_tax_rate_pct NUMERIC(5, 2) NOT NULL DEFAULT 0.00 CHECK (override_tax_rate_pct >= 0),
    statutory_rationale TEXT NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_tax_holidays_active_category ON declarative_tax_holidays_and_tariffs(organization_id, product_category, is_active);
