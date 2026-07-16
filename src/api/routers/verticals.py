from typing import Dict, List
from fastapi import APIRouter, status
from pydantic import BaseModel
from src.core.vertical_registry import vertical_registry

router = APIRouter(prefix="/api/v1/verticals", tags=["Vertical Registration Framework (Section 35)"])

class RegisterVerticalRequest(BaseModel):
    vertical_code: str
    vertical_name: str
    description: str
    required_roles: List[str]
    default_currency: str = "KES"

@router.get("/registered", response_model=List[Dict])
def get_registered_verticals():
    return list(vertical_registry.registered_verticals.values())

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_vertical(req: RegisterVerticalRequest):
    return vertical_registry.register_new_vertical(
        req.vertical_code, req.vertical_name, req.description, req.required_roles, req.default_currency
    )
