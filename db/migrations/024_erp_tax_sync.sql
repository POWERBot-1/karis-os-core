-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 024: Enterprise ERP/Accounting Sync & Notification Templates (Section 36.5 & 43.2)
-- ============================================================================

-- 1. ERP & ACCOUNTING SYSTEM BATCH SYNCHRONIZATION LOGS
CREATE TABLE IF NOT EXISTS erp_accounting_sync_logs (
    sync_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    target_system_name VARCHAR(100) NOT NULL CHECK (target_system_name IN ('SAP_S4HANA_KENYA', 'ORACLE_NETSUITE', 'QUICKBOOKS_ENTERPRISE', 'MICROSOFT_DYNAMICS')),
    fiscal_period VARCHAR(50) NOT NULL, -- e.g., 'FY-2026-Q3'
    batch_start_timestamp TIMESTAMP NOT NULL,
    batch_end_timestamp TIMESTAMP NOT NULL,
    total_ledger_entries_synced INT NOT NULL CHECK (total_ledger_entries_synced >= 0),
    total_debit_volume_kes NUMERIC(20, 2) NOT NULL,
    total_credit_volume_kes NUMERIC(20, 2) NOT NULL,
    sync_status VARCHAR(50) NOT NULL DEFAULT 'COMPLETED_VERIFIED' CHECK (sync_status IN ('COMPLETED_VERIFIED', 'PARTIAL_RECONCILIATION', 'FAILED_RETRYING')),
    external_batch_reference VARCHAR(100) UNIQUE NOT NULL,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. DECLARATIVE NOTIFICATION TEMPLATES (Rule 7 Enforced)
CREATE TABLE IF NOT EXISTS notification_templates (
    template_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    template_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'TPL-ORDER-CONFIRMED-SMS', 'TPL-LOAN-APPROVED-WA'
    channel_type VARCHAR(50) NOT NULL CHECK (channel_type IN ('SMS', 'WHATSAPP', 'EMAIL', 'IN_APP_PUSH')),
    template_subject VARCHAR(255),
    template_body_text TEXT NOT NULL, -- Dynamic syntax with {{customer_name}}, {{amount_kes}}, etc.
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. NOTIFICATION DISPATCH AUDIT LOGS
CREATE TABLE IF NOT EXISTS notification_dispatch_logs (
    dispatch_id TEXT PRIMARY KEY,
    template_id TEXT REFERENCES notification_templates(template_id),
    recipient_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    recipient_phone_or_email VARCHAR(255) NOT NULL,
    channel_type VARCHAR(50) NOT NULL,
    rendered_message_text TEXT NOT NULL,
    delivery_status VARCHAR(50) NOT NULL DEFAULT 'DELIVERED_CONFIRMED' CHECK (
        delivery_status IN ('QUEUED_DISPATCH', 'DELIVERED_CONFIRMED', 'FAILED_GATEWAY_ERROR')
    ),
    correlation_id TEXT NOT NULL,
    dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_erp_sync_org_system ON erp_accounting_sync_logs(organization_id, target_system_name);
CREATE INDEX idx_notification_dispatch_recipient ON notification_dispatch_logs(recipient_identity_id, delivery_status);
