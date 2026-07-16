-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 047: AI Supply Chain Bottlenecks & Dynamic Route Bypass (Section 27.4 & 13.4)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_supply_chain_bottlenecks (
    bottleneck_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    warehouse_or_corridor_code VARCHAR(100) NOT NULL, -- e.g., 'CORRIDOR-MACHAKOS-NAIROBI-A104'
    active_transit_delay_hours NUMERIC(5, 2) NOT NULL CHECK (active_transit_delay_hours >= 0),
    backlogged_crates_count INT NOT NULL CHECK (backlogged_crates_count >= 0),
    bottleneck_status VARCHAR(50) NOT NULL DEFAULT 'NORMAL_FLOW' CHECK (
        bottleneck_status IN ('NORMAL_FLOW', 'MODERATE_CONGESTION', 'CRITICAL_TRANSIT_BOTTLENECK_DETECTED', 'BYPASS_ROUTE_ACTIVE')
    ),
    ai_recommended_bypass_action TEXT NOT NULL,
    approval_status VARCHAR(50) NOT NULL DEFAULT 'PENDING_HUMAN_APPROVAL' CHECK (
        approval_status IN ('PENDING_HUMAN_APPROVAL', 'APPROVED_BYPASS_APPLIED', 'REJECTED')
    ),
    approved_by_identity_id TEXT REFERENCES identities(identity_id),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP
);

CREATE INDEX idx_supply_bottlenecks_status ON ai_supply_chain_bottlenecks(warehouse_or_corridor_code, bottleneck_status);
