import uuid
from typing import Dict, List, Optional
from src.domain.models import EventCategory, EventPayload, OrderItemModel, OrderModel, RetailPosSessionModel
from src.core.event_bus import event_bus
from src.core.exchange_engine import exchange_engine
from src.domain.models import AssetType

class RetailPosService:
    """
    KARIS OS™ Omnichannel POS & Supermarket Retail Service.
    Enforces Section 20 (Omnichannel POS Engine) & Section 30 (Supermarket & Retail Vertical).
    Supports multi-branch POS sessions, barcode scans, and mixed KES+KRT payments.
    """
    def __init__(self):
        self.stores: Dict[str, Dict] = {}
        self.sessions: Dict[str, RetailPosSessionModel] = {}

    def register_store_and_terminal(
        self,
        organization_id: str,
        store_name: str,
        terminal_code: str,
        branch_type: str = "SUPERMARKET"
    ) -> Dict:
        store_id = str(uuid.uuid4())
        store = {
            "store_id": store_id,
            "organization_id": organization_id,
            "store_name": store_name,
            "terminal_code": terminal_code,
            "branch_type": branch_type
        }
        self.stores[store_id] = store
        return store

    def open_pos_session(
        self,
        terminal_code: str,
        cashier_identity_id: str,
        opening_cash_kes: float = 10000.0
    ) -> RetailPosSessionModel:
        session = RetailPosSessionModel(
            session_id=str(uuid.uuid4()),
            terminal_code=terminal_code,
            cashier_identity_id=cashier_identity_id,
            opening_cash_kes=opening_cash_kes,
            status="OPEN"
        )
        self.sessions[session.session_id] = session
        return session

    def process_pos_checkout(
        self,
        session_id: str,
        store_id: str,
        customer_identity_id: str,
        supplier_identity_id: str,
        items: List[OrderItemModel],
        payment_method: str = "MIXED_PAYMENT",
        krt_discount_used: float = 0.0
    ) -> Dict:
        if session_id not in self.sessions:
            raise KeyError(f"POS Session ID {session_id} not found.")

        store = self.stores.get(store_id, {"organization_id": "ORG_RETAIL_DEFAULT"})
        total_price_kes = sum(it.total_price for it in items)

        # If KRT discount used, execute token exchange / redemption
        krt_discount_kes_value = 0.0
        if krt_discount_used > 0:
            exch_res = exchange_engine.execute_exchange(
                identity_id=customer_identity_id,
                organization_id=store["organization_id"],
                from_asset=AssetType.KRT,
                to_asset=AssetType.KES,
                from_amount=krt_discount_used
            )
            krt_discount_kes_value = exch_res["to_amount"]

        final_fiat_due_kes = max(total_price_kes - krt_discount_kes_value, 0.0)

        order_id = str(uuid.uuid4())
        
        # Emit POS_CHECKOUT_COMPLETED event
        pos_ev = EventPayload(
            event_type="POS_CHECKOUT_COMPLETED",
            event_category=EventCategory.COMMERCE,
            actor_identity_id=customer_identity_id,
            organization_id=store["organization_id"],
            correlation_id=order_id,
            source_module="OMNICHANNEL_POS_ENGINE",
            payload={
                "session_id": session_id,
                "terminal_code": self.sessions[session_id].terminal_code,
                "store_id": store_id,
                "order_id": order_id,
                "total_kes_amount": total_price_kes,
                "krt_discount_kes_value": krt_discount_kes_value,
                "final_fiat_paid_kes": final_fiat_due_kes,
                "payment_method": payment_method
            }
        )
        event_bus.publish(pos_ev)

        # Emit PAYMENT_CONFIRMED -> Triggering Universal Ledger & Rule Engine (Rule 2 & Rule 6)
        pay_ev = EventPayload(
            event_type="PAYMENT_CONFIRMED",
            event_category=EventCategory.PAYMENT,
            actor_identity_id=customer_identity_id,
            organization_id=store["organization_id"],
            correlation_id=order_id,
            source_module="PAYMENT_ENGINE",
            payload={
                "payment_id": str(uuid.uuid4()),
                "order_id": order_id,
                "payer_identity_id": customer_identity_id,
                "supplier_identity_id": supplier_identity_id,
                "payment_method": payment_method,
                "external_reference": f"POS-REF-{order_id[:8].upper()}",
                "amount_kes": final_fiat_due_kes,
                "status": "PAYMENT_CONFIRMED"
            }
        )
        event_bus.publish(pay_ev)

        return {
            "status": "SUCCESS",
            "order_id": order_id,
            "total_price_kes": total_price_kes,
            "krt_discount_used": krt_discount_used,
            "fiat_paid_kes": final_fiat_due_kes,
            "receipt_barcode": f"POS-RCP-{order_id[:8].upper()}"
        }

retail_pos_service = RetailPosService()
