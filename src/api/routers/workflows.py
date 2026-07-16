from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.core.workflow_engine import workflow_engine

router = APIRouter(prefix="/api/v1/workflows", tags=["Declarative Workflow State Machine (Section 11.2)"])

class InitiateWorkflowRequest(BaseModel):
    workflow_code: str
    target_resource_id: str
    organization_id: str
    initiated_by_identity_id: str
    initial_context: Optional[Dict] = None

class AdvanceStateRequest(BaseModel):
    instance_id: str
    new_state: str
    actor_identity_id: str
    approval_notes: str = "Transition approved"

@router.get("/definitions", response_model=List[Dict])
def get_definitions():
    return list(workflow_engine.definitions.values())

@router.post("/initiate", status_code=status.HTTP_201_CREATED)
def initiate_workflow(req: InitiateWorkflowRequest):
    try:
        return workflow_engine.initiate_workflow(
            req.workflow_code, req.target_resource_id, req.organization_id, req.initiated_by_identity_id, req.initial_context
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/advance", status_code=status.HTTP_200_OK)
def advance_state(req: AdvanceStateRequest):
    try:
        return workflow_engine.advance_workflow_state(req.instance_id, req.new_state, req.actor_identity_id, req.approval_notes)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
