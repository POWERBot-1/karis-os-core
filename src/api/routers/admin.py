from typing import Dict, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from src.db.database import engine

router = APIRouter(prefix="/api/v1/admin", tags=["Administration & Configuration Console (Section 43)"])

class RuleDefinitionModel(BaseModel):
    rule_id: str
    organization_id: str
    rule_code: str
    rule_name: str
    description: str
    trigger_event_type: str
    conditions: List[Dict]
    actions: List[Dict]
    priority: int = 100
    is_active: bool = True

class WorkflowDefinitionModel(BaseModel):
    workflow_def_id: str
    organization_id: str
    workflow_code: str
    workflow_name: str
    vertical: str
    steps: List[Dict]
    is_active: bool = True

@router.get("/rules", response_model=List[Dict])
def get_business_rules():
    """Returns all declarative business rules currently active across multi-tenant organizations."""
    with engine.connect() as conn:
        res = conn.execute(text("SELECT rule_id, organization_id, rule_code, rule_name, trigger_event_type, is_active FROM business_rules;"))
        return [dict(row._mapping) for row in res]

@router.post("/rules", status_code=status.HTTP_201_CREATED)
def create_business_rule(rule: RuleDefinitionModel):
    """Dynamically creates or updates a declarative business rule without source-code modification (Rule 7)."""
    import json
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO business_rules (rule_id, organization_id, rule_code, rule_name, description, trigger_event_type, conditions, actions, priority, is_active)
            VALUES (:id, :org, :code, :name, :desc, :trigger, :cond, :act, :prio, :active)
        """), {
            "id": rule.rule_id, "org": rule.organization_id, "code": rule.rule_code, "name": rule.rule_name,
            "desc": rule.description, "trigger": rule.trigger_event_type,
            "cond": json.dumps(rule.conditions), "act": json.dumps(rule.actions),
            "prio": rule.priority, "active": 1 if rule.is_active else 0
        })
        conn.commit()
    return {"status": "SUCCESS", "message": f"Declarative rule '{rule.rule_code}' created.", "rule_id": rule.rule_id}

@router.get("/workflows", response_model=List[Dict])
def get_workflows():
    """Returns all declarative workflow definitions across verticals."""
    with engine.connect() as conn:
        res = conn.execute(text("SELECT workflow_def_id, organization_id, workflow_code, workflow_name, vertical, is_active FROM workflow_definitions;"))
        return [dict(row._mapping) for row in res]
