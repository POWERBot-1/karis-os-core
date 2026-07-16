-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 018: KARIS OS 2.0 Vision (CBDC, Open Banking, Cross-Border EAC & ESG Carbon Credits)
-- Enforces: Section 48 (KARIS OS 2.0 Innovation Roadmap)
-- ============================================================================

-- 1. CENTRAL BANK DIGITAL CURRENCY (CBDC) SETTLEMENT LEDGER
CREATE TABLE IF NOT EXISTS cbdc_settlement_ledger (
    cbdc_tx_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL REFERENCES event_store(event_id),
    central_bank_identifier VARCHAR(100) NOT NULL, -- e.g., 'CBK-KENYA-CENTRAL-BANK'
    sender_institution_id TEXT NOT NULL REFERENCES identities(identity_id),
    recipient_institution_id TEXT NOT NULL REFERENCES identities(identity_id),
    cbdc_asset_code VARCHAR(50) NOT NULL DEFAULT 'CBDC_KES' CHECK (cbdc_asset_code IN ('CBDC_KES', 'CBDC_UGX', 'CBDC_TZS', 'CBDC_RWF')),
    amount NUMERIC(20, 6) NOT NULL CHECK (amount > 0),
    settlement_type VARCHAR(50) NOT NULL CHECK (settlement_type IN ('WHOLESALE_INTERBANK', 'RETAIL_SETTLEMENT', 'CROSS_BORDER_EAC')),
    cryptographic_signature TEXT NOT NULL,
    settled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. OPEN BANKING API CONSENTS & PAYMENT INITIATION
CREATE TABLE IF NOT EXISTS open_banking_consents (
    consent_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL REFERENCES identities(identity_id) ON DELETE CASCADE,
    bank_institution_id TEXT NOT NULL REFERENCES identities(identity_id),
    bank_name VARCHAR(100) NOT NULL, -- e.g., 'Equity Bank Kenya', 'KCB Bank', 'Co-operative Bank'
    account_masked VARCHAR(50) NOT NULL, -- e.g., 'XXXX-XXXX-1928'
    consent_type VARCHAR(50) NOT NULL CHECK (consent_type IN ('ACCOUNT_INFORMATION_AIS', 'PAYMENT_INITIATION_PIS')),
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'REVOKED', 'EXPIRED')),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL
);

-- 3. CROSS-BORDER EAST AFRICAN COMMUNITY (EAC) SETTLEMENTS
CREATE TABLE IF NOT EXISTS cross_border_eac_transfers (
    transfer_id TEXT PRIMARY KEY,
    sender_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    recipient_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    source_country VARCHAR(10) NOT NULL CHECK (source_country IN ('KE', 'UG', 'TZ', 'RW', 'BI', 'SS', 'CD')),
    destination_country VARCHAR(10) NOT NULL CHECK (destination_country IN ('KE', 'UG', 'TZ', 'RW', 'BI', 'SS', 'CD')),
    source_currency VARCHAR(10) NOT NULL, -- e.g., 'KES'
    destination_currency VARCHAR(10) NOT NULL, -- e.g., 'UGX'
    source_amount NUMERIC(20, 2) NOT NULL CHECK (source_amount > 0),
    destination_amount NUMERIC(20, 2) NOT NULL CHECK (destination_amount > 0),
    exchange_rate_used NUMERIC(15, 6) NOT NULL,
    settlement_status VARCHAR(50) NOT NULL DEFAULT 'INITIATED' CHECK (settlement_status IN ('INITIATED', 'EXCHANGING', 'COMPLETED', 'FAILED')),
    ledger_transaction_id TEXT REFERENCES ledger_transactions(transaction_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. ESG & CARBON FOOTPRINT TRACEABILITY RECORDS (Section 48.2)
-- Tracks Scope 1, 2, and 3 emissions across farm produce batches and logistics trips, awarding KRT-GREEN tokens.
CREATE TABLE IF NOT EXISTS esg_carbon_traceability_records (
    esg_record_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    target_resource_id TEXT NOT NULL, -- e.g., batch_id or dispatch_id
    target_resource_type VARCHAR(50) NOT NULL CHECK (target_resource_type IN ('PRODUCE_BATCH', 'LOGISTICS_TRIP', 'KITCHEN_MEAL', 'ENTERPRISE_SUMMARY')),
    scope_1_emissions_kg_co2 NUMERIC(10, 4) DEFAULT 0.0000 NOT NULL,
    scope_2_emissions_kg_co2 NUMERIC(10, 4) DEFAULT 0.0000 NOT NULL,
    scope_3_emissions_kg_co2 NUMERIC(10, 4) DEFAULT 0.0000 NOT NULL,
    total_carbon_footprint_kg_co2 NUMERIC(10, 4) NOT NULL,
    sustainability_rating VARCHAR(50) NOT NULL DEFAULT 'CARBON_NEUTRAL' CHECK (
        sustainability_rating IN ('CARBON_NEGATIVE', 'CARBON_NEUTRAL', 'LOW_EMISSION', 'STANDARD', 'HIGH_EMISSION')
    ),
    krt_green_tokens_minted NUMERIC(15, 4) DEFAULT 0.0000 NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_cbdc_settlement_sender ON cbdc_settlement_ledger(sender_institution_id, settlement_type);
CREATE INDEX idx_open_banking_consents_identity ON open_banking_consents(identity_id, status);
CREATE INDEX idx_cross_border_eac_status ON cross_border_eac_transfers(settlement_status, source_country, destination_country);
CREATE INDEX idx_esg_carbon_resource ON esg_carbon_traceability_records(target_resource_id, target_resource_type);
