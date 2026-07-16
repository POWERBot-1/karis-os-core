-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 038: Multi-Vendor Marketplace Aggregation & Split Settlements (Section 14.3 & 17.2)
-- ============================================================================

-- 1. MULTI-VENDOR MARKETPLACE CART ORDERS
CREATE TABLE IF NOT EXISTS marketplace_split_orders (
    cart_order_id TEXT PRIMARY KEY,
    cart_order_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'CART-MKT-2026-89A'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    customer_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    total_cart_amount_kes NUMERIC(15, 2) NOT NULL CHECK (total_cart_amount_kes > 0),
    payment_method VARCHAR(50) NOT NULL DEFAULT 'M_PESA',
    payment_reference VARCHAR(100) NOT NULL, -- e.g., 'QG37XXXXXXXX'
    settlement_status VARCHAR(50) NOT NULL DEFAULT 'PENDING_SPLIT' CHECK (
        settlement_status IN ('PENDING_SPLIT', 'MULTI_VENDOR_SPLIT_SETTLED', 'PARTIALLY_REFUNDED', 'FAILED')
    ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. MARKETPLACE VENDOR SETTLEMENT ALLOCATIONS
CREATE TABLE IF NOT EXISTS marketplace_vendor_settlement_allocations (
    allocation_id TEXT PRIMARY KEY,
    cart_order_id TEXT NOT NULL REFERENCES marketplace_split_orders(cart_order_id) ON DELETE CASCADE,
    vendor_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    gross_item_amount_kes NUMERIC(15, 2) NOT NULL CHECK (gross_item_amount_kes > 0),
    platform_commission_rate_pct NUMERIC(5, 2) DEFAULT 15.00 NOT NULL,
    platform_commission_kes NUMERIC(15, 2) NOT NULL CHECK (platform_commission_kes >= 0),
    net_vendor_payout_kes NUMERIC(15, 2) NOT NULL CHECK (net_vendor_payout_kes > 0),
    ledger_transaction_id TEXT REFERENCES ledger_transactions(transaction_id),
    payout_status VARCHAR(50) NOT NULL DEFAULT 'SETTLED_VIA_LEDGER' CHECK (
        payout_status IN ('SETTLED_VIA_LEDGER', 'HELD_IN_ESCROW', 'DISPUTED')
    ),
    settled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_marketplace_allocations_vendor ON marketplace_vendor_settlement_allocations(vendor_identity_id, payout_status);
