-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 026: Future Industries Suite (Education, Tourism & Real Estate) (Section 35.3)
-- ============================================================================

-- 1. EDUCATION HUB: STUDENT TUITION FEE INSTALLMENT PLANS (`KARIS Edu-Pay`)
CREATE TABLE IF NOT EXISTS education_tuition_plans (
    plan_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    student_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    parent_or_guardian_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    institution_name VARCHAR(255) NOT NULL, -- e.g., 'Machakos Academy of Technology'
    academic_term VARCHAR(100) NOT NULL, -- e.g., 'Term 3 2026'
    total_tuition_fee_kes NUMERIC(15, 2) NOT NULL CHECK (total_tuition_fee_kes > 0),
    amount_paid_kes NUMERIC(15, 2) DEFAULT 0.00 NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE_INSTALLMENT' CHECK (status IN ('ACTIVE_INSTALLMENT', 'FULLY_PAID_SCHOLARSHIP', 'DEFAULTED')),
    krt_edu_tokens_awarded NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. TOURISM & HOSPITALITY HUB: ECO-LODGE SAFARI BOOKINGS (`KARIS Safari & Stays`)
CREATE TABLE IF NOT EXISTS hospitality_bookings (
    booking_id TEXT PRIMARY KEY,
    booking_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'SAFARI-MACHAKOS-99A'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    guest_identity_id TEXT NOT NULL REFERENCES identities(identity_id),
    lodge_or_hotel_name VARCHAR(255) NOT NULL, -- e.g., 'Machakos Luxury Eco-Safari Camp'
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    number_of_nights INT NOT NULL CHECK (number_of_nights > 0),
    total_booking_price_kes NUMERIC(15, 2) NOT NULL,
    krt_green_carbon_offset_tokens NUMERIC(10, 2) DEFAULT 50.00 NOT NULL,
    booking_status VARCHAR(50) NOT NULL DEFAULT 'CONFIRMED' CHECK (booking_status IN ('CONFIRMED', 'CHECKED_IN', 'COMPLETED', 'CANCELLED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. REAL ESTATE & CONSTRUCTION HUB: FRACTIONAL PROPERTY SYNDICATION (`KARIS Prop-Share`)
CREATE TABLE IF NOT EXISTS real_estate_syndications (
    syndication_id TEXT PRIMARY KEY,
    property_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'PROP-MLOLONGO-TOWERS-01'
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    property_name VARCHAR(255) NOT NULL,
    property_location TEXT NOT NULL,
    total_property_valuation_kes NUMERIC(20, 2) NOT NULL,
    total_fractional_units NUMERIC(15, 2) NOT NULL CHECK (total_fractional_units > 0),
    price_per_fractional_unit_kes NUMERIC(15, 2) NOT NULL,
    units_sold NUMERIC(15, 2) DEFAULT 0.00 NOT NULL,
    expected_rental_yield_pct NUMERIC(5, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN_SYNDICATION' CHECK (status IN ('OPEN_SYNDICATION', 'FULLY_SUBSCRIBED', 'UNDER_CONSTRUCTION', 'TENANTED_YIELDING')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_edu_tuition_student ON education_tuition_plans(student_identity_id, status);
CREATE INDEX idx_hospitality_guest ON hospitality_bookings(guest_identity_id, booking_status);
CREATE INDEX idx_prop_share_status ON real_estate_syndications(status);
