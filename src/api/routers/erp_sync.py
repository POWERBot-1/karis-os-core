from typing import Dict
from fastapi import APIRouter, status
from pydantic import BaseModel
from src.integrations.erp_tax_sync import erp_notification_engine

router = APIRouter(prefix="/api/v1/integrations", tags=["Enterprise ERP Sync & Notification Template Engine (Section 36.5 & 43.2)"])

class ErpSyncRequest(BaseModel):
    organization_id: str = "ORG-KARIS-RETAIL"
    target_system: str = "SAP_S4HANA_KENYA"
    fiscal_period: str = "FY-2026-Q3"

class NotificationDispatchRequest(BaseModel):
    template_code: str = "TPL-ORDER-CONFIRMED-SMS"
    recipient_identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944"
    recipient_contact: str = "+254711000003"
    variables: Dict[str, str] = {"customer_name": "Amina Wanjiku", "order_number": "ORD-SAP-101", "amount_kes": "4500.00", "qr_code": "KARIS-TRACE-QR-12C8D4F2"}
    organization_id: str = "ORG-KARIS-RETAIL"

@router.post("/erp-sync/batch", status_code=status.HTTP_201_CREATED)
def execute_erp_sync(req: ErpSyncRequest):
    return erp_notification_engine.execute_erp_accounting_batch_sync(
        req.organization_id, req.target_system, req.fiscal_period
    )

@router.post("/notifications/dispatch", status_code=status.HTTP_201_CREATED)
def dispatch_notification(req: NotificationDispatchRequest):
    return erp_notification_engine.dispatch_notification(
        req.template_code, req.recipient_identity_id, req.recipient_contact, req.variables, req.organization_id
    )
