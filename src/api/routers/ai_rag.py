from fastapi import APIRouter
from pydantic import BaseModel
from src.ai.agents import multi_agent_suite

router = APIRouter(prefix="/api/v1/ai", tags=["AI Multi-Agent Orchestration & Vector RAG (Section 13 & 39)"])

class AskAgriRequest(BaseModel):
    query: str

class AskSupportRequest(BaseModel):
    subject: str
    description: str

@router.get("/executive-briefing")
def get_executive_briefing(organization_id: str = "ORG-KARIS-RETAIL"):
    """Returns an executive intelligence summary across platform volume and treasury health."""
    return multi_agent_suite.get_executive_briefing(organization_id)

@router.post("/agriculture/ask")
def ask_agriculture(req: AskAgriRequest):
    """Answers agricultural queries using local/cloud Vector RAG grounding (`AgricultureAgent`)."""
    return multi_agent_suite.ask_agriculture_agent(req.query)

@router.post("/support/ask")
def ask_support(req: AskSupportRequest):
    """Classifies inbound support tickets and suggests RAG-backed resolutions (`SupportAgent`)."""
    return multi_agent_suite.ask_support_agent(req.subject, req.description)
