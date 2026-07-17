-- ============================================================================
-- KARIS OS™ MIGRATION 057: KARIS BORDERX EAST AFRICAN CUSTOMS & TRADE CLEARING ENGINE (SECTION 58 / VERTICAL 23)
-- ============================================================================
-- Establishes database tables and constraints for Vertical 23 (KARIS BorderX™):
-- 1. borderx_accounts: Trade entities (`IMPORTER, EXPORTER, CLEARING_AGENT, TRANSPORTER, FREIGHT_COMPANY, SHIPPING_LINE, CUSTOMS_OFFICER`) & 9 multi-currency trade wallets (`kes, ugx, tzs, rwf, bif, ssp, usd, eur, krt`)
-- 2. borderx_customs_declarations: Cross-border declarations (`IMPORTS, EXPORTS, TRANSIT_CARGO, WAREHOUSING, BONDED_GOODS, TEMPORARY_IMPORTS, DUTY_EXEMPTIONS`) across 8 regional corridors (`KE, UG, TZ, RW, BI, SS, CD, ET`)
-- 3. borderx_duty_payments: Smart Duty breakdown & double-entry settlements (`import_duty, export_duty, vat, excise, railway_levy, idf, rdl, port_charges, clearing_fees, agent_fees, inspection_fees`) with KRT fee discounts
-- 4. borderx_shipments_tracking: Multi-modal cargo tracking (`TRUCKS, RAIL, SHIPS, AIR_CARGO`), container seal verification & Smart Border Queue congestion/waiting time forecasts (`Busia, Malaba, Namanga, Gatuna, Rusumo, Nimule`)
-- 5. borderx_customs_inspections: Physical inspection schedules triggered when AI customs risk score (`customs_risk_score >= 75`) catches under-valuation, fake invoices, or smuggling patterns (`Rule 10 human officer verification`)
-- 6. borderx_trade_finance_facilities: Trade finance (`WORKING_CAPITAL, INVOICE_FINANCING, LETTERS_OF_CREDIT, TRADE_CREDIT, PURCHASE_FINANCING, SUPPLIER_FINANCING`) strictly verified under Rule 3 & double-entry settled under Rule 9
-- 7. borderx_logistics_marketplace_listings: Cargo, truck & warehouse matching listings across regional clearing corridors
-- 8. borderx_bonded_warehouses: Bonded goods, cold/dry storage tracking, container location & release orders
-- 9. borderx_digital_documents: Generated trade certificates (`COMMERCIAL_INVOICE, PACKING_LIST, CERTIFICATE_OF_ORIGIN, BILL_OF_LADING, TRANSIT_DECLARATION, CUSTOMS_DECLARATION_FORM, INSPECTION_CERTIFICATE, DELIVERY_NOTE`) with SHA-256 hash
-- 10. borderx_risk_and_fraud_logs: AI customs risk engine & fraud logs tracking under-valuation, duplicate entries, cargo diversion & tax evasion
-- 11. borderx_regional_trade_statistics: Government portal read-model telemetry aggregating regional trade volumes, duty collected, border traffic & commodity trends (`EAC / COMESA / AfCFTA`)
-- ============================================================================

