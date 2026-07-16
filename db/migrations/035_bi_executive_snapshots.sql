-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 035: Unified BI Executive & Leadership Dashboard Aggregations (Section 27.2 & 27.3)
-- ============================================================================

CREATE TABLE IF NOT EXISTS bi_executive_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    dashboard_category VARCHAR(50) NOT NULL CHECK (
        dashboard_category IN ('EXECUTIVE_SUMMARY', 'COMMERCE_RETAIL_POS', 'DELIVERY_LOGISTICS', 'FINANCE_TREASURY_LENDING', 'HEALTHCARE_EMR_CHV')
    ),
    metrics_payload_json TEXT NOT NULL,
    total_orders_tracked INT DEFAULT 0 NOT NULL,
    total_revenue_kes NUMERIC(20, 2) DEFAULT 0.00 NOT NULL,
    total_krt_circulating NUMERIC(20, 2) DEFAULT 0.00 NOT NULL,
    treasury_reserve_ratio_pct NUMERIC(5, 2) DEFAULT 0.00 NOT NULL,
    snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_bi_snapshots_org_category ON bi_executive_snapshots(organization_id, dashboard_category, snapshot_timestamp);
