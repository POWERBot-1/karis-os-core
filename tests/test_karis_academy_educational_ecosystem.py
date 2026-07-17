import pytest
from datetime import datetime, timezone
import uuid
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType
from src.verticals.karis_academy.service import KarisAcademyService

@pytest.fixture
def karis_academy_env():
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0" * 64
    event_bus.event_store.clear()

    # Initialize baseline reserves and user wallets
    treasury = wallet_engine.get_or_create_wallet("ORG-TREASURY-MAIN", "ORG-COLLEGE-MACHAKOS", WalletType.RESERVE_WALLET, AssetType.KRT, 1000000.0)
    reward_pool = wallet_engine.get_or_create_wallet("TREASURY_IDENTITY", "ORG-COLLEGE-MACHAKOS", WalletType.REWARD_POOL, AssetType.KRT, 500000.0)
    student_krt = wallet_engine.get_or_create_wallet("USER-AMINA-777", "ORG-COLLEGE-MACHAKOS", WalletType.KRT_WALLET, AssetType.KRT, 0.0)

    svc = KarisAcademyService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
    return svc, event_bus, ledger_engine, wallet_engine

def test_karis_academy_institutions_concept_graphs_and_rule_10_artifacts(karis_academy_env):
    svc, eb, le, we = karis_academy_env

    # 1. Register institution
    inst = svc.register_institution("Machakos Institute of Technology", "TECHNICAL_UNIVERSITY", "EAST_AFRICA_TVET_VOCATIONAL", "ADMIN-EDU-01", "ORG-COLLEGE-MACHAKOS")
    assert inst.name == "Machakos Institute of Technology"

    # 2. Create concept node
    c = svc.create_concept_node(inst.institution_id, "Neural Network RAG Embeddings", "COMPUTER_SCIENCE_AI", ["CONCEPT-MATH-101"], 85.0, 250.0)
    assert c.mastery_threshold_pct == 85.0
    assert c.concept_id in svc.knowledge_engine.concepts

    # 3. Generate AI artifact locked at DRAFT_PENDING_EDUCATOR_APPROVAL (`Rule 10`)
    item = svc.generate_and_save_ai_artifact(c.concept_id, inst.institution_id, "SYSTEM-AI-GEN", "LESSON_NOTE_AND_QUIZ", "Neural Network RAG Embeddings")
    assert item.ai_generated_status == "DRAFT_PENDING_EDUCATOR_APPROVAL"
    assert item.version_number == 1

    # 4. Educator review & publish (`Rule 10 sign-off`)
    pub_item = svc.review_and_publish_lesson_or_quiz(item.item_id, "EDUCATOR-OMONDI-01", "ORG-COLLEGE-MACHAKOS")
    assert pub_item.ai_generated_status == "PUBLISHED_APPROVED"
    assert pub_item.version_number == 2

    # Verify events
    assert any(e.event_type == "ACADEMY_INSTITUTION_REGISTERED" for e in eb.event_store)
    assert any(e.event_type == "ACADEMY_CONCEPT_NODE_CREATED" for e in eb.event_store)
    assert any(e.event_type == "ACADEMY_LESSON_OR_QUIZ_PUBLISHED" for e in eb.event_store)

def test_karis_academy_student_mastery_and_scholarship_disbursement(karis_academy_env):
    svc, eb, le, we = karis_academy_env

    # 1. Certify Student Mastery (`96.5% >= 85% threshold`) -> Auto-mints +250 KRT-EDU (`Rule 5 & Rule 9`)
    mast_res = svc.record_student_mastery("USER-AMINA-777", "INST-01", "CONCEPT-AI-201", 96.5, "ORG-COLLEGE-MACHAKOS")
    assert mast_res["status"] == "MASTERY_CERTIFIED_SUCCESS"
    assert mast_res["krt_edu_reward_earned"] == 250.0
    assert mast_res["student_new_krt_balance"] == 250.0
    assert mast_res["reconciled_ledger_hash"] != "0" * 64

    # 2. Disburse Institutional Scholarship Stipend (`Rule 5 & Rule 9 double entry`)
    schol_res = svc.disburse_scholarship_stipend("USER-AMINA-777", "INST-01", 5000.0, "LIVING_STIPEND_AND_TUITION", "ORG-COLLEGE-MACHAKOS")
    assert schol_res["status"] == "SCHOLARSHIP_DISBURSED_SUCCESS"
    assert schol_res["amount_krt_disbursed"] == 5000.0
    assert schol_res["student_new_krt_balance"] == 5250.0  # 250 + 5000

    # Verify events
    assert any(e.event_type == "ACADEMY_STUDENT_MASTERY_COMPLETED" for e in eb.event_store)
    assert any(e.event_type == "ACADEMY_SCHOLARSHIP_DISBURSED" for e in eb.event_store)
