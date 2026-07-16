-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 010: Omnichannel POS & Supermarket Retail Vertical
-- Enforces: Section 20 (POS Engine) & Section 30 (Supermarket & Retail Vertical)
-- ============================================================================

-- 1. RETAIL STORES & POS TERMINALS
CREATE TABLE IF NOT EXISTS retail_stores (
    store_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    store_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'STORE-RETAIL-MLOLONGO-01'
    store_name VARCHAR(255) NOT NULL,
    branch_type VARCHAR(100) NOT NULL CHECK (branch_type IN ('SUPERMARKET', 'WHOLESALE_DEPOT', 'PHARMACY_BRANCH', 'EXPRESS_STORE')),
    address TEXT NOT NULL,
    manager_identity_id UUID REFERENCES identities(identity_id),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS pos_terminals (
    terminal_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES retail_stores(store_id) ON DELETE CASCADE,
    terminal_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'POS-MLO-01-T1'
    device_type VARCHAR(50) NOT NULL CHECK (device_type IN ('SMART_TERMINAL', 'TABLET', 'DESKTOP', 'SELF_KIOSK', 'MOBILE_POS')),
    offline_sync_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ONLINE' CHECK (status IN ('ONLINE', 'OFFLINE', 'MAINTENANCE')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. POS CASHIER SESSIONS
CREATE TABLE IF NOT EXISTS pos_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    terminal_id UUID NOT NULL REFERENCES pos_terminals(terminal_id),
    cashier_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    closed_at TIMESTAMP WITH TIME ZONE,
    opening_cash_kes NUMERIC(15, 2) NOT NULL CHECK (opening_cash_kes >= 0),
    expected_closing_cash_kes NUMERIC(15, 2) DEFAULT 0.00,
    actual_closing_cash_kes NUMERIC(15, 2) DEFAULT 0.00,
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED', 'RECONCILING'))
);

-- 3. STORE SHELF INVENTORY & DYNAMIC PRICING RULES
CREATE TABLE IF NOT EXISTS store_inventory (
    store_inventory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES retail_stores(store_id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(product_id),
    batch_id UUID REFERENCES inventory_batches(batch_id),
    shelf_quantity NUMERIC(15, 4) NOT NULL CHECK (shelf_quantity >= 0),
    min_replenishment_level NUMERIC(15, 4) DEFAULT 10.00 NOT NULL,
    standard_retail_price_kes NUMERIC(15, 2) NOT NULL CHECK (standard_retail_price_kes >= 0),
    dynamic_price_kes NUMERIC(15, 2), -- Set by Retail AI Pricing Engine
    is_on_promotion BOOLEAN DEFAULT FALSE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(store_id, product_id, batch_id)
);

CREATE INDEX idx_pos_sessions_cashier ON pos_sessions(cashier_identity_id, status);
CREATE INDEX idx_store_inventory_store ON store_inventory(store_id, product_id);
