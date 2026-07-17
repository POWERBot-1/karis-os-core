-- ============================================================================
-- KARIS OS™ MIGRATION 054: KARIS ACADEMY EDUCATIONAL ECOSYSTEM (SECTION 55)
-- ============================================================================
-- Establishes database tables and constraints for Vertical 20 (Karis Academy™):
-- 1. karis_academy_institutions: Unlimited schools, colleges, universities & training centers
-- 2. karis_academy_concept_nodes: Interconnected knowledge engine concepts & prerequisites
-- 3. karis_academy_lessons_and_quizzes: 14 AI-generated educational artifacts (`Rule 10 approval`)
-- 4. karis_academy_student_records: Immutable academic transcripts & KRT-EDU rewards (`Rule 9`)
-- 5. karis_academy_scholarship_disbursements: Reconciled scholarship stipends via wallet engine (`Rule 5`)
-- ============================================================================

CREATE TABLE IF NOT EXISTS karis_academy_institutions (
    institution_id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(organization_id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    institution_type VARCHAR(64) NOT NULL DEFAULT 'TECHNICAL_UNIVERSITY',
    curriculum_framework VARCHAR(64) NOT NULL DEFAULT 'KENYA_CBC_COMPETENCY_BASED',
    admin_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    enrolled_count INTEGER NOT NULL DEFAULT 1,
    tuition_krt_pool NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karis_academy_concept_nodes (
    concept_id VARCHAR(64) PRIMARY KEY,
    institution_id VARCHAR(64) NOT NULL REFERENCES karis_academy_institutions(institution_id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    category_domain VARCHAR(64) NOT NULL DEFAULT 'COMPUTER_SCIENCE_AI',
    prerequisite_concept_ids_json TEXT NOT NULL DEFAULT '[]',
    mastery_threshold_pct NUMERIC(5, 2) NOT NULL DEFAULT 85.00,
    krt_reward_on_mastery NUMERIC(15, 4) NOT NULL DEFAULT 250.0000,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karis_academy_lessons_and_quizzes (
    item_id VARCHAR(64) PRIMARY KEY,
    concept_id VARCHAR(64) NOT NULL REFERENCES karis_academy_concept_nodes(concept_id) ON DELETE RESTRICT,
    institution_id VARCHAR(64) NOT NULL REFERENCES karis_academy_institutions(institution_id) ON DELETE RESTRICT,
    creator_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    item_type VARCHAR(64) NOT NULL DEFAULT 'LESSON_NOTE_AND_QUIZ',
    title VARCHAR(255) NOT NULL,
    content_payload_json TEXT NOT NULL,
    version_number INTEGER NOT NULL DEFAULT 1,
    ai_generated_status VARCHAR(64) NOT NULL DEFAULT 'DRAFT_PENDING_EDUCATOR_APPROVAL',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karis_academy_student_records (
    record_id VARCHAR(64) PRIMARY KEY,
    student_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    institution_id VARCHAR(64) NOT NULL REFERENCES karis_academy_institutions(institution_id) ON DELETE RESTRICT,
    concept_id VARCHAR(64) NOT NULL REFERENCES karis_academy_concept_nodes(concept_id) ON DELETE RESTRICT,
    mastery_score_pct NUMERIC(5, 2) NOT NULL DEFAULT 95.00,
    completion_status VARCHAR(32) NOT NULL DEFAULT 'MASTERY_CERTIFIED',
    krt_edu_reward_earned NUMERIC(15, 4) NOT NULL DEFAULT 250.0000,
    reconciled_ledger_hash VARCHAR(64) NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS karis_academy_scholarship_disbursements (
    disbursement_id VARCHAR(64) PRIMARY KEY,
    institution_id VARCHAR(64) NOT NULL REFERENCES karis_academy_institutions(institution_id) ON DELETE RESTRICT,
    student_identity_id VARCHAR(64) NOT NULL REFERENCES identities(identity_id) ON DELETE RESTRICT,
    amount_krt NUMERIC(15, 4) NOT NULL CHECK (amount_krt > 0),
    disbursement_type VARCHAR(64) NOT NULL DEFAULT 'LIVING_STIPEND_AND_TUITION',
    reconciled_ledger_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_academy_institutions_org ON karis_academy_institutions(organization_id);
CREATE INDEX IF NOT EXISTS idx_academy_concepts_inst ON karis_academy_concept_nodes(institution_id);
CREATE INDEX IF NOT EXISTS idx_academy_lessons_concept ON karis_academy_lessons_and_quizzes(concept_id);
CREATE INDEX IF NOT EXISTS idx_academy_student_records_student ON karis_academy_student_records(student_identity_id);
CREATE INDEX IF NOT EXISTS idx_academy_scholarships_student ON karis_academy_scholarship_disbursements(student_identity_id);
