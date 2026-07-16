import uuid
from typing import Dict, Optional
from src.domain.models import EventCategory, EventPayload, HealthcareAppointmentModel, HealthcarePrescriptionModel
from src.core.event_bus import event_bus

class HealthcareMedicalService:
    """
    KARIS OS™ Healthcare & Medical Services Service.
    Enforces Section 32 (Healthcare & Medical Services Vertical).
    Manages Patient EMR Profiles, Appointments, Digital Prescriptions, and CHV Maternal Health Workflows.
    """
    def __init__(self):
        self.facilities: Dict[str, Dict] = {}
        self.patients: Dict[str, Dict] = {}
        self.appointments: Dict[str, HealthcareAppointmentModel] = {}
        self.prescriptions: Dict[str, HealthcarePrescriptionModel] = {}

    def register_facility(self, organization_id: str, name: str, facility_type: str = "COUNTY_HOSPITAL") -> Dict:
        fac = {
            "facility_id": str(uuid.uuid4()),
            "organization_id": organization_id,
            "facility_name": name,
            "facility_type": facility_type
        }
        self.facilities[fac["facility_id"]] = fac
        return fac

    def register_patient(self, identity_id: str, blood_group: str = "O+", chv_identity_id: Optional[str] = None) -> Dict:
        patient = {
            "patient_id": str(uuid.uuid4()),
            "identity_id": identity_id,
            "blood_group": blood_group,
            "chv_assigned_identity_id": chv_identity_id,
            "consent_recorded": True
        }
        self.patients[patient["patient_id"]] = patient
        return patient

    def book_appointment(
        self,
        facility_id: str,
        patient_id: str,
        doctor_identity_id: str,
        appointment_type: str = "TELEMEDICINE",
        consultation_fee_kes: float = 1500.0
    ) -> HealthcareAppointmentModel:
        if facility_id not in self.facilities:
            raise KeyError(f"Facility ID {facility_id} not found.")
        if patient_id not in self.patients:
            raise KeyError(f"Patient ID {patient_id} not found.")

        apt = HealthcareAppointmentModel(
            appointment_id=str(uuid.uuid4()),
            facility_id=facility_id,
            patient_id=patient_id,
            doctor_identity_id=doctor_identity_id,
            appointment_type=appointment_type,
            consultation_fee_kes=consultation_fee_kes
        )
        self.appointments[apt.appointment_id] = apt

        fac = self.facilities[facility_id]
        ev = EventPayload(
            event_type="HEALTHCARE_APPOINTMENT_BOOKED",
            event_category=EventCategory.HEALTHCARE,
            actor_identity_id=self.patients[patient_id]["identity_id"],
            organization_id=fac["organization_id"],
            correlation_id=apt.appointment_id,
            source_module="HEALTHCARE_ENGINE",
            payload=apt.model_dump(mode="json")
        )
        event_bus.publish(ev)
        return apt

    def issue_prescription(
        self,
        appointment_id: str,
        medication_product_id: str,
        quantity: float,
        diagnosis_summary: str = "Standard checkup approved"
    ) -> HealthcarePrescriptionModel:
        if appointment_id not in self.appointments:
            raise KeyError(f"Appointment ID {appointment_id} not found.")

        apt = self.appointments[appointment_id]
        emr_note_id = str(uuid.uuid4())

        presc = HealthcarePrescriptionModel(
            prescription_id=str(uuid.uuid4()),
            emr_note_id=emr_note_id,
            patient_id=apt.patient_id,
            doctor_identity_id=apt.doctor_identity_id,
            medication_product_id=medication_product_id,
            quantity_prescribed=quantity
        )
        self.prescriptions[presc.prescription_id] = presc

        fac = self.facilities.get(apt.facility_id, {"organization_id": "ORG_HEALTH_DEFAULT"})
        ev = EventPayload(
            event_type="HEALTHCARE_PRESCRIPTION_CREATED",
            event_category=EventCategory.HEALTHCARE,
            actor_identity_id=apt.doctor_identity_id,
            organization_id=fac["organization_id"],
            correlation_id=presc.prescription_id,
            source_module="HEALTHCARE_ENGINE",
            payload=presc.model_dump(mode="json")
        )
        event_bus.publish(ev)
        return presc

    def record_chv_visit(self, organization_id: str, chv_identity_id: str, patient_id: str, notes: str) -> Dict:
        """Section 32.9: Community Health Volunteer (CHV) Maternal Health Check."""
        visit_id = str(uuid.uuid4())
        ev = EventPayload(
            event_type="EXTENSION_OFFICER_VISIT", # Triggering KRT incentive via Rule Engine
            event_category=EventCategory.HEALTHCARE,
            actor_identity_id=chv_identity_id,
            organization_id=organization_id,
            correlation_id=visit_id,
            source_module="HEALTHCARE_ENGINE",
            payload={
                "visit_id": visit_id,
                "chv_identity_id": chv_identity_id,
                "patient_id": patient_id,
                "notes": notes,
                "krt_incentive_eligible": 50.0
            }
        )
        event_bus.publish(ev)
        return {"status": "SUCCESS", "visit_id": visit_id, "chv_identity_id": chv_identity_id}

healthcare_service = HealthcareMedicalService()
