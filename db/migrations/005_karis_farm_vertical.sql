-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 005: Agriculture & KARIS FARM Flagship Vertical
-- Enforces: Section 28 (KARIS FARM Vertical), Produce Traceability & Farm Operations
-- ============================================================================

-- 1. FARMS TABLE
CREATE TABLE IF NOT EXISTS farms (
    farm_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    farmer_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    cooperative_identity_id UUID REFERENCES identities(identity_id),
    farm_name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(100) UNIQUE,
    region_county VARCHAR(100) NOT NULL, -- e.g., 'Machakos County', 'Kiambu County'
    sub_county VARCHAR(100),
    ward VARCHAR(100),
    gps_coordinates VARCHAR(100), -- e.g., '-1.3564,36.9321'
    total_acreage NUMERIC(10, 2) NOT NULL CHECK (total_acreage > 0),
    certification_status VARCHAR(50) DEFAULT 'STANDARD' CHECK (
        certification_status IN ('STANDARD', 'ORGANIC', 'GAP_CERTIFIED', 'EXPORT_CERTIFIED')
    ),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. LAND PARCELS & CROP PLANS TABLE
CREATE TABLE IF NOT EXISTS crop_plans (
    plan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(farm_id) ON DELETE CASCADE,
    crop_type VARCHAR(100) NOT NULL, -- e.g., 'HASS_AVOCADO', 'FRENCH_BEANS', 'MAIZE', 'TOMATOES'
    parcel_name_or_code VARCHAR(100) NOT NULL,
    acreage_allocated NUMERIC(10, 2) NOT NULL,
    planting_date DATE NOT NULL,
    expected_harvest_date DATE NOT NULL,
    expected_yield_kg NUMERIC(15, 2) NOT NULL,
    input_cost_budget_kes NUMERIC(15, 2) DEFAULT 0.00,
    status VARCHAR(50) NOT NULL DEFAULT 'PLANTED' CHECK (
        status IN ('PLANTED', 'GROWING', 'HARVESTING', 'COMPLETED', 'FAILED')
    ),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. HARVEST LOGS TABLE
CREATE TABLE IF NOT EXISTS harvest_logs (
    harvest_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id UUID NOT NULL REFERENCES crop_plans(plan_id) ON DELETE RESTRICT,
    farm_id UUID NOT NULL REFERENCES farms(farm_id),
    harvest_date DATE NOT NULL,
    quantity_kg NUMERIC(15, 2) NOT NULL CHECK (quantity_kg > 0),
    quality_grade VARCHAR(50) NOT NULL CHECK (quality_grade IN ('GRADE_A', 'GRADE_B', 'REJECTED')),
    moisture_content_pct NUMERIC(5, 2),
    inspected_by_identity_id UUID REFERENCES identities(identity_id),
    batch_id UUID REFERENCES inventory_batches(batch_id),
    event_id UUID NOT NULL REFERENCES event_store(event_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. PRODUCE END-TO-END TRACEABILITY LINEAGE
-- Ensures complete food safety, recall capability, and consumer transparency from farm to table.
CREATE TABLE IF NOT EXISTS produce_traceability_records (
    traceability_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID NOT NULL REFERENCES inventory_batches(batch_id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(farm_id),
    harvest_id UUID REFERENCES harvest_logs(harvest_id),
    producer_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    aggregator_identity_id UUID REFERENCES identities(identity_id),
    processor_identity_id UUID REFERENCES identities(identity_id),
    transporter_identity_id UUID REFERENCES identities(identity_id),
    retail_destination_identity_id UUID REFERENCES identities(identity_id),
    traceability_qr_code VARCHAR(255) UNIQUE NOT NULL,
    lineage_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 5. AGRICULTURAL EXTENSION & CHV VISIT LOGS
CREATE TABLE IF NOT EXISTS extension_officer_visits (
    visit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(farm_id) ON DELETE CASCADE,
    officer_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    visit_date DATE NOT NULL,
    observations TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    pest_or_disease_risk_score NUMERIC(5, 2) DEFAULT 0.00,
    krt_incentive_awarded NUMERIC(10, 2) DEFAULT 0.00,
    event_id UUID NOT NULL REFERENCES event_store(event_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_farms_farmer ON farms(farmer_identity_id);
CREATE INDEX idx_farms_coop ON farms(cooperative_identity_id);
CREATE INDEX idx_crop_plans_farm ON crop_plans(farm_id, status);
CREATE INDEX idx_harvest_logs_batch ON harvest_logs(batch_id);
CREATE INDEX idx_traceability_batch ON produce_traceability_records(batch_id);
CREATE INDEX idx_traceability_qr ON produce_traceability_records(traceability_qr_code);
