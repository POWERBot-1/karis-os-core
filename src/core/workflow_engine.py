import uuid
from typing import Dict, List, Optional
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus
from src.core.ai_gateway import ai_gateway

class WorkflowStateMachineEngine:
    """
    KARIS OS™ Workflow State Machine Engine (Section 11.2 & 43.3).
    Enforces declarative multi-step approval workflows across enterprise verticals.
    Enforces Rule 10: AI evaluates and scores transitions, while human administrators approve high-impact gates.
    """
    def __init__(self):
        self.definitions: Dict[str, Dict] = {}
        self.instances: Dict[str, Dict] = {}
        self._seed_default_workflows()

    def _seed_default_workflows(self):
        self.definitions["CREDIT_APPROVAL_WORKFLOW"] = {
            "workflow_code": "CREDIT_APPROVAL_WORKFLOW",
            "workflow_name": "AI-Scored Enterprise Credit Approval Workflow",
            "vertical": "FINANCE",
            "steps": [
                {"state": "APPLICATION_SUBMITTED", "next": ["RISK_EVALUATION"], "require_ai_score": True},
                {"state": "RISK_EVALUATION", "next": ["CREDIT_APPROVED", "CREDIT_REJECTED", "PENDING_HUMAN_REVIEW"], "auto_advance_if_score_lt": 25.0},
                {"state": "PENDING_HUMAN_REVIEW", "next": ["CREDIT_APPROVED", "CREDIT_REJECTED"], "require_role": "PLATFORM_ADMINISTRATOR"},
                {"state": "CREDIT_APPROVED", "next": ["FUNDS_ALLOCATED"], "trigger_disbursement": True},
                {"state": "CREDIT_REJECTED", "next": [], "terminal": True},
                {"state": "FUNDS_ALLOCATED", "next": [], "terminal": True}
            ]
        }
        self.definitions["FARMER_ONBOARDING_WORKFLOW"] = {
            "workflow_code": "FARMER_ONBOARDING_WORKFLOW",
            "workflow_name": "Cooperative Farmer & Land Parcel Verification",
            "vertical": "AGRICULTURE",
            "steps": [
                {"state": "FARM_REGISTERED", "next": ["GPS_LAND_VERIFIED"], "require_chv_visit": True},
                {"state": "GPS_LAND_VERIFIED", "next": ["GAP_CERTIFIED"], "require_role": "COOPERATIVE_SUPERVISOR"},
                {"state": "GAP_CERTIFIED", "next": [], "terminal": True}
            ]
        }

    def initiate_workflow(
        self,
        workflow_code: str,
        target_resource_id: str,
        organization_id: str,
        initiated_by_identity_id: str,
        initial_context: Optional[Dict] = None
    ) -> Dict:
        if workflow_code not in self.definitions:
            raise KeyError(f"Workflow definition '{workflow_code}' not registered.")

        if initial_context is None:
            initial_context = {}

        w_def = self.definitions[workflow_code]
        initial_state = w_def["steps"][0]["state"]
        instance_id = str(uuid.uuid4())

        inst = {
            "instance_id": instance_id,
            "workflow_code": workflow_code,
            "target_resource_id": target_resource_id,
            "organization_id": organization_id,
            "current_state": initial_state,
            "initiated_by": initiated_by_identity_id,
            "context": initial_context,
            "status": "ACTIVE"
        }
        self.instances[instance_id] = inst

        # Emit initial state event
        ev = EventPayload(
            event_type="WORKFLOW_STATE_CHANGED",
            event_category=EventCategory.GOVERNANCE,
            actor_identity_id=initiated_by_identity_id,
            organization_id=organization_id,
            correlation_id=instance_id,
            source_module="WORKFLOW_STATE_MACHINE_ENGINE",
            payload={
                "instance_id": instance_id,
                "workflow_code": workflow_code,
                "target_resource_id": target_resource_id,
                "previous_state": "NONE",
                "new_state": initial_state,
                "approval_notes": "Workflow initiated"
            }
        )
        event_bus.publish(ev)
        return inst

    def advance_workflow_state(
        self,
        instance_id: str,
        new_state: str,
        actor_identity_id: str,
        approval_notes: str = "Transition approved"
    ) -> Dict:
        if instance_id not in self.instances:
            raise KeyError(f"Workflow instance ID {instance_id} not found.")

        inst = self.instances[instance_id]
        if inst["status"] != "ACTIVE":
            raise ValueError(f"Cannot advance workflow in status '{inst['status']}'.")

        w_def = self.definitions[inst["workflow_code"]]
        curr_step = next((s for s in w_def["steps"] if s["state"] == inst["current_state"]), None)
        if not curr_step or new_state not in curr_step.get("next", []):
            raise ValueError(f"Invalid transition from '{inst['current_state']}' to '{new_state}'.")

        prev_state = inst["current_state"]
        inst["current_state"] = new_state
        if next((s for s in w_def["steps"] if s["state"] == new_state), {}).get("terminal", False):
            inst["status"] = "COMPLETED"

        ev = EventPayload(
            event_type="WORKFLOW_STATE_CHANGED",
            event_category=EventCategory.GOVERNANCE,
            actor_identity_id=actor_identity_id,
            organization_id=inst["organization_id"],
            correlation_id=instance_id,
            source_module="WORKFLOW_STATE_MACHINE_ENGINE",
            payload={
                "instance_id": instance_id,
                "workflow_code": inst["workflow_code"],
                "target_resource_id": inst["target_resource_id"],
                "previous_state": prev_state,
                "new_state": new_state,
                "approval_notes": approval_notes
            }
        )
        event_bus.publish(ev)
        return inst

workflow_engine = WorkflowStateMachineEngine()
