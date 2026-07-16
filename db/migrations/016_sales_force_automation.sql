-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 016: Sales Force Automation Engine
-- Enforces: Section 22 (Sales Force Automation Engine)
-- ============================================================================

-- 1. FIELD SALES AGENTS TABLE
CREATE TABLE IF NOT EXISTS field_sales_agents (
    agent_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL UNIQUE REFERENCES identities(identity_id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    agent_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'SFA-MACHAKOS-01'
    assigned_territory VARCHAR(100) NOT NULL, -- e.g., 'Machakos County - Mlolongo Ward'
    supervisor_identity_id TEXT REFERENCES identities(identity_id),
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'ON_LEAVE', 'SUSPENDED')),
    commission_rate_pct NUMERIC(5, 2) DEFAULT 5.00 NOT NULL,
    total_revenue_generated_kes NUMERIC(20, 2) DEFAULT 0.00 NOT NULL,
    total_visits_completed INT DEFAULT 0 NOT NULL,
    total_referrals_converted INT DEFAULT 0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. SALES VISITS & OUTREACH ACTIVITIES
CREATE TABLE IF NOT EXISTS sales_visits (
    visit_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES field_sales_agents(agent_id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    customer_identity_id TEXT REFERENCES identities(identity_id),
    customer_business_name VARCHAR(255),
    visit_type VARCHAR(50) NOT NULL CHECK (visit_type IN ('FARMER_ONBOARDING', 'MERCHANT_REGISTRATION', 'PRODUCT_PROMOTION', 'FOLLOW_UP')),
    scheduled_time TIMESTAMP NOT NULL,
    completed_time TIMESTAMP,
    gps_coordinates VARCHAR(100),
    visit_status VARCHAR(50) NOT NULL DEFAULT 'TASK_CREATED' CHECK (visit_status IN (
        'TASK_CREATED', 'TASK_ASSIGNED', 'VISIT_STARTED', 'CUSTOMER_ENGAGED',
        'ORDER_CAPTURED', 'FOLLOW_UP_CREATED', 'TASK_COMPLETED', 'CANCELLED'
    )),
    notes TEXT,
    order_id TEXT REFERENCES orders(order_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. REFERRAL TRACKING & INCENTIVE LOGS
CREATE TABLE IF NOT EXISTS sales_referrals (
    referral_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES field_sales_agents(agent_id),
    referred_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    referral_code VARCHAR(100) NOT NULL,
    conversion_status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (conversion_status IN ('PENDING', 'CONVERTED_FIRST_PURCHASE', 'REJECTED')),
    converted_at TIMESTAMP,
    krt_bonus_granted NUMERIC(10, 2) DEFAULT 0.00,
    ledger_entry_id TEXT REFERENCES ledger_entries(entry_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_field_sales_agents_territory ON field_sales_agents(assigned_territory, status);
CREATE INDEX idx_sales_visits_agent_status ON sales_visits(agent_id, visit_status);
CREATE INDEX idx_sales_referrals_code ON sales_referrals(referral_code, conversion_status);
