-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 025: AI CRM Churn Prediction, Lifetime Value & Retention Campaigns (Section 23.4)
-- ============================================================================

-- 1. AI CUSTOMER INTELLIGENCE EVALUATIONS
CREATE TABLE IF NOT EXISTS ai_customer_intelligence_evaluations (
    evaluation_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL REFERENCES identities(identity_id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    historical_spend_kes NUMERIC(20, 2) NOT NULL,
    purchase_frequency_days NUMERIC(8, 2) NOT NULL,
    calculated_lifetime_value_kes NUMERIC(20, 2) NOT NULL,
    predicted_churn_risk_pct NUMERIC(5, 2) NOT NULL CHECK (predicted_churn_risk_pct BETWEEN 0 AND 100),
    customer_segment_tier VARCHAR(50) NOT NULL CHECK (customer_segment_tier IN (
        'LIFETIME_CHAMPION', 'LOYAL_ADVOCATE', 'HIGH_GROWTH_LEAD', 'AT_RISK_LOYALIST', 'CHURNED_INACTIVE'
    )),
    ai_recommended_action TEXT NOT NULL,
    retention_campaign_triggered BOOLEAN DEFAULT FALSE NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_ai_crm_segment_churn ON ai_customer_intelligence_evaluations(customer_segment_tier, predicted_churn_risk_pct);
