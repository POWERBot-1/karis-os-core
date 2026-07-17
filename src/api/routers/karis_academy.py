from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from src.verticals.karis_academy.service import karis_academy_service, KarisAcademyService

router = APIRouter(prefix="/api/v1/karis-academy", tags=["KARIS ACADEMY™ AI Educational Ecosystem (`Section 55 - Vertical 20`)"])

def get_academy_service() -> KarisAcademyService:
    return karis_academy_service

class RegisterInstitutionRequest(BaseModel):
    name: str = "Machakos Institute of Technology"
    institution_type: str = "TECHNICAL_UNIVERSITY"
    curriculum_framework: str = "EAST_AFRICA_TVET_VOCATIONAL"
    admin_identity_id: str = "ADMIN-EDU-01"
    organization_id: str = "ORG-COLLEGE-MACHAKOS"

class CreateConceptNodeRequest(BaseModel):
    institution_id: str
    title: str = "Neural Network RAG Embeddings & Vector Search"
    category_domain: str = "COMPUTER_SCIENCE_AI"
    prerequisites: List[str] = ["CONCEPT-MATH-101"]
    mastery_threshold: float = 85.0
    krt_reward: float = 250.0

class GenerateArtifactRequest(BaseModel):
    concept_id: str
    institution_id: str
    creator_identity_id: str
    artifact_type: str = "LESSON_NOTE_AND_QUIZ"
    topic_title: str = "Neural Network RAG Embeddings & Vector Search"

class ReviewPublishRequest(BaseModel):
    item_id: str
    educator_identity_id: str
    organization_id: str = "ORG-COLLEGE-MACHAKOS"

class RecordMasteryRequest(BaseModel):
    student_identity_id: str
    institution_id: str
    concept_id: str
    mastery_score_pct: float = 96.5
    organization_id: str = "ORG-COLLEGE-MACHAKOS"

class DisburseScholarshipRequest(BaseModel):
    student_identity_id: str
    institution_id: str
    amount_krt: float = 5000.0
    disbursement_type: str = "LIVING_STIPEND_AND_TUITION"
    organization_id: str = "ORG-COLLEGE-MACHAKOS"

@router.post("/institutions")
def reg_inst(req: RegisterInstitutionRequest, svc: KarisAcademyService = Depends(get_academy_service)):
    inst = svc.register_institution(req.name, req.institution_type, req.curriculum_framework, req.admin_identity_id, req.organization_id)
    return {"status": "INSTITUTION_REGISTERED", "institution": inst.model_dump()}

@router.post("/concepts")
def create_concept(req: CreateConceptNodeRequest, svc: KarisAcademyService = Depends(get_academy_service)):
    c = svc.create_concept_node(req.institution_id, req.title, req.category_domain, req.prerequisites, req.mastery_threshold, req.krt_reward)
    return {"status": "CONCEPT_NODE_CREATED", "concept": c.model_dump()}

@router.post("/ai/generate-artifact")
def gen_art(req: GenerateArtifactRequest, svc: KarisAcademyService = Depends(get_academy_service)):
    item = svc.generate_and_save_ai_artifact(req.concept_id, req.institution_id, req.creator_identity_id, req.artifact_type, req.topic_title)
    return {"status": "ARTIFACT_GENERATED_DRAFT", "artifact": item.model_dump()}

@router.post("/lessons/review-publish")
def pub_lesson(req: ReviewPublishRequest, svc: KarisAcademyService = Depends(get_academy_service)):
    try:
        item = svc.review_and_publish_lesson_or_quiz(req.item_id, req.educator_identity_id, req.organization_id)
        return {"status": "ARTIFACT_PUBLISHED_APPROVED", "artifact": item.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/mastery")
def record_mastery(req: RecordMasteryRequest, svc: KarisAcademyService = Depends(get_academy_service)):
    try:
        return svc.record_student_mastery(req.student_identity_id, req.institution_id, req.concept_id, req.mastery_score_pct, req.organization_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/scholarship")
def disburse_schol(req: DisburseScholarshipRequest, svc: KarisAcademyService = Depends(get_academy_service)):
    try:
        return svc.disburse_scholarship_stipend(req.student_identity_id, req.institution_id, req.amount_krt, req.disbursement_type, req.organization_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
