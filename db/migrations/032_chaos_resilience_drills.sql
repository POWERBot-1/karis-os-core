-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 032: Chaos Engineering & Fault Injection Resilience Suite (Section 44.2 & 40.7)
-- ============================================================================

CREATE TABLE IF NOT EXISTS chaos_fault_injection_logs (
    drill_id TEXT PRIMARY KEY,
    drill_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'CHAOS-DRILL-2026-01'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    fault_type VARCHAR(100) NOT NULL CHECK (fault_type IN (
        'SIMULATED_NETWORK_LATENCY_500MS', 'SIMULATED_DATABASE_SLAVE_DISCONNECT',
        'SIMULATED_CONCURRENT_THREAD_DEADLOCK', 'SIMULATED_REDIS_CACHE_FAILOVER'
    )),
    target_component VARCHAR(100) NOT NULL, -- e.g., 'UNIVERSAL_LEDGER_ENGINE', 'UNIVERSAL_EVENT_BUS'
    concurrent_transactions_injected INT NOT NULL CHECK (concurrent_transactions_injected >= 0),
    dlq_events_recovered_count INT NOT NULL CHECK (dlq_events_recovered_count >= 0),
    ledger_integrity_post_drill VARCHAR(50) NOT NULL DEFAULT 'VERIFIED_CLEAN',
    drill_status VARCHAR(50) NOT NULL DEFAULT 'COMPLETED_PASSED' CHECK (
        drill_status IN ('COMPLETED_PASSED', 'COMPLETED_HEALED_VIA_DLQ', 'FAILED_CORRUPTION_DETECTED')
    ),
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_chaos_drills_status_fault ON chaos_fault_injection_logs(drill_status, fault_type);
