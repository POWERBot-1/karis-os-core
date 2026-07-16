-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 033: Multi-Warehouse Serial Tracking & AI Weather-Aware Dispatch (Section 15 & 21.5)
-- ============================================================================

-- 1. MULTI-WAREHOUSE SERIAL NUMBER CRATE INVENTORY
CREATE TABLE IF NOT EXISTS warehouse_serial_number_inventory (
    serial_item_id TEXT PRIMARY KEY,
    serial_barcode VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'SN-AVO-CRATE-2026-0001'
    product_id TEXT NOT NULL REFERENCES products(product_id),
    batch_id TEXT NOT NULL REFERENCES inventory_batches(batch_id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    warehouse_location_code VARCHAR(100) NOT NULL, -- e.g., 'WH-MACHAKOS-MAIN', 'WH-MLOLONGO-DEPOT'
    current_custodian_identity_id TEXT REFERENCES identities(identity_id),
    item_status VARCHAR(50) NOT NULL DEFAULT 'AVAILABLE_IN_WAREHOUSE' CHECK (
        item_status IN ('AVAILABLE_IN_WAREHOUSE', 'RESERVED_FOR_DISPATCH', 'IN_TRANSIT_RIDER', 'DELIVERED_RETAIL', 'EXPIRED')
    ),
    traceability_qr_code TEXT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. AI WEATHER-AWARE ROUTE PROXIMITY DISPATCH RECORDS (Section 21.5)
CREATE TABLE IF NOT EXISTS weather_aware_logistics_dispatches (
    weather_dispatch_id TEXT PRIMARY KEY,
    dispatch_id TEXT NOT NULL UNIQUE REFERENCES logistics_dispatches(dispatch_id) ON DELETE CASCADE,
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    pickup_gps VARCHAR(100) NOT NULL,
    dropoff_gps VARCHAR(100) NOT NULL,
    weather_condition VARCHAR(100) NOT NULL CHECK (
        weather_condition IN ('CLEAR_SUNNY', 'MODERATE_CLOUDY', 'HEAVY_RAINFALL_STORM', 'EXTREME_HEAT_SURGE')
    ),
    selected_vehicle_type VARCHAR(50) NOT NULL,
    ai_weather_rationale TEXT NOT NULL,
    weather_surge_multiplier NUMERIC(4, 2) DEFAULT 1.00 NOT NULL,
    final_delivery_fee_kes NUMERIC(15, 2) NOT NULL,
    dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_warehouse_serial_location_status ON warehouse_serial_number_inventory(warehouse_location_code, item_status);
CREATE INDEX idx_weather_dispatch_condition ON weather_aware_logistics_dispatches(weather_condition, selected_vehicle_type);
