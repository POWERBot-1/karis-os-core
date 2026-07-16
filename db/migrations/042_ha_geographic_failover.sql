-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 042: Active-Active High Availability & Geographic Failover Routing (Section 40.8 & 45.3)
-- ============================================================================

-- 1. ACTIVE-ACTIVE GEOGRAPHIC CLUSTER NODES
CREATE TABLE IF NOT EXISTS ha_geographic_cluster_nodes (
    node_id TEXT PRIMARY KEY,
    cluster_node_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'CLUSTER-NAIROBI-MAIN', 'CLUSTER-MACHAKOS-EDGE', 'CLUSTER-MOMBASA-DR'
    region_location VARCHAR(100) NOT NULL,
    cloud_provider VARCHAR(50) NOT NULL CHECK (cloud_provider IN ('AWS_EKS_AFRICA', 'GCP_GKE', 'AZURE_AKS', 'PRIVATE_KUBERNETES_CLUSTER')),
    health_heartbeat_status VARCHAR(50) NOT NULL DEFAULT 'ONLINE_HEALTHY' CHECK (
        health_heartbeat_status IN ('ONLINE_HEALTHY', 'HEARTBEAT_TIMEOUT_DEGRADED', 'MAINTENANCE_DRAINED', 'OFFLINE_FAILED')
    ),
    error_rate_pct NUMERIC(5, 2) DEFAULT 0.00 NOT NULL,
    replication_lag_ms NUMERIC(10, 2) DEFAULT 2.15 NOT NULL,
    active_connections_count INT DEFAULT 1200 NOT NULL,
    last_heartbeat_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. GEOGRAPHIC FAILOVER ROUTING LOGS
CREATE TABLE IF NOT EXISTS ha_geographic_failover_events (
    failover_id TEXT PRIMARY KEY,
    failover_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'FAILOVER-20260716-89A'
    failed_node_id TEXT NOT NULL REFERENCES ha_geographic_cluster_nodes(node_id),
    promoted_node_id TEXT NOT NULL REFERENCES ha_geographic_cluster_nodes(node_id),
    trigger_reason VARCHAR(255) NOT NULL, -- e.g., 'Heartbeat timeout on CLUSTER-NAIROBI-MAIN during 150 ops/sec stress test'
    traffic_rerouted_pct NUMERIC(5, 2) DEFAULT 100.00 NOT NULL,
    ledger_continuity_status VARCHAR(50) NOT NULL DEFAULT '100PCT_LEDGER_CONTINUITY_VERIFIED',
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_ha_cluster_health ON ha_geographic_cluster_nodes(health_heartbeat_status, error_rate_pct);
