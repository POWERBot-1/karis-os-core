from fastapi import APIRouter
from src.db.cqrs_projections import cqrs_projections_engine

router = APIRouter(prefix="/api/v1/cqrs", tags=["CQRS Event-Driven Read Model Projections (Section 37.3)"])

@router.get("/dashboard")
def get_cqrs_projections_dashboard():
    """Returns real-time CQRS analytical read model projections decoupled from write transactions."""
    return cqrs_projections_engine.get_projections_dashboard()
