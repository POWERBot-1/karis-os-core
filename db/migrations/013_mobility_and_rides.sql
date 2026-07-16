-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 013: Mobility & Ride-Hailing Vertical
-- Enforces: Section 33 (Mobility & Ride-Hailing Vertical)
-- ============================================================================

-- 1. FLEET VEHICLES & DRIVERS
CREATE TABLE IF NOT EXISTS mobility_drivers (
    driver_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identity_id UUID NOT NULL UNIQUE REFERENCES identities(identity_id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    licence_number VARCHAR(100) UNIQUE NOT NULL,
    vehicle_make_model VARCHAR(100) NOT NULL, -- e.g., 'Toyota Belta', 'Bajaj RE TukTuk', 'TVC Motorbike'
    registration_plate VARCHAR(50) UNIQUE NOT NULL,
    service_tier VARCHAR(50) NOT NULL CHECK (service_tier IN ('BODABODA', 'TUKTUK', 'STANDARD_TAXI', 'EXPRESS_CAR', 'CORPORATE_VAN')),
    status VARCHAR(50) NOT NULL DEFAULT 'OFFLINE' CHECK (status IN ('OFFLINE', 'ONLINE_AVAILABLE', 'ON_TRIP', 'SUSPENDED')),
    rating NUMERIC(3, 2) DEFAULT 5.00 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. RIDE REQUESTS & TRIPS
CREATE TABLE IF NOT EXISTS mobility_trips (
    trip_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'TRIP-MACHAKOS-182A'
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    passenger_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    driver_id UUID REFERENCES mobility_drivers(driver_id),
    pickup_location_text TEXT NOT NULL,
    dropoff_location_text TEXT NOT NULL,
    pickup_gps VARCHAR(100) NOT NULL,
    dropoff_gps VARCHAR(100) NOT NULL,
    estimated_distance_km NUMERIC(10, 2) NOT NULL CHECK (estimated_distance_km > 0),
    base_fare_kes NUMERIC(15, 2) NOT NULL,
    dynamic_surge_multiplier NUMERIC(4, 2) DEFAULT 1.00 NOT NULL, -- Calculated by Mobility AI Engine
    total_fare_kes NUMERIC(15, 2) NOT NULL CHECK (total_fare_kes >= 0),
    driver_payout_kes NUMERIC(15, 2) NOT NULL,
    trip_status VARCHAR(50) NOT NULL DEFAULT 'RIDE_REQUESTED' CHECK (trip_status IN (
        'RIDE_REQUESTED', 'DRIVER_MATCHED', 'DRIVER_ACCEPTED', 'DRIVER_ARRIVED',
        'TRIP_STARTED', 'TRIP_IN_PROGRESS', 'TRIP_COMPLETED', 'CANCELLED'
    )),
    order_id UUID REFERENCES orders(order_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_mobility_drivers_status ON mobility_drivers(status, service_tier);
CREATE INDEX idx_mobility_trips_passenger ON mobility_trips(passenger_identity_id, trip_status);
CREATE INDEX idx_mobility_trips_driver ON mobility_trips(driver_id, trip_status);
