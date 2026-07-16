-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 020: Enterprise Predictive Intelligence & Demand Forecasting Engine
-- Enforces: Section 27.4 (Enterprise AI Intelligence) & Section 13.4 (AI Responsibilities)
-- ============================================================================

-- 1. AI DEMAND FORECASTS TABLE
CREATE TABLE IF NOT EXISTS ai_demand_forecasts (
    forecast_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    product_id TEXT NOT NULL REFERENCES products(product_id),
    branch_store_id TEXT REFERENCES retail_stores(store_id),
    forecast_period_start DATE NOT NULL,
    forecast_period_end DATE NOT NULL,
    predicted_demand_units NUMERIC(15, 4) NOT NULL CHECK (predicted_demand_units >= 0),
    predicted_stockout_date DATE,
    recommended_reorder_units NUMERIC(15, 4) NOT NULL CHECK (recommended_reorder_units >= 0),
    confidence_score_pct NUMERIC(5, 2) NOT NULL CHECK (confidence_score_pct BETWEEN 0 AND 100),
    forecast_summary TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. DYNAMIC PRICING ELASTICITY RECOMMENDATIONS (Rule 10 Enforced)
CREATE TABLE IF NOT EXISTS dynamic_pricing_recommendations (
    recommendation_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    product_id TEXT NOT NULL REFERENCES products(product_id),
    current_unit_price_kes NUMERIC(15, 2) NOT NULL,
    recommended_unit_price_kes NUMERIC(15, 2) NOT NULL,
    price_change_pct NUMERIC(5, 2) NOT NULL,
    trigger_factor VARCHAR(100) NOT NULL CHECK (trigger_factor IN (
        'SHELF_EXPIRY_APPROACHING', 'SURGE_MARKET_DEMAND', 'COMPETITOR_BENCHMARK',
        'OVERSTOCK_CLEARANCE', 'SEASONAL_HARVEST_GLUT'
    )),
    ai_rationale TEXT NOT NULL,
    approval_status VARCHAR(50) NOT NULL DEFAULT 'PENDING_HUMAN_APPROVAL' CHECK (
        approval_status IN ('PENDING_HUMAN_APPROVAL', 'APPROVED_APPLIED', 'REJECTED', 'AUTO_APPLIED')
    ),
    approved_by_identity_id TEXT REFERENCES identities(identity_id),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    applied_at TIMESTAMP
);

CREATE INDEX idx_ai_demand_forecasts_product ON ai_demand_forecasts(product_id, branch_store_id);
CREATE INDEX idx_dynamic_pricing_status ON dynamic_pricing_recommendations(approval_status, trigger_factor);
