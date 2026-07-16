from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.verticals.finance_invest.service import finance_investment_service

router = APIRouter(prefix="/api/v1/finance", tags=["Investor Capital & Lending Vertical"])

class CreatePoolRequest(BaseModel):
    pool_code: str
    pool_name: str
    category: str
    target_capital_kes: float
    expected_roi_pct: float

class DepositCapitalRequest(BaseModel):
    pool_id: str
    investor_identity_id: str
    organization_id: str
    amount_kes: float

class ApplyCreditRequest(BaseModel):
    borrower_identity_id: str
    organization_id: str
    requested_amount_kes: float
    historical_spend_kes: float = 50000.0

class ApproveLoanRequest(BaseModel):
    application_id: str
    approver_identity_id: str

@router.post("/pools", status_code=status.HTTP_201_CREATED)
def create_pool(req: CreatePoolRequest):
    return finance_investment_service.create_investment_pool(
        req.pool_code, req.pool_name, req.category, req.target_capital_kes, req.expected_roi_pct
    )

@router.post("/pools/deposit", status_code=status.HTTP_201_CREATED)
def deposit_capital(req: DepositCapitalRequest):
    try:
        return finance_investment_service.deposit_capital(
            req.pool_id, req.investor_identity_id, req.organization_id, req.amount_kes
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/credit/apply", status_code=status.HTTP_201_CREATED)
def apply_credit(req: ApplyCreditRequest):
    return finance_investment_service.apply_for_credit(
        req.borrower_identity_id, req.organization_id, req.requested_amount_kes, req.historical_spend_kes
    )

@router.post("/credit/approve", status_code=status.HTTP_200_OK)
def approve_loan(req: ApproveLoanRequest):
    try:
        return finance_investment_service.approve_and_disburse_loan(req.application_id, req.approver_identity_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
