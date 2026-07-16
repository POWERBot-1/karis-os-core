-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 036: CI/CD Automated Deployment Quality Gates & Threshold Verification (Section 40.5 & 40.6)
-- ============================================================================

CREATE TABLE IF NOT EXISTS cicd_quality_gate_evaluations (
    evaluation_id TEXT PRIMARY KEY,
    pipeline_build_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'BUILD-20260716-PROD-99A'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    commit_hash VARCHAR(64) NOT NULL,
    branch_name VARCHAR(100) NOT NULL DEFAULT 'main',
    pytest_pass_rate_pct NUMERIC(5, 2) NOT NULL CHECK (pytest_pass_rate_pct BETWEEN 0 AND 100),
    stress_benchmark_ops_per_sec NUMERIC(10, 2) NOT NULL,
    rule_9_audit_hash_chain_intact BOOLEAN NOT NULL DEFAULT TRUE,
    security_vulnerabilities_detected INT DEFAULT 0 NOT NULL,
    gate_decision VARCHAR(50) NOT NULL DEFAULT 'CICD_GATE_PASSED_AUTHORIZED' CHECK (
        gate_decision IN ('CICD_GATE_PASSED_AUTHORIZED', 'CICD_GATE_FAILED_REJECTED', 'CONDITIONAL_CANARY_ROLLOUT')
    ),
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_cicd_quality_gates_decision ON cicd_quality_gate_evaluations(gate_decision, evaluated_at);
