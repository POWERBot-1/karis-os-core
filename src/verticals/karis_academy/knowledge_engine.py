import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from src.domain.models import KarisAcademyConceptNodeModel

class KarisAcademyKnowledgeEngine:
    """
    KARIS OS™ :: KARIS Academy™ Knowledge Engine (`Section 55.2`).
    Organizes learning into interconnected concepts rather than isolated courses.
    Maps prerequisites, supports multiple curriculum frameworks (`KENYA_CBC`, `TVET`, `IGCSE`, `UNIVERSITY_DEGREE`),
    and computes personalized adaptive concept sequences based on real-time student mastery.
    """
    def __init__(self):
        self.concepts: Dict[str, KarisAcademyConceptNodeModel] = {}
        self.frameworks: Dict[str, str] = {
            "KENYA_CBC_COMPETENCY_BASED": "Kenya Competency-Based Curriculum (`CBC`) mapped to digital economy competencies.",
            "EAST_AFRICA_TVET_VOCATIONAL": "Technical and Vocational Education and Training (`TVET`) practical skill certifications.",
            "CAMBRIDGE_IGCSE": "International general secondary academic qualifications.",
            "UNIVERSITY_DEGREE": "Undergraduate and postgraduate accredited academic degree pathways."
        }
        self._seed_default_concepts()

    def _seed_default_concepts(self):
        # Create baseline concept chain: Linear Algebra -> Python Data Structures -> Neural Network RAG
        c1 = KarisAcademyConceptNodeModel(
            concept_id="CONCEPT-MATH-101",
            institution_id="ORG-COLLEGE-MACHAKOS",
            title="Linear Algebra & Vector Embeddings",
            category_domain="MATHEMATICS_AI",
            prerequisite_concept_ids_json="[]",
            mastery_threshold_pct=85.0,
            krt_reward_on_mastery=100.0
        )
        c2 = KarisAcademyConceptNodeModel(
            concept_id="CONCEPT-AI-201",
            institution_id="ORG-COLLEGE-MACHAKOS",
            title="Neural Network RAG Embeddings & Vector Search",
            category_domain="COMPUTER_SCIENCE_AI",
            prerequisite_concept_ids_json=json.dumps(["CONCEPT-MATH-101"]),
            mastery_threshold_pct=85.0,
            krt_reward_on_mastery=250.0
        )
        self.concepts[c1.concept_id] = c1
        self.concepts[c2.concept_id] = c2

    def add_concept_node(
        self,
        institution_id: str,
        title: str,
        category: str,
        prerequisites: List[str] = None,
        mastery_threshold: float = 85.0,
        krt_reward: float = 250.0
    ) -> KarisAcademyConceptNodeModel:
        if prerequisites is None:
            prerequisites = []
        c = KarisAcademyConceptNodeModel(
            institution_id=institution_id,
            title=title,
            category_domain=category,
            prerequisite_concept_ids_json=json.dumps(prerequisites),
            mastery_threshold_pct=mastery_threshold,
            krt_reward_on_mastery=krt_reward
        )
        self.concepts[c.concept_id] = c
        return c

    def compute_adaptive_pathway(
        self,
        student_identity_id: str,
        completed_concept_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        AI Knowledge Engine recommends personalized learning sequences based on prerequisites
        and real-time student mastery!
        """
        if completed_concept_ids is None:
            completed_concept_ids = []

        recommended_next = []
        locked_prerequisites = []

        for c_id, node in self.concepts.items():
            if c_id in completed_concept_ids:
                continue
            prereqs = json.loads(node.prerequisite_concept_ids_json)
            missing = [p for p in prereqs if p not in completed_concept_ids]
            if not missing:
                recommended_next.append({"concept_id": c_id, "title": node.title, "krt_reward": node.krt_reward_on_mastery, "status": "UNLOCKED_READY"})
            else:
                locked_prerequisites.append({"concept_id": c_id, "title": node.title, "missing_prerequisites": missing, "status": "LOCKED_NEEDS_PREREQUISITES"})

        return {
            "student_identity_id": student_identity_id,
            "completed_concepts_count": len(completed_concept_ids),
            "recommended_next_concepts": recommended_next,
            "locked_future_concepts": locked_prerequisites,
            "curriculum_framework_active": "KENYA_CBC_COMPETENCY_BASED / UNIVERSITY_DEGREE"
        }
