-- ============================================================================
-- KARIS OS™ MIGRATION 052: KARIS INNOVATION EXPANSION SUITE (SECTION 52)
-- ============================================================================
-- Establishes database tables and constraints for Verticals 16, 17, and 18:
-- 1. pharma_cold_chain_batches: Track temperature-sensitive pharmaceutical lots & QR codes
-- 2. pharma_temperature_telemetry: IoT telemetry monitoring exact storage/transit temp (`<8°C`)
-- 3. prop_share_syndications: Fractional real estate properties & monthly rental income pools
-- 4. prop_share_allocations: Investor share ownership & automated dividend metrics (`Rule 9`)
-- 5. edupay_tuition_plans: Student academic term fee installment schedules (`Rule 3`)
-- 6. edupay_tuition_installments: Reconciled tuition payments awarding `KRT-EDU` (`Rule 7 & 9`)
-- ============================================================================

CREATE TABLE IF NOT EXISTS pharma_cold_chain_batches (
    batch_id VARCHAR(64) PRIMARY KEY,
    product_id VARCHAR(64) NOT NULL,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(organization_id) ON DELETE RESTRICT,
    batch_number VARCHAR(128) NOT NULL UNIQUE,
    qr_traceability_code VARCHAR(128) NOT NULL UNIQUE,
    storage_min_celsius NUMERIC(5, 2) NOT NULL DEFAULT 2.00,
    storage_max_celsius NUMERIC(5, 2) NOT NULL DEFAULT 8.00,
    current_temperature_celsius NUMERIC(5, 2) NOT NULL DEFAULT 4.50,
    status VARCHAR(32) NOT NULL DEFAULT 'SAFE_COLD_CHAIN',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pharma_temperature_telemetry (
    telemetry_id VARCHAR(64) PRIMARY KEY,
    batch_id VARCHAR(64) NOT NULL REFERENCES pharma_cold_chain_batches(batch_id) ON DELETE RESTRICT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temperature_celsius NUMERIC(5, 2) NOT NULL,
    humidity_pct NUMERIC(5, 2) NOT NULL DEFAULT 55.00,
    gps_location VARCHAR(128) NOT NULL DEFAULT '(-1.3850, 36.9400)',
    status VARCHAR(32) NOT NULL DEFAULT 'NORMAL'
);

CREATE TABLE IF NOT EXISTS prop_share_syndications (
    syndication_id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(organization_id) ON DELETE RESTRICT,
    property_title VARCHAR(255) NOT NULL,
    location_county VARCHAR(64) NOT NULL DEFAULT 'Machakos County',
    total_shares INTEGER NOT NULL CHECK (total_shares > 0),
    share_price_kes NUMERIC(15, 4) NOT NULL CHECK (share_price_kes > 0),
    monthly_rental_income_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    status VARCHAR(32) NOT NULL DEFAULT 'OPEN_FOR_ALLOCATION',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prop_share_allocations (
    allocation_id VARCHAR(64) PRIMARY KEY,
    syndication_id VARCHAR(64) NOT NULL REFERENCES prop_share_syndications(syndication_id) ON DELETE RESTRICT,
    investor_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    shares_owned INTEGER NOT NULL CHECK (shares_owned >= 0),
    total_invested_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    total_dividends_earned_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_prop_share_alloc UNIQUE (syndication_id, investor_identity_id)
);

CREATE TABLE IF NOT EXISTS edupay_tuition_plans (
    plan_id VARCHAR(64) PRIMARY KEY,
    student_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    institution_organization_id VARCHAR(64) NOT NULL REFERENCES organizations(organization_id) ON DELETE RESTRICT,
    academic_term VARCHAR(64) NOT NULL,
    total_tuition_kes NUMERIC(15, 4) NOT NULL CHECK (total_tuition_kes > 0),
    paid_amount_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    remaining_balance_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE_INSTALLMENTS',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS edupay_tuition_installments (
    installment_id VARCHAR(64) PRIMARY KEY,
    plan_id VARCHAR(64) NOT NULL REFERENCES edupay_tuition_plans(plan_id) ON DELETE RESTRICT,
    payer_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    amount_kes NUMERIC(15, 4) NOT NULL CHECK (amount_kes > 0),
    payment_method VARCHAR(32) NOT NULL DEFAULT 'MPESA_EXPRESS_PALPLUS',
    external_reference VARCHAR(128) NOT NULL UNIQUE,
    reconciled_ledger_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pharma_batches_org ON pharma_cold_chain_batches(organization_id);
CREATE INDEX IF NOT EXISTS idx_pharma_telemetry_batch ON pharma_temperature_telemetry(batch_id);
CREATE INDEX IF NOT EXISTS idx_prop_syndications_org ON prop_share_syndications(organization_id);
CREATE INDEX IF NOT EXISTS idx_prop_allocations_synd ON prop_share_allocations(syndication_id);
CREATE INDEX IF NOT EXISTS idx_edupay_plans_student ON edupay_tuition_plans(student_identity_id);
