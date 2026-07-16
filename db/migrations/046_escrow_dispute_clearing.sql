-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 046: Unified Escrow Clearing House & Dispute Resolution (Section 31.1 & 11.2)
-- ============================================================================

-- 1. ENTERPRISE MULTI-PARTY ESCROW HOLDINGS
CREATE TABLE IF NOT EXISTS enterprise_escrow_holdings (
    escrow_id TEXT PRIMARY KEY,
    escrow_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'ESCROW-HOLD-2026-01'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    buyer_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    seller_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    escrowed_amount_kes NUMERIC(20, 2) NOT NULL CHECK (escrowed_amount_kes > 0),
    escrow_wallet_id TEXT NOT NULL REFERENCES wallets(wallet_id),
    status VARCHAR(50) NOT NULL DEFAULT 'HELD_IN_ESCROW' CHECK (
        status IN ('HELD_IN_ESCROW', 'RELEASED_TO_SELLER', 'REFUNDED_TO_BUYER', 'SPLIT_RESOLVED_DISPUTE')
    ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    released_at TIMESTAMP
);

-- 2. ENTERPRISE COMMERCE DISPUTE CASES
CREATE TABLE IF NOT EXISTS enterprise_dispute_cases (
    dispute_id TEXT PRIMARY KEY,
    dispute_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'DISPUTE-AGRI-2026-89A'
    escrow_id TEXT NOT NULL REFERENCES enterprise_escrow_holdings(escrow_id) ON DELETE CASCADE,
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    raised_by_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    dispute_reason VARCHAR(100) NOT NULL CHECK (
        dispute_reason IN ('PRODUCE_QUALITY_CLAIM', 'DELIVERY_NON_ARRIVAL', 'SHORT_SHIPMENT_COUNT', 'PRICING_OVERCHARGE', 'OTHER')
    ),
    dispute_summary TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'DISPUTE_RAISED' CHECK (
        status IN ('DISPUTE_RAISED', 'UNDER_INVESTIGATION', 'RESOLVED_SPLIT_REFUND', 'RESOLVED_FULL_RELEASE_SELLER', 'RESOLVED_FULL_REFUND_BUYER')
    ),
    resolution_decision_summary TEXT,
    seller_payout_pct NUMERIC(5, 2) DEFAULT 100.00 NOT NULL,
    buyer_refund_pct NUMERIC(5, 2) DEFAULT 0.00 NOT NULL,
    resolved_by_identity_id TEXT REFERENCES identities(identity_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP
);

CREATE INDEX idx_escrow_holdings_order_status ON enterprise_escrow_holdings(order_id, status);
CREATE INDEX idx_dispute_cases_escrow_status ON enterprise_dispute_cases(escrow_id, status);
