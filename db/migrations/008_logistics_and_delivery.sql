-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 008: Delivery & Logistics Engine
-- Enforces: Section 21 (Delivery & Logistics) & Rule 4 (No Delivery -> No Rider Payment)
-- ============================================================================

-- 1. DELIVERY ZONES & TERRITORIES
CREATE TABLE IF NOT EXISTS delivery_zones (
    zone_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    zone_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'ZONE-MACHAKOS-MLOLONGO', 'ZONE-NAIROBI-CBD'
    zone_name VARCHAR(255) NOT NULL,
    base_delivery_fee_kes NUMERIC(15, 2) NOT NULL CHECK (base_delivery_fee_kes >= 0),
    per_km_fee_kes NUMERIC(15, 2) NOT NULL CHECK (per_km_fee_kes >= 0),
    krt_delivery_bonus NUMERIC(10, 2) DEFAULT 10.00, -- KRT bonus awarded per completed delivery
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. DELIVERY PARTNERS / RIDERS TABLE
CREATE TABLE IF NOT EXISTS delivery_partners (
    rider_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identity_id UUID NOT NULL REFERENCES identities(identity_id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    assigned_zone_id UUID REFERENCES delivery_zones(zone_id),
    vehicle_type VARCHAR(50) NOT NULL CHECK (vehicle_type IN (
        'MOTORCYCLE', 'BICYCLE', 'VAN', 'REFRIGERATED_TRUCK', 'TUKTUK', 'AMBULANCE'
    )),
    registration_plate VARCHAR(50) UNIQUE NOT NULL,
    verification_status VARCHAR(50) NOT NULL DEFAULT 'VERIFIED' CHECK (
        verification_status IN ('PENDING_VERIFICATION', 'VERIFIED', 'SUSPENDED')
    ),
    active_status VARCHAR(50) NOT NULL DEFAULT 'AVAILABLE' CHECK (
        active_status IN ('AVAILABLE', 'ON_DELIVERY', 'OFFLINE')
    ),
    performance_score NUMERIC(5, 2) DEFAULT 100.00 NOT NULL,
    safety_score NUMERIC(5, 2) DEFAULT 100.00 NOT NULL,
    total_deliveries_completed INT DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(identity_id, organization_id)
);

-- 3. LOGISTICS DISPATCHES & DELIVERIES TABLE
CREATE TABLE IF NOT EXISTS logistics_dispatches (
    dispatch_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    order_id UUID NOT NULL REFERENCES orders(order_id) ON DELETE RESTRICT,
    rider_id UUID REFERENCES delivery_partners(rider_id),
    pickup_address TEXT NOT NULL,
    dropoff_address TEXT NOT NULL,
    distance_km NUMERIC(10, 2) NOT NULL CHECK (distance_km >= 0),
    delivery_fee_kes NUMERIC(15, 2) NOT NULL CHECK (delivery_fee_kes >= 0),
    escrow_payout_kes NUMERIC(15, 2) NOT NULL CHECK (escrow_payout_kes >= 0),
    dispatch_status VARCHAR(50) NOT NULL DEFAULT 'ORDER_READY' CHECK (dispatch_status IN (
        'ORDER_READY', 'DELIVERY_REQUESTED', 'RIDER_MATCHED', 'RIDER_ACCEPTED',
        'PICKUP_STARTED', 'ITEM_COLLECTED', 'IN_TRANSIT', 'ARRIVED_DESTINATION',
        'DELIVERY_CONFIRMED', 'DELIVERY_CANCELLED'
    )),
    ai_dispatch_score NUMERIC(5, 2), -- Calculated by AI Dispatch Engine
    estimated_arrival_time TIMESTAMP WITH TIME ZONE,
    correlation_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. PROOF OF DELIVERY & ESCROW PAYOUT LOG (Enforcing Rule 4)
CREATE TABLE IF NOT EXISTS delivery_proofs (
    proof_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dispatch_id UUID NOT NULL UNIQUE REFERENCES logistics_dispatches(dispatch_id) ON DELETE RESTRICT,
    order_id UUID NOT NULL REFERENCES orders(order_id),
    rider_id UUID NOT NULL REFERENCES delivery_partners(rider_id),
    recipient_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    gps_coordinates_confirmed VARCHAR(100) NOT NULL,
    verification_code_used VARCHAR(50), -- e.g., OTP or QR confirmation code provided by recipient
    recipient_signature_url TEXT,
    photo_proof_url TEXT,
    payout_released BOOLEAN DEFAULT FALSE NOT NULL,
    ledger_transaction_id UUID REFERENCES ledger_transactions(transaction_id),
    krt_bonus_granted NUMERIC(10, 2) DEFAULT 0.00,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_delivery_partners_zone ON delivery_partners(assigned_zone_id, active_status);
CREATE INDEX idx_logistics_dispatches_status ON logistics_dispatches(dispatch_status);
CREATE INDEX idx_logistics_dispatches_rider ON logistics_dispatches(rider_id, dispatch_status);
