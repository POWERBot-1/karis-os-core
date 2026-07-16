from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.core.exchange_engine import exchange_engine
from src.domain.models import AssetType

router = APIRouter(prefix="/api/v1/exchange", tags=["Multi-Asset Exchange Engine"])

class ExchangeRequest(BaseModel):
    identity_id: str
    organization_id: str
    from_asset: AssetType
    to_asset: AssetType
    from_amount: float

@router.post("/execute", status_code=status.HTTP_200_OK)
def execute_exchange(req: ExchangeRequest):
    try:
        return exchange_engine.execute_exchange(
            req.identity_id, req.organization_id, req.from_asset, req.to_asset, req.from_amount
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
