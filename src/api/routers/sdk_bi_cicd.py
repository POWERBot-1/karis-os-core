from fastapi import APIRouter, status
from pydantic import BaseModel
from src.integrations.sdk_generator import sdk_generator_engine
from src.observability.bi_aggregation import bi_executive_engine
from src.observability.cicd_quality_gate import cicd_quality_gate_engine

router = APIRouter(prefix="/api/v1/integrations", tags=["SDK Generator, Unified BI Dashboards & CI/CD Quality Gates (Sections 46, 27, 40)"])

class SdkGenRequest(BaseModel):
    organization_id: str = "ORG-KARIS-RETAIL"
    requested_by_identity_id: str = "DEV-CLIENT-01"

class CicdEvalRequest(BaseModel):
    commit_hash: str = "A8F291B0C4D5E6F7"
    branch_name: str = "main"
    pytest_pass_pct: float = 100.0
    stress_ops_sec: float = 2380.0
    security_vulns: int = 0
    organization_id: str = "ORG-KARIS-RETAIL"

@router.post("/sdk/generate-python", status_code=status.HTTP_201_CREATED)
def generate_python_sdk(req: SdkGenRequest):
    """Generates complete type-hinted Python Async/Sync client SDK (`karis_os_client.py`)."""
    return sdk_generator_engine.generate_python_sdk_package(req.organization_id, req.requested_by_identity_id)

@router.post("/sdk/generate-typescript", status_code=status.HTTP_201_CREATED)
def generate_typescript_sdk(req: SdkGenRequest):
    """Generates complete TypeScript / Node client SDK (`karis-os-sdk.ts`)."""
    return sdk_generator_engine.generate_typescript_sdk_package(req.organization_id, req.requested_by_identity_id)

@router.get("/analytics/bi/executive-report")
def get_bi_report(organization_id: str = "ORG-KARIS-RETAIL"):
    """Compiles C-suite intelligence across 5 domain dashboards (`Executive, Commerce, Delivery, Finance, Healthcare`)."""
    return bi_executive_engine.generate_unified_bi_executive_report(organization_id)

@router.post("/observability/cicd/evaluate-gate", status_code=status.HTTP_201_CREATED)
def evaluate_cicd_gate(req: CicdEvalRequest):
    """Verifies that all enterprise release thresholds are satisfied (`100% pytest`, `Rule 9 intact`, `>1500 ops/sec`)."""
    return cicd_quality_gate_engine.evaluate_cicd_release_quality_gate(
        req.commit_hash, req.branch_name, req.pytest_pass_pct, req.stress_ops_sec, req.security_vulns, req.organization_id
    )
