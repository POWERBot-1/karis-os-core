-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 045: Multi-Cloud Kubernetes Container Autoscaling & HPA Logs (Section 40.3 & 40.4)
-- ============================================================================

CREATE TABLE IF NOT EXISTS kubernetes_hpa_autoscaling_logs (
    hpa_log_id TEXT PRIMARY KEY,
    cluster_node_code VARCHAR(100) NOT NULL REFERENCES ha_geographic_cluster_nodes(cluster_node_code),
    target_microservice_deployment VARCHAR(100) NOT NULL CHECK (
        target_microservice_deployment IN ('karis-api-gateway', 'karis-event-worker', 'karis-ledger-engine', 'karis-ai-gateway')
    ),
    current_replicas INT NOT NULL CHECK (current_replicas >= 1),
    desired_replicas INT NOT NULL CHECK (desired_replicas >= 1),
    cpu_utilization_pct NUMERIC(5, 2) NOT NULL CHECK (cpu_utilization_pct BETWEEN 0 AND 100),
    request_velocity_ops_per_sec NUMERIC(10, 2) NOT NULL,
    scaling_action VARCHAR(50) NOT NULL CHECK (
        scaling_action IN ('PODS_SCALED_OUT_TRAFFIC_SURGE', 'PODS_SCALED_IN_LOW_LOAD', 'OPTIMAL_REPLICAS_MAINTAINED')
    ),
    scaling_reason TEXT NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_k8s_hpa_service_time ON kubernetes_hpa_autoscaling_logs(target_microservice_deployment, evaluated_at);
