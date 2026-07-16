from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.observability.disaster_recovery import dr_engine
from src.core.event_replay import event_replay_engine

router = APIRouter(prefix="/api/v1/recovery", tags=["Disaster Recovery (PITR) & Event Replay (Section 37.5 & 44.4)"])

class SnapshotRequest(BaseModel):
    organization_id: str = "ORG-KARIS-RETAIL"
    snapshot_type: str = "POINT_IN_TIME_PITR"
    creator_identity_id: str = "SYSTEM_DR_ENGINE"

class ReplayRequest(BaseModel):
    target_timestamp: Optional[str] = None
    organization_id: str = "ORG-KARIS-RETAIL"

@router.post("/snapshot", status_code=status.HTTP_201_CREATED)
def create_pitr_snapshot(req: SnapshotRequest):
    return dr_engine.create_point_in_time_snapshot(req.organization_id, req.snapshot_type, req.creator_identity_id)

@router.get("/snapshot/{snapshot_id}/verify")
def verify_snapshot(snapshot_id: str):
    try:
        return dr_engine.verify_snapshot_checksum(snapshot_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/replay", status_code=status.HTTP_200_OK)
def trigger_event_sourcing_replay(req: ReplayRequest):
    """Replays domain events to reconstruct exact multi-asset wallet balances (`Rule 1 & Section 37.5`)."""
    return event_replay_engine.reconstruct_system_state_from_events(req.target_timestamp, req.organization_id)
