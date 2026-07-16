from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.verticals.healthcare.service import healthcare_service

router = APIRouter(prefix="/api/v1/healthcare", tags=["Healthcare, EMR & Medical Services Vertical"])

class RegisterFacilityRequest(BaseModel):
    organization_id: str
    name: str
    facility_type: str = "COUNTY_HOSPITAL"

class RegisterPatientRequest(BaseModel):
    identity_id: str
    blood_group: str = "O+"
    chv_identity_id: Optional[str] = None

class BookAppointmentRequest(BaseModel):
    facility_id: str
    patient_id: str
    doctor_identity_id: str
    appointment_type: str = "TELEMEDICINE"
    consultation_fee_kes: float = 1500.0

class IssuePrescriptionRequest(BaseModel):
    appointment_id: str
    medication_product_id: str
    quantity: float
    diagnosis_summary: str = "Standard checkup approved"

class RecordChvVisitRequest(BaseModel):
    organization_id: str
    chv_identity_id: str
    patient_id: str
    notes: str

@router.post("/facilities", status_code=status.HTTP_201_CREATED)
def register_facility(req: RegisterFacilityRequest):
    return healthcare_service.register_facility(req.organization_id, req.name, req.facility_type)

@router.post("/patients", status_code=status.HTTP_201_CREATED)
def register_patient(req: RegisterPatientRequest):
    return healthcare_service.register_patient(req.identity_id, req.blood_group, req.chv_identity_id)

@router.post("/appointments", status_code=status.HTTP_201_CREATED)
def book_appointment(req: BookAppointmentRequest):
    try:
        return healthcare_service.book_appointment(
            req.facility_id, req.patient_id, req.doctor_identity_id, req.appointment_type, req.consultation_fee_kes
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/prescriptions", status_code=status.HTTP_201_CREATED)
def issue_prescription(req: IssuePrescriptionRequest):
    try:
        return healthcare_service.issue_prescription(
            req.appointment_id, req.medication_product_id, req.quantity, req.diagnosis_summary
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/chv-visits", status_code=status.HTTP_201_CREATED)
def record_chv_visit(req: RecordChvVisitRequest):
    return healthcare_service.record_chv_visit(req.organization_id, req.chv_identity_id, req.patient_id, req.notes)
