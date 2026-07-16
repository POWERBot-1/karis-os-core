from fastapi import APIRouter, status
from pydantic import BaseModel
from src.observability.k8s_autoscaler import k8s_hpa_engine

router = APIRouter(prefix="/api/v1/observability/k8s", tags=["Multi-Cloud Kubernetes HPA Autoscaling & Container Orchestration (Section 40.3 & 40.4)"])

class HpaEvaluateRequest(BaseModel):
    request_velocity_ops_per_sec: float = 2380.0
    cpu_utilization_pct: float = 88.5
    target_service: str = "karis-api-gateway"
    cluster_node_code: str = "CLUSTER-NAIROBI-MAIN"
    organization_id: str = "SYSTEM_CORE_ORG"

@router.post("/hpa-evaluate", status_code=status.HTTP_200_OK)
def evaluate_hpa_scaling(req: HpaEvaluateRequest):
    """Evaluates live request velocity (`ops/sec`) and CPU load, dynamically scaling container pod replicas (`4 -> 16 pods`)."""
    return k8s_hpa_engine.evaluate_traffic_load_and_scale_pods(
        req.request_velocity_ops_per_sec, req.cpu_utilization_pct, req.target_service,
        req.cluster_node_code, req.organization_id
    )
