from fastapi import APIRouter, status
from pydantic import BaseModel
from src.ai.supply_chain_bottlenecks import supply_chain_bottleneck_engine

router = APIRouter(prefix="/api/v1/analytics/ai", tags=["AI Supply Chain Bottlenecks & Dynamic Route Bypass (Section 27.4 & 13.4)"])

class BottleneckAnalyzeRequest(BaseModel):
    corridor_code: str = "CORRIDOR-MACHAKOS-NAIROBI-A104"
    active_transit_delay_hours: float = 8.5
    backlogged_crates_count: int = 650
    organization_id: str = "ORG-KARIS-FARM"

@router.post("/supply-chain-bottleneck", status_code=status.HTTP_201_CREATED)
def analyze_bottleneck(req: BottleneckAnalyzeRequest):
    return supply_chain_bottleneck_engine.analyze_network_supply_chain_bottlenecks(
        req.corridor_code, req.active_transit_delay_hours, req.backlogged_crates_count, req.organization_id
    )
