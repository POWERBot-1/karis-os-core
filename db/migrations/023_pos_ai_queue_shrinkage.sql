-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 023: AI-Assisted POS Queue Congestion & Retail Shrinkage Detection (Section 20.3 & 30.5)
-- ============================================================================

-- 1. POS TERMINAL QUEUE MONITORING LOGS
CREATE TABLE IF NOT EXISTS pos_queue_monitoring_logs (
    log_id TEXT PRIMARY KEY,
    store_id TEXT NOT NULL REFERENCES retail_stores(store_id) ON DELETE CASCADE,
    terminal_id TEXT NOT NULL REFERENCES pos_terminals(terminal_id),
    active_customers_in_line INT NOT NULL CHECK (active_customers_in_line >= 0),
    estimated_wait_time_minutes NUMERIC(5, 2) NOT NULL CHECK (estimated_wait_time_minutes >= 0),
    congestion_status VARCHAR(50) NOT NULL DEFAULT 'NORMAL_FLOW' CHECK (
        congestion_status IN ('NORMAL_FLOW', 'MODERATE_QUEUE', 'QUEUE_CONGESTION_DETECTED', 'CRITICAL_BOTTLENECK')
    ),
    ai_recommendation_action VARCHAR(255),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. RETAIL INVENTORY SHRINKAGE & DISCREPANCY AUDITS
CREATE TABLE IF NOT EXISTS retail_shrinkage_anomalies (
    shrinkage_id TEXT PRIMARY KEY,
    store_id TEXT NOT NULL REFERENCES retail_stores(store_id),
    product_id TEXT NOT NULL REFERENCES products(product_id),
    batch_id TEXT REFERENCES inventory_batches(batch_id),
    expected_system_quantity NUMERIC(15, 4) NOT NULL,
    physical_recount_quantity NUMERIC(15, 4) NOT NULL,
    discrepancy_quantity NUMERIC(15, 4) NOT NULL,
    estimated_loss_kes NUMERIC(15, 2) NOT NULL,
    shrinkage_reason VARCHAR(100) NOT NULL CHECK (
        shrinkage_reason IN ('UNRECORDED_SPOILAGE', 'THEFT_SUSPECTED', 'CASHIER_CHECKOUT_ERROR', 'SUPPLIER_SHORT_SHIPMENT', 'UNKNOWN')
    ),
    investigation_status VARCHAR(50) NOT NULL DEFAULT 'FLAGGED_FOR_AUDIT' CHECK (
        investigation_status IN ('FLAGGED_FOR_AUDIT', 'UNDER_INVESTIGATION', 'WRITTEN_OFF_LEDGER', 'RESOLVED')
    ),
    recounted_by_identity_id TEXT REFERENCES identities(identity_id),
    recounted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_pos_queue_monitoring_status ON pos_queue_monitoring_logs(store_id, congestion_status);
CREATE INDEX idx_retail_shrinkage_store ON retail_shrinkage_anomalies(store_id, investigation_status);
