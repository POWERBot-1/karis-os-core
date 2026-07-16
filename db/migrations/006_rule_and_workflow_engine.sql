-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 006: Declarative Rule Engine & Workflow Engine
-- Enforces: Section 11 (Rule Engine & Workflow Engine) & Rule 7 (Everything Configurable)
-- ============================================================================

-- 1. DECLARATIVE BUSINESS RULES TABLE
CREATE TABLE IF NOT EXISTS business_rules (
    rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    rule_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'AUTOMATED_SETTLEMENT_ON_DELIVERY', 'KRT_REWARD_ON_PURCHASE'
    rule_name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_event_type VARCHAR(100) NOT NULL, -- e.g., 'PAYMENT_CONFIRMED', 'DELIVERY_COMPLETED'
    conditions JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g., [{"field": "payment_status", "op": "equals", "value": "PAYMENT_CONFIRMED"}]
    actions JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g., [{"action": "CREDIT_SUPPLIER_WALLET"}, {"action": "MINT_KRT_REWARD"}]
    priority INT DEFAULT 100 NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. WORKFLOW DEFINITIONS TABLE
CREATE TABLE IF NOT EXISTS workflow_definitions (
    workflow_def_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    workflow_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'CREDIT_APPROVAL_WORKFLOW', 'FARMER_ONBOARDING_WORKFLOW'
    workflow_name VARCHAR(255) NOT NULL,
    vertical VARCHAR(100) NOT NULL,
    steps JSONB NOT NULL, -- Ordered array of states, triggers, conditions, escalations
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. WORKFLOW INSTANCES TABLE
CREATE TABLE IF NOT EXISTS workflow_instances (
    instance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_def_id UUID NOT NULL REFERENCES workflow_definitions(workflow_def_id),
    target_resource_id UUID NOT NULL, -- e.g., order_id, credit_application_id, farmer_id
    target_resource_type VARCHAR(100) NOT NULL,
    current_state VARCHAR(100) NOT NULL,
    initiated_by_identity_id UUID REFERENCES identities(identity_id),
    assigned_to_identity_id UUID REFERENCES identities(identity_id),
    context_data JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'COMPLETED', 'ESCALATED', 'CANCELLED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. RULE ENGINE EXECUTION AUDIT LOG
CREATE TABLE IF NOT EXISTS rule_execution_logs (
    execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id UUID NOT NULL REFERENCES business_rules(rule_id),
    event_id UUID NOT NULL REFERENCES event_store(event_id),
    execution_status VARCHAR(50) NOT NULL CHECK (execution_status IN ('SUCCESS', 'CONDITION_FAILED', 'ACTION_FAILED')),
    execution_duration_ms NUMERIC(10, 2) NOT NULL,
    actions_executed JSONB NOT NULL,
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_business_rules_trigger ON business_rules(trigger_event_type, is_active);
CREATE INDEX idx_workflow_instances_resource ON workflow_instances(target_resource_id, target_resource_type);
CREATE INDEX idx_rule_execution_logs_event ON rule_execution_logs(event_id);
