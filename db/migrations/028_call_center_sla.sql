-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 028: Call Center Service Level Agreement (SLA) & Escalation Engine (Section 24.4)
-- ============================================================================

-- 1. SLA MONITORING & BENCHMARK RECORDS
CREATE TABLE IF NOT EXISTS sla_monitoring_records (
    sla_record_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL UNIQUE REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    ticket_priority VARCHAR(50) NOT NULL,
    first_response_due_at TIMESTAMP NOT NULL,
    first_responded_at TIMESTAMP,
    resolution_due_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    sla_status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE_WITHIN_SLA' CHECK (
        sla_status IN ('ACTIVE_WITHIN_SLA', 'FIRST_RESPONSE_BREACHED', 'RESOLUTION_BREACHED', 'COMPLETED_ON_TIME', 'COMPLETED_BREACHED', 'ESCALATED_SUPERVISOR')
    ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. SLA ESCALATION AUDIT LOGS
CREATE TABLE IF NOT EXISTS sla_escalation_logs (
    escalation_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
    sla_record_id TEXT NOT NULL REFERENCES sla_monitoring_records(sla_record_id),
    previous_agent_identity_id TEXT REFERENCES identities(identity_id),
    escalated_to_supervisor_id TEXT NOT NULL REFERENCES identities(identity_id),
    escalation_reason VARCHAR(100) NOT NULL CHECK (
        escalation_reason IN ('FIRST_RESPONSE_TIME_EXCEEDED', 'RESOLUTION_TIME_EXCEEDED', 'REPEAT_COMPLAINT_RATE_HIGH', 'CUSTOMER_REQUESTED')
    ),
    escalated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_sla_monitoring_status_due ON sla_monitoring_records(sla_status, resolution_due_at);
CREATE INDEX idx_sla_escalation_ticket ON sla_escalation_logs(ticket_id);
