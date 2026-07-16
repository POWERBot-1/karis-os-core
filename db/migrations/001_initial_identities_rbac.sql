-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 001: Identities, Organizations & Role-Based Access Control (RBAC)
-- Enforces: Section 7 (Identity, Organization & RBAC), Rule 7, Rule 8, Rule 9
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. IDENTITIES TABLE
-- Globally unique digital identity for every human, organization, system, AI agent, or API service.
CREATE TABLE IF NOT EXISTS identities (
    identity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identity_type VARCHAR(50) NOT NULL CHECK (identity_type IN (
        'INDIVIDUAL', 'BUSINESS', 'GOVERNMENT_INSTITUTION', 'BANK', 'INVESTOR',
        'NGO', 'COOPERATIVE', 'HEALTHCARE_PROVIDER', 'EDUCATIONAL_INSTITUTION',
        'AI_AGENT', 'EXTERNAL_API_SERVICE', 'PLATFORM_ADMINISTRATOR'
    )),
    global_identifier VARCHAR(255) UNIQUE NOT NULL, -- e.g., National ID, KRA PIN, Business Reg No, AI Agent UUID
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(50) UNIQUE, -- e.g., +254700000000 (M-Pesa linked phone)
    auth_methods JSONB NOT NULL DEFAULT '["OTP_SMS"]'::jsonb,
    verification_status VARCHAR(50) NOT NULL DEFAULT 'PENDING_VERIFICATION' CHECK (
        verification_status IN ('PENDING_VERIFICATION', 'VERIFIED', 'SUSPENDED', 'REVOKED')
    ),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 2. ORGANIZATIONS TABLE (Multi-Tenancy Foundation)
-- Each organization operates independently while sharing core platform services.
CREATE TABLE IF NOT EXISTS organizations (
    organization_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_organization_id UUID REFERENCES organizations(organization_id),
    name VARCHAR(255) UNIQUE NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL, -- e.g., 'KARIS_FARM', 'KARIS_RETAIL', 'KARIS_EATERY'
    vertical_type VARCHAR(100) NOT NULL,
    tax_identifier VARCHAR(100),
    country_code VARCHAR(10) DEFAULT 'KE' NOT NULL,
    currency VARCHAR(10) DEFAULT 'KES' NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPENDED', 'ARCHIVED')),
    settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. ROLES TABLE
-- Defines granular permissions across organizations and verticals.
CREATE TABLE IF NOT EXISTS roles (
    role_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE CASCADE,
    role_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE NOT NULL,
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g., ["ORDER:CREATE", "LEDGER:READ", "INVENTORY:ADD"]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(organization_id, role_name)
);

-- 4. ORGANIZATION MEMBERSHIPS & RBAC ASSIGNMENTS
-- Single Identity Principle: One person may hold multiple roles across organizations without duplicating accounts.
CREATE TABLE IF NOT EXISTS organization_memberships (
    membership_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identity_id UUID NOT NULL REFERENCES identities(identity_id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    assigned_by_identity_id UUID REFERENCES identities(identity_id),
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'EXPIRED', 'REVOKED')),
    valid_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(identity_id, organization_id, role_id)
);

-- 5. AUDIT LOGS FOR IDENTITY & RBAC OPERATIONS
-- Enforces: Rule 9 (Immutable Transactions) & Rule 8 (Timestamped)
CREATE TABLE IF NOT EXISTS rbac_audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    actor_identity_id UUID REFERENCES identities(identity_id),
    target_identity_id UUID REFERENCES identities(identity_id),
    organization_id UUID REFERENCES organizations(organization_id),
    action_description TEXT NOT NULL,
    previous_state JSONB,
    new_state JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cryptographic_hash VARCHAR(64) NOT NULL
);

-- Indexing for fast authorization checks and multi-tenant queries
CREATE INDEX idx_identities_phone ON identities(phone_number);
CREATE INDEX idx_identities_type ON identities(identity_type);
CREATE INDEX idx_org_memberships_identity ON organization_memberships(identity_id, status);
CREATE INDEX idx_org_memberships_org ON organization_memberships(organization_id, status);
