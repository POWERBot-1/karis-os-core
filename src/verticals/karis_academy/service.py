import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from src.domain.models import (
    KarisAcademyInstitutionModel, KarisAcademyConceptNodeModel,
    KarisAcademyLessonQuizModel, KarisAcademyStudentRecordModel,
    KarisAcademyScholarshipModel, EventPayload, AssetType, WalletType
)
from src.core.event_bus import event_bus, UniversalEventBus
from src.core.ledger_engine import ledger_engine, UniversalLedgerEngine
from src.core.wallet_engine import wallet_engine, MultiAssetWalletEngine
from src.verticals.karis_academy.ai_copilot import KarisAcademyAICopilot
from src.verticals.karis_academy.knowledge_engine import KarisAcademyKnowledgeEngine

class KarisAcademyService:
    """
    KARIS OS™ :: KARIS Academy™ AI Educational Ecosystem (`Section 55 / Vertical 20`).
    Unifies Interconnected Concept Graphs, 14 AI-Generated Educational Artifacts under Rule 10,
    7 AI Learning Assistants, Immutable Academic Transcripts (`Rule 9`), and KRT-EDU Utility Rewards.
    """
    def __init__(
        self,
        event_bus: UniversalEventBus,
        ledger_engine: UniversalLedgerEngine,
        wallet_engine: MultiAssetWalletEngine
    ):
        self.event_bus = event_bus
        self.ledger_engine = ledger_engine
        self.wallet_engine = wallet_engine
        self.ai_copilot = KarisAcademyAICopilot()
        self.knowledge_engine = KarisAcademyKnowledgeEngine()

        self.institutions: Dict[str, KarisAcademyInstitutionModel] = {}
        self.lessons_and_quizzes: Dict[str, KarisAcademyLessonQuizModel] = {}
        self.student_records: Dict[str, KarisAcademyStudentRecordModel] = {}
        self.scholarships: Dict[str, KarisAcademyScholarshipModel] = {}

    def register_institution(
        self,
        name: str,
        institution_type: str,
        curriculum_framework: str,
        admin_identity_id: str,
        organization_id: str = "ORG-COLLEGE-MACHAKOS"
    ) -> KarisAcademyInstitutionModel:
        """Registers a school, college, university, or training center (`Section 55.1`)."""
        inst = KarisAcademyInstitutionModel(
            organization_id=organization_id,
            name=name,
            institution_type=institution_type,
            curriculum_framework=curriculum_framework,
            admin_identity_id=admin_identity_id
        )
        self.institutions[inst.institution_id] = inst

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="ACADEMY_INSTITUTION_REGISTERED",
            event_category="EDUCATION",
            actor_identity_id=admin_identity_id,
            organization_id=organization_id,
            correlation_id=inst.institution_id,
            source_module="KARIS_ACADEMY_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload=inst.model_dump(mode="json")
        )
        self.event_bus.publish(ev)
        return inst

    def create_concept_node(
        self,
        institution_id: str,
        title: str,
        category_domain: str = "COMPUTER_SCIENCE_AI",
        prerequisites: List[str] = None,
        mastery_threshold: float = 85.0,
        krt_reward: float = 250.0
    ) -> KarisAcademyConceptNodeModel:
        """Creates an interconnected concept node inside the Knowledge Engine (`Section 55.2`)."""
        c = self.knowledge_engine.add_concept_node(institution_id, title, category_domain, prerequisites, mastery_threshold, krt_reward)
        
        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="ACADEMY_CONCEPT_NODE_CREATED",
            event_category="EDUCATION",
            actor_identity_id="SYSTEM_KNOWLEDGE_ENGINE",
            organization_id="ORG-COLLEGE-MACHAKOS",
            correlation_id=c.concept_id,
            source_module="KARIS_ACADEMY_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload=c.model_dump(mode="json")
        )
        self.event_bus.publish(ev)
        return c

    def generate_and_save_ai_artifact(
        self,
        concept_id: str,
        institution_id: str,
        creator_identity_id: str,
        artifact_type: str = "LESSON_NOTE_AND_QUIZ",
        topic_title: str = "Neural Network RAG Embeddings & Vector Search"
    ) -> KarisAcademyLessonQuizModel:
        """Generates AI educational artifact locked at `DRAFT_PENDING_EDUCATOR_APPROVAL` (`Rule 10`)."""
        art_res = self.ai_copilot.generate_educational_artifact(concept_id, institution_id, artifact_type, topic_title)
        
        item = KarisAcademyLessonQuizModel(
            concept_id=concept_id,
            institution_id=institution_id,
            creator_identity_id=creator_identity_id,
            item_type=artifact_type,
            title=topic_title,
            content_payload_json=art_res["content_payload_json"],
            version_number=1,
            ai_generated_status="DRAFT_PENDING_EDUCATOR_APPROVAL"
        )
        self.lessons_and_quizzes[item.item_id] = item
        return item

    def review_and_publish_lesson_or_quiz(
        self,
        item_id: str,
        educator_identity_id: str,
        organization_id: str = "ORG-COLLEGE-MACHAKOS"
    ) -> KarisAcademyLessonQuizModel:
        """
        Enforces Rule 10 (`AI Assists; Humans Approve`).
        Educator reviews, edits, and signs off on an AI-generated artifact, setting status to `PUBLISHED_APPROVED`.
        Emits ACADEMY_LESSON_OR_QUIZ_PUBLISHED (`Rule 6`).
        """
        if item_id not in self.lessons_and_quizzes:
            raise KeyError(f"Lesson/Quiz Item ID {item_id} not found.")
        item = self.lessons_and_quizzes[item_id]

        item.ai_generated_status = "PUBLISHED_APPROVED"
        item.version_number += 1

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="ACADEMY_LESSON_OR_QUIZ_PUBLISHED",
            event_category="EDUCATION",
            actor_identity_id=educator_identity_id,
            organization_id=organization_id,
            correlation_id=item.item_id,
            source_module="KARIS_ACADEMY_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "item_id": item.item_id,
                "concept_id": item.concept_id,
                "institution_id": item.institution_id,
                "item_type": item.item_type,
                "title": item.title,
                "version_number": item.version_number,
                "ai_generated_status": item.ai_generated_status
            }
        )
        self.event_bus.publish(ev)
        return item

    def record_student_mastery(
        self,
        student_identity_id: str,
        institution_id: str,
        concept_id: str,
        mastery_score_pct: float,
        organization_id: str = "ORG-COLLEGE-MACHAKOS"
    ) -> Dict[str, Any]:
        """
        Records immutable academic transcript entry (`Rule 9`).
        If `mastery_score_pct >= mastery_threshold_pct`, automatically mints `KRT-EDU` utility reward
        tokens (`+250 KRT-EDU`) via exact double-entry accounting (`Rule 5 & Rule 9`).
        """
        if concept_id not in self.knowledge_engine.concepts:
            raise KeyError(f"Concept Node {concept_id} not found.")
        c_node = self.knowledge_engine.concepts[concept_id]

        if mastery_score_pct < c_node.mastery_threshold_pct:
            raise ValueError(f"Score {mastery_score_pct}% below mastery threshold {c_node.mastery_threshold_pct}% for {c_node.title}.")

        reward_krt = c_node.krt_reward_on_mastery
        student_krt = self.wallet_engine.get_or_create_wallet(student_identity_id, organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)
        treasury_reward = self.wallet_engine.get_or_create_wallet("TREASURY_IDENTITY", organization_id, WalletType.REWARD_POOL, AssetType.KRT, 1000000.0)

        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=treasury_reward.wallet_id,
            credit_wallet_id=student_krt.wallet_id,
            amount=reward_krt,
            currency="KRT",
            organization_id=organization_id,
            trigger_event_id=f"MASTERY-{concept_id[:8]}-{student_identity_id[:6]}",
            description=f"KARIS Academy Mastery Reward ({reward_krt} KRT-EDU) for mastering {c_node.title} ({mastery_score_pct}%)"
        )

        record = KarisAcademyStudentRecordModel(
            student_identity_id=student_identity_id,
            institution_id=institution_id,
            concept_id=concept_id,
            mastery_score_pct=mastery_score_pct,
            completion_status="MASTERY_CERTIFIED",
            krt_edu_reward_earned=reward_krt,
            reconciled_ledger_hash=self.ledger_engine.last_hash
        )
        self.student_records[record.record_id] = record

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="ACADEMY_STUDENT_MASTERY_COMPLETED",
            event_category="EDUCATION",
            actor_identity_id=student_identity_id,
            organization_id=organization_id,
            correlation_id=tx_id,
            source_module="KARIS_ACADEMY_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "record_id": record.record_id,
                "student_identity_id": student_identity_id,
                "institution_id": institution_id,
                "concept_id": concept_id,
                "mastery_score_pct": mastery_score_pct,
                "krt_edu_reward_earned": reward_krt,
                "reference_transaction_id": tx_id
            }
        )
        self.event_bus.publish(ev)

        return {
            "status": "MASTERY_CERTIFIED_SUCCESS",
            "record_id": record.record_id,
            "concept_title": c_node.title,
            "mastery_score_pct": mastery_score_pct,
            "krt_edu_reward_earned": reward_krt,
            "student_new_krt_balance": student_krt.balance,
            "reconciled_ledger_hash": self.ledger_engine.last_hash
        }

    def disburse_scholarship_stipend(
        self,
        student_identity_id: str,
        institution_id: str,
        amount_krt: float = 5000.0,
        disbursement_type: str = "LIVING_STIPEND_AND_TUITION",
        organization_id: str = "ORG-COLLEGE-MACHAKOS"
    ) -> Dict[str, Any]:
        """Disburses institutional scholarship stipend via double-entry accounting (`Rule 5 & Rule 9`)."""
        if amount_krt <= 0:
            raise ValueError("Scholarship disbursement must be greater than 0.")

        scholarship_pool = self.wallet_engine.get_or_create_wallet("POOL-ACADEMY-SCHOLARSHIP-01", organization_id, WalletType.RESERVE_WALLET, AssetType.KRT, 500000.0)
        student_krt = self.wallet_engine.get_or_create_wallet(student_identity_id, organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)

        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=scholarship_pool.wallet_id,
            credit_wallet_id=student_krt.wallet_id,
            amount=amount_krt,
            currency="KRT",
            organization_id=organization_id,
            trigger_event_id=f"SCHOLAR-{student_identity_id[:6]}",
            description=f"KARIS Academy Scholarship Disbursement ({amount_krt} KRT: {disbursement_type})"
        )

        disb = KarisAcademyScholarshipModel(
            institution_id=institution_id,
            student_identity_id=student_identity_id,
            amount_krt=amount_krt,
            disbursement_type=disbursement_type,
            reconciled_ledger_hash=self.ledger_engine.last_hash
        )
        self.scholarships[disb.disbursement_id] = disb

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="ACADEMY_SCHOLARSHIP_DISBURSED",
            event_category="EDUCATION",
            actor_identity_id="SYSTEM_SCHOLARSHIP_POOL",
            organization_id=organization_id,
            correlation_id=tx_id,
            source_module="KARIS_ACADEMY_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "disbursement_id": disb.disbursement_id,
                "institution_id": institution_id,
                "student_identity_id": student_identity_id,
                "amount_krt": amount_krt,
                "disbursement_type": disbursement_type,
                "reference_transaction_id": tx_id
            }
        )
        self.event_bus.publish(ev)

        return {
            "status": "SCHOLARSHIP_DISBURSED_SUCCESS",
            "disbursement_id": disb.disbursement_id,
            "student_identity_id": student_identity_id,
            "amount_krt_disbursed": amount_krt,
            "student_new_krt_balance": student_krt.balance,
            "audit_hash": self.ledger_engine.last_hash
        }

karis_academy_service = KarisAcademyService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
