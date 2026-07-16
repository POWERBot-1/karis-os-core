-- ============================================================================
-- KARIS OS™ UNIFIED ENTERPRISE & DIGITAL ECONOMY PLATFORM
-- Migration 012: Healthcare, EMR, Pharmacy, Laboratory & Ambulance Dispatch
-- Enforces: Section 32 (Healthcare & Medical Services Vertical)
-- ============================================================================

-- 1. MEDICAL FACILITIES & CLINICS
CREATE TABLE IF NOT EXISTS healthcare_facilities (
    facility_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    facility_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'HOSP-MACHAKOS-COUNTY-01'
    facility_name VARCHAR(255) NOT NULL,
    facility_type VARCHAR(100) NOT NULL CHECK (facility_type IN (
        'NATIONAL_HOSPITAL', 'COUNTY_HOSPITAL', 'PRIVATE_CLINIC', 'DISPENSARY',
        'PHARMACY', 'DIAGNOSTIC_LAB', 'AMBULANCE_UNIT'
    )),
    address TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. PATIENT HEALTHCARE PROFILES (Strict Privacy & Consent Controlled)
CREATE TABLE IF NOT EXISTS patient_profiles (
    patient_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identity_id UUID NOT NULL UNIQUE REFERENCES identities(identity_id) ON DELETE CASCADE,
    blood_group VARCHAR(10),
    allergies JSONB DEFAULT '[]'::jsonb,
    chronic_conditions JSONB DEFAULT '[]'::jsonb,
    emergency_contact_phone VARCHAR(50),
    consent_recorded BOOLEAN DEFAULT TRUE NOT NULL,
    chv_assigned_identity_id UUID REFERENCES identities(identity_id), -- Community Health Volunteer
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. MEDICAL APPOINTMENTS & TELECONSULTATIONS
CREATE TABLE IF NOT EXISTS medical_appointments (
    appointment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_id UUID NOT NULL REFERENCES healthcare_facilities(facility_id),
    patient_id UUID NOT NULL REFERENCES patient_profiles(patient_id),
    doctor_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    appointment_type VARCHAR(50) NOT NULL CHECK (appointment_type IN ('IN_PERSON', 'TELEMEDICINE', 'HOME_VISIT', 'EMERGENCY')),
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'APPOINTMENT_BOOKED' CHECK (status IN (
        'APPOINTMENT_BOOKED', 'CONFIRMED', 'PATIENT_CHECKED_IN', 'CONSULTATION_STARTED',
        'CONSULTATION_COMPLETED', 'CANCELLED', 'NO_SHOW'
    )),
    consultation_fee_kes NUMERIC(15, 2) NOT NULL CHECK (consultation_fee_kes >= 0),
    order_id UUID REFERENCES orders(order_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. ELECTRONIC MEDICAL RECORDS (EMR) - IMMUTABLE CLINICAL NOTES
CREATE TABLE IF NOT EXISTS emr_clinical_notes (
    emr_note_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id UUID NOT NULL REFERENCES medical_appointments(appointment_id),
    patient_id UUID NOT NULL REFERENCES patient_profiles(patient_id),
    doctor_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    diagnosis_summary TEXT NOT NULL,
    treatment_plan TEXT NOT NULL,
    vitals_data JSONB DEFAULT '{}'::jsonb,
    audit_hash VARCHAR(64) NOT NULL, -- Rule 9 Immutability enforcement for clinical notes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 5. PRESCRIPTIONS & PHARMACY DISPENSING
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    emr_note_id UUID NOT NULL REFERENCES emr_clinical_notes(emr_note_id),
    patient_id UUID NOT NULL REFERENCES patient_profiles(patient_id),
    doctor_identity_id UUID NOT NULL REFERENCES identities(identity_id),
    medication_product_id UUID NOT NULL REFERENCES products(product_id),
    dosage_instructions TEXT NOT NULL,
    quantity_prescribed NUMERIC(10, 2) NOT NULL CHECK (quantity_prescribed > 0),
    status VARCHAR(50) NOT NULL DEFAULT 'ISSUED' CHECK (status IN ('ISSUED', 'DISPENSED', 'EXPIRED')),
    dispensed_by_pharmacy_id UUID REFERENCES healthcare_facilities(facility_id),
    dispensed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 6. AMBULANCE EMERGENCY DISPATCH
CREATE TABLE IF NOT EXISTS ambulance_dispatches (
    emergency_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patient_profiles(patient_id),
    facility_id UUID REFERENCES healthcare_facilities(facility_id),
    pickup_coordinates VARCHAR(100) NOT NULL,
    assigned_ambulance_rider_id UUID REFERENCES delivery_partners(rider_id),
    priority VARCHAR(50) DEFAULT 'LIFE_THREATENING' NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'EMERGENCY_REQUESTED' CHECK (status IN (
        'EMERGENCY_REQUESTED', 'LOCATION_IDENTIFIED', 'NEAREST_UNIT_SELECTED',
        'AMBULANCE_DISPATCHED', 'PATIENT_PICKED', 'HOSPITAL_NOTIFIED', 'PATIENT_DELIVERED', 'CASE_CLOSED'
    )),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_medical_appointments_patient ON medical_appointments(patient_id, status);
CREATE INDEX idx_emr_clinical_notes_patient ON emr_clinical_notes(patient_id);
CREATE INDEX idx_prescriptions_patient ON prescriptions(patient_id, status);
