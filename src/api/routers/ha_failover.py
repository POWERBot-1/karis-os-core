from typing import Dict, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.observability.ha_failover import ha_failover_engine

router = APIRouter(prefix="/api/v1/observability/ha", tags=["Active-Active High Availability & Geographic Failover (Section 40.8)"])

class ExecuteFailoverRequest(BaseModel):
    failed_node_code: str = "CLUSTER-NAIROBI-MAIN"
    promoted_node_code: str = "CLUSTER-MACHAKOS-EDGE"
    trigger_reason: str = "Simulated node heartbeat timeout during 2,400 ops/sec stress drill"
    organization_id: str = "SYSTEM_CORE_ORG"

@router.get("/cluster-health", response_model=List[Dict])
def get_cluster_health():
    return ha_failover_engine.get_cluster_nodes_health()

@router.post("/execute-failover", status_code=status.HTTP_200_OK)
def execute_failover(req: ExecuteFailoverRequest):
    try:
        return ha_failover_engine.evaluate_cluster_health_and_execute_failover(
            req.failed_node_code, req.promoted_node_code, req.trigger_reason, req.organization_id
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
