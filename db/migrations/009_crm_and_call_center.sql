-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 009: Customer Relationship Management (CRM) & Call Center Engine
-- Enforces: Section 23 (CRM Engine) & Section 24 (Call Center & Customer Experience)
-- ============================================================================

-- 1. UNIFIED CUSTOMER PROFILES TABLE
-- Every customer maintains one evolving relationship profile across all KARIS OS verticals.
CREATE TABLE IF NOT EXISTS crm_customer_profiles (
    crm_profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identity_id UUID NOT NULL UNIQUE REFERENCES identities(identity_id) ON DELETE CASCADE,
    customer_stage VARCHAR(50) NOT NULL DEFAULT 'REGISTERED' CHECK (customer_stage IN (
        'LEAD', 'REGISTERED', 'ACTIVE_CUSTOMER', 'LOYAL_CUSTOMER', 'ADVOCATE', 'INVESTOR', 'LIFETIME_MEMBER'
    )),
    total_lifetime_spend_kes NUMERIC(20, 2) DEFAULT 0.00 NOT NULL,
    total_orders_placed INT DEFAULT 0 NOT NULL,
    ai_churn_risk_score NUMERIC(5, 2) DEFAULT 0.00, -- 0-100 score from AI Customer Intelligence
    ai_lifetime_value_prediction NUMERIC(20, 2) DEFAULT 0.00,
    preferred_communication_channel VARCHAR(50) DEFAULT 'WHATSAPP' CHECK (
        preferred_communication_channel IN ('WHATSAPP', 'SMS', 'EMAIL', 'VOICE_CALL', 'IN_APP')
    ),
    preferences_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. CALL CENTER SUPPORT TICKETS TABLE
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_number VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'TKT-20260716-89A1'
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    customer_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    assigned_agent_identity_id UUID REFERENCES identities(identity_id),
    channel VARCHAR(50) NOT NULL CHECK (channel IN (
        'VOICE_CALL', 'WHATSAPP', 'SMS', 'EMAIL', 'IN_APP_CHAT', 'AI_CHAT_ASSISTANT'
    )),
    category VARCHAR(100) NOT NULL CHECK (category IN (
        'ORDER_DELAY', 'PAYMENT_DISPUTE', 'PRODUCE_QUALITY_CLAIM', 'DELIVERY_ISSUE',
        'LOAN_INQUIRY', 'TECHNICAL_SUPPORT', 'GENERAL_INQUIRY'
    )),
    priority VARCHAR(50) NOT NULL DEFAULT 'MEDIUM' CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
    status VARCHAR(50) NOT NULL DEFAULT 'TICKET_CREATED' CHECK (status IN (
        'TICKET_CREATED', 'AGENT_ASSIGNED', 'INVESTIGATION', 'CUSTOMER_UPDATED',
        'RESOLUTION_PROVIDED', 'CUSTOMER_CONFIRMED', 'TICKET_CLOSED', 'ESCALATED'
    )),
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    ai_sentiment_score NUMERIC(5, 2), -- -100 to +100 score
    ai_recommended_solution TEXT,
    resolution_notes TEXT,
    sla_due_at TIMESTAMP WITH TIME ZONE NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. TICKET COMMUNICATION LOGS
CREATE TABLE IF NOT EXISTS ticket_communications (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
    sender_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    sender_role VARCHAR(50) NOT NULL CHECK (sender_role IN ('CUSTOMER', 'AGENT', 'AI_ASSISTANT', 'SYSTEM')),
    message_text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_support_tickets_customer ON support_tickets(customer_identity_id, status);
CREATE INDEX idx_support_tickets_agent ON support_tickets(assigned_agent_identity_id, status);
CREATE INDEX idx_support_tickets_priority_sla ON support_tickets(priority, sla_due_at) WHERE status != 'TICKET_CLOSED';