CREATE TABLE IF NOT EXISTS borderx_accounts (
    account_id VARCHAR(64) PRIMARY KEY,
    identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    account_number VARCHAR(64) UNIQUE NOT NULL,
    entity_type VARCHAR(64) NOT NULL DEFAULT 'IMPORTER', -- IMPORTER, EXPORTER, CLEARING_AGENT, TRANSPORTER, FREIGHT_COMPANY, SHIPPING_LINE, CUSTOMS_OFFICER
    kyc_status VARCHAR(64) NOT NULL DEFAULT 'VERIFIED_TIER_3',
    kes_wallet_id VARCHAR(64) NOT NULL,
    ugx_wallet_id VARCHAR(64) NOT NULL,
    tzs_wallet_id VARCHAR(64) NOT NULL,
    rwf_wallet_id VARCHAR(64) NOT NULL,
    bif_wallet_id VARCHAR(64) NOT NULL,
    ssp_wallet_id VARCHAR(64) NOT NULL,
    usd_wallet_id VARCHAR(64) NOT NULL,
    eur_wallet_id VARCHAR(64) NOT NULL,
    krt_wallet_id VARCHAR(64) NOT NULL,
    customs_account_ref VARCHAR(128) NOT NULL,
    reputation_score INTEGER NOT NULL DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borderx_customs_declarations (
    declaration_id VARCHAR(64) PRIMARY KEY,
    trader_account_id VARCHAR(64) NOT NULL REFERENCES borderx_accounts(account_id) ON DELETE RESTRICT,
    agent_account_id VARCHAR(64) NOT NULL REFERENCES borderx_accounts(account_id) ON DELETE RESTRICT,
    declaration_type VARCHAR(64) NOT NULL DEFAULT 'IMPORTS', -- IMPORTS, EXPORTS, TRANSIT_CARGO, WAREHOUSING, BONDED_GOODS, TEMPORARY_IMPORTS, DUTY_EXEMPTIONS
    origin_country_code VARCHAR(8) NOT NULL DEFAULT 'CN',
    destination_country_code VARCHAR(8) NOT NULL DEFAULT 'KE', -- KE, UG, TZ, RW, BI, SS, CD, ET
    border_post_code VARCHAR(32) NOT NULL DEFAULT 'BUSIA_EAC', -- BUSIA, MALABA, NAMANGA, GATUNA, RUSUMO, NIMULE, MOMBASA_PORT
    hs_code VARCHAR(32) NOT NULL,
    commodity_description VARCHAR(255) NOT NULL,
    cif_value_usd NUMERIC(18, 4) NOT NULL,
    cif_value_kes NUMERIC(18, 4) NOT NULL,
    total_duty_assessed_kes NUMERIC(18, 4) NOT NULL,
    total_duty_assessed_krt NUMERIC(18, 4) NOT NULL,
    customs_risk_score NUMERIC(5, 2) NOT NULL DEFAULT 15.00,
    status VARCHAR(64) NOT NULL DEFAULT 'DECLARATION_FILED', -- DECLARATION_FILED, UNDER_INSPECTION, DUTY_PAID, CLEARED_FOR_ENTRY, BLOCKED_UNDER_VALUATION_OR_SMUGGLING
    ledger_entry_id VARCHAR(64) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borderx_duty_payments (
    payment_id VARCHAR(64) PRIMARY KEY,
    declaration_id VARCHAR(64) NOT NULL REFERENCES borderx_customs_declarations(declaration_id) ON DELETE RESTRICT,
    trader_account_id VARCHAR(64) NOT NULL REFERENCES borderx_accounts(account_id) ON DELETE RESTRICT,
    import_duty_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    export_duty_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    vat_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    excise_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    railway_levy_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    idf_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000, -- Import Declaration Fee
    rdl_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000, -- Railway Development Levy
    port_charges_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    clearing_fees_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    agent_fees_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    inspection_fees_kes NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    total_amount_kes NUMERIC(18, 4) NOT NULL,
    total_amount_krt NUMERIC(18, 4) NOT NULL,
    krt_fee_discount_pct NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    settlement_currency VARCHAR(16) NOT NULL DEFAULT 'KRT', -- KRT, KES, UGX, TZS, RWF, BIF, SSP, USD, EUR
    ledger_entry_id VARCHAR(64) NOT NULL,
    settled_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borderx_shipments_tracking (
    shipment_id VARCHAR(64) PRIMARY KEY,
    declaration_id VARCHAR(64) NOT NULL REFERENCES borderx_customs_declarations(declaration_id) ON DELETE RESTRICT,
    transporter_account_id VARCHAR(64) NOT NULL REFERENCES borderx_accounts(account_id) ON DELETE RESTRICT,
    transport_mode VARCHAR(32) NOT NULL DEFAULT 'TRUCKS', -- TRUCKS, RAIL, SHIPS, AIR_CARGO
    container_number VARCHAR(64) NOT NULL,
    seal_number VARCHAR(64) NOT NULL,
    seal_verification_status VARCHAR(32) NOT NULL DEFAULT 'SEAL_INTACT_VERIFIED',
    current_border_post VARCHAR(32) NOT NULL DEFAULT 'BUSIA_EAC',
    gps_coordinates VARCHAR(64) NOT NULL DEFAULT '0.4608° N, 34.0911° E',
    ai_predicted_waiting_hours NUMERIC(5, 2) NOT NULL DEFAULT 1.50,
    congestion_status VARCHAR(32) NOT NULL DEFAULT 'MODERATE_CONGESTION', -- CLEAR_FLOW, MODERATE_CONGESTION, HEAVY_CONGESTION
    ai_recommended_alternate_border VARCHAR(32) NOT NULL DEFAULT 'MALABA_EAC',
    status VARCHAR(64) NOT NULL DEFAULT 'IN_TRANSIT_TO_BORDER', -- IN_TRANSIT_TO_BORDER, AT_BORDER_QUEUE, CLEARED_CUSTOMS, DELIVERED_DESTINATION
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borderx_customs_inspections (
    inspection_id VARCHAR(64) PRIMARY KEY,
    declaration_id VARCHAR(64) NOT NULL REFERENCES borderx_customs_declarations(declaration_id) ON DELETE RESTRICT,
    customs_officer_account_id VARCHAR(64) NOT NULL REFERENCES borderx_accounts(account_id) ON DELETE RESTRICT,
    border_post VARCHAR(32) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    ai_risk_flag_summary TEXT NOT NULL,
    inspection_status VARCHAR(64) NOT NULL DEFAULT 'SCHEDULED_PENDING_INSPECTION', -- SCHEDULED_PENDING_INSPECTION, INSPECTION_PASSED_CLEARED, INSPECTION_FAILED_SEIZED
    officer_notes TEXT NOT NULL DEFAULT '',
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS borderx_trade_finance_facilities (
    facility_id VARCHAR(64) PRIMARY KEY,
    borrower_account_id VARCHAR(64) NOT NULL REFERENCES borderx_accounts(account_id) ON DELETE RESTRICT,
    facility_type VARCHAR(64) NOT NULL DEFAULT 'WORKING_CAPITAL', -- WORKING_CAPITAL, INVOICE_FINANCING, LETTERS_OF_CREDIT, TRADE_CREDIT, PURCHASE_FINANCING, SUPPLIER_FINANCING
    principal_amount_usd NUMERIC(18, 4) NOT NULL,
    principal_amount_krt NUMERIC(18, 4) NOT NULL,
    interest_rate_pct NUMERIC(5, 2) NOT NULL DEFAULT 8.50,
    tenor_days INTEGER NOT NULL DEFAULT 90,
    credit_approval_status VARCHAR(64) NOT NULL DEFAULT 'CREDIT_APPROVED', -- CREDIT_APPROVED, ACTIVE_DISBURSED, REPAID_SETTLED, REJECTED
    disbursement_ledger_id VARCHAR(64) NOT NULL DEFAULT '',
    repayment_ledger_id VARCHAR(64) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borderx_logistics_marketplace_listings (
    listing_id VARCHAR(64) PRIMARY KEY,
    provider_account_id VARCHAR(64) NOT NULL REFERENCES borderx_accounts(account_id) ON DELETE RESTRICT,
    listing_type VARCHAR(64) NOT NULL DEFAULT 'TRUCK_AVAILABLE', -- CARGO_AVAILABLE, TRUCK_AVAILABLE, WAREHOUSE_SPACE, CLEARING_AGENT_SERVICE
    origin_corridor VARCHAR(64) NOT NULL,
    destination_corridor VARCHAR(64) NOT NULL,
    capacity_tons NUMERIC(10, 2) NOT NULL DEFAULT 28.00,
    price_krt NUMERIC(15, 4) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'AVAILABLE', -- AVAILABLE, MATCHED_BOOKED, COMPLETED
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borderx_bonded_warehouses (
    warehouse_item_id VARCHAR(64) PRIMARY KEY,
    warehouse_account_id VARCHAR(64) NOT NULL REFERENCES borderx_accounts(account_id) ON DELETE RESTRICT,
    declaration_id VARCHAR(64) NOT NULL REFERENCES borderx_customs_declarations(declaration_id) ON DELETE RESTRICT,
    warehouse_type VARCHAR(64) NOT NULL DEFAULT 'BONDED_WAREHOUSE', -- BONDED_WAREHOUSE, COLD_STORAGE, DRY_STORAGE
    container_number VARCHAR(64) NOT NULL,
    seal_number VARCHAR(64) NOT NULL,
    storage_fee_daily_krt NUMERIC(10, 4) NOT NULL DEFAULT 50.0000,
    release_order_status VARCHAR(64) NOT NULL DEFAULT 'BONDED_IN_CUSTODY', -- BONDED_IN_CUSTODY, RELEASE_ORDER_ISSUED, DISPATCHED
    stored_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    released_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS borderx_digital_documents (
    document_id VARCHAR(64) PRIMARY KEY,
    declaration_id VARCHAR(64) NOT NULL REFERENCES borderx_customs_declarations(declaration_id) ON DELETE RESTRICT,
    document_type VARCHAR(64) NOT NULL, -- COMMERCIAL_INVOICE, PACKING_LIST, CERTIFICATE_OF_ORIGIN, BILL_OF_LADING, TRANSIT_DECLARATION, CUSTOMS_DECLARATION_FORM, INSPECTION_CERTIFICATE, DELIVERY_NOTE
    document_title VARCHAR(255) NOT NULL,
    payload_json TEXT NOT NULL,
    sha256_verification_hash VARCHAR(128) NOT NULL,
    digital_signature VARCHAR(255) NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borderx_risk_and_fraud_logs (
    log_id VARCHAR(64) PRIMARY KEY,
    trader_account_id VARCHAR(64) NOT NULL REFERENCES borderx_accounts(account_id) ON DELETE RESTRICT,
    declaration_id VARCHAR(64) NOT NULL DEFAULT '',
    fraud_type VARCHAR(64) NOT NULL, -- UNDER_VALUATION, FAKE_INVOICES, SMUGGLING_PATTERNS, DUPLICATE_CARGO, HIGH_RISK_TRADERS, SUSPICIOUS_TRANSACTIONS, CARGO_DIVERSION, TAX_EVASION
    detected_value_usd NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    ai_risk_score NUMERIC(5, 2) NOT NULL,
    status VARCHAR(64) NOT NULL DEFAULT 'FLAGGED_HIGH_RISK_BLOCKED',
    audit_notes TEXT NOT NULL,
    logged_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borderx_regional_trade_statistics (
    stat_id VARCHAR(64) PRIMARY KEY,
    region_corridor VARCHAR(64) NOT NULL DEFAULT 'EAC_NORTHERN_CORRIDOR', -- EAC_NORTHERN_CORRIDOR, EAC_CENTRAL_CORRIDOR, COMESA_CLEARING, AFCFTA_REGIONAL
    total_declarations_processed INTEGER NOT NULL DEFAULT 0,
    total_cif_value_usd NUMERIC(20, 4) NOT NULL DEFAULT 0.0000,
    total_duty_collected_kes NUMERIC(20, 4) NOT NULL DEFAULT 0.0000,
    total_duty_collected_krt NUMERIC(20, 4) NOT NULL DEFAULT 0.0000,
    avg_border_waiting_hours NUMERIC(5, 2) NOT NULL DEFAULT 1.85,
    top_commodity_hs_code VARCHAR(32) NOT NULL DEFAULT '8517.13.00',
    stat_period_date VARCHAR(32) NOT NULL DEFAULT '2026-07-17',
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
