import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from src.domain.models import HostedPaymentLinkModel, PaymentLinkTransactionModel, EventPayload, AssetType, WalletType, EventCategory
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.core.rule_engine import rule_engine
from src.verticals.financial_services.service import financial_engine

class PaymentLinkCheckoutEngine:
    """
    KARIS OS™ PalPlus & Hosted Payment Link Checkout Engine (`Section 51 / Section 34.5`).
    Integrates our active temporary payment link: `https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f`.
    Enables smallholder farmers (`KARIS FARM`), POS checkouts, prediction entries (`POWER BOT X`), and solar
    PAYG installments (`KARIS ENERGY`) to generate universal hosted checkout URLs and settle automatically via webhooks.
    """
    def __init__(self):
        self.active_links: Dict[str, HostedPaymentLinkModel] = {}
        self.transactions: Dict[str, PaymentLinkTransactionModel] = {}
        self._seed_default_palplus_link()

    def _seed_default_palplus_link(self):
        default_link = HostedPaymentLinkModel(
            payment_link_id="6e8de0bc-1284-4bba-a5de-f886665bf18f",
            provider="PALPLUS",
            external_link_url="https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f",
            merchant_organization_id="ORG-KARIS-RETAIL",
            created_by_identity_id="7f8013a9-310c-4f16-9031-295274a26944",
            amount_kes=0.0,
            status="ACTIVE_TEMPORARY_LINK"
        )
        self.active_links[default_link.payment_link_id] = default_link

    def get_or_register_payment_link(
        self,
        payment_link_id: str = "6e8de0bc-1284-4bba-a5de-f886665bf18f",
        external_link_url: str = "https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f",
        merchant_org_id: str = "ORG-KARIS-RETAIL",
        amount_kes: float = 0.0,
        target_order_id: Optional[str] = None
    ) -> HostedPaymentLinkModel:
        if payment_link_id in self.active_links:
            link = self.active_links[payment_link_id]
            if target_order_id:
                link.target_order_id = target_order_id
            if amount_kes > 0:
                link.amount_kes = amount_kes
            return link

        link = HostedPaymentLinkModel(
            payment_link_id=payment_link_id,
            provider="PALPLUS",
            external_link_url=external_link_url,
            merchant_organization_id=merchant_org_id,
            created_by_identity_id="SYSTEM-CHECKOUT",
            target_order_id=target_order_id,
            amount_kes=amount_kes,
            status="ACTIVE_TEMPORARY_LINK"
        )
        self.active_links[link.payment_link_id] = link
        return link

    def generate_checkout_package(
        self,
        order_id: str,
        amount_kes: float,
        payer_identity_id: str,
        description: str = "Universal Checkout via PalPlus Temporary Payment Link"
    ) -> Dict[str, Any]:
        """
        Generates a checkout package linking any order, prediction entry, or solar PAYG fee directly
        to our active PalPlus temporary payment link (`https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f`).
        """
        link = self.get_or_register_payment_link(
            payment_link_id="6e8de0bc-1284-4bba-a5de-f886665bf18f",
            target_order_id=order_id,
            amount_kes=amount_kes
        )

        return {
            "checkout_id": f"CHK-{uuid.uuid4().hex[:8].upper()}",
            "payment_link_id": link.payment_link_id,
            "provider": link.provider,
            "payment_link_url": link.external_link_url,
            "target_order_id": order_id,
            "amount_kes": amount_kes,
            "payer_identity_id": payer_identity_id,
            "description": description,
            "qr_code_payload": f"{link.external_link_url}?order={order_id}&amount={amount_kes}",
            "instructions": f"Click the secure PalPlus temporary link above or scan QR code via mobile browser / WhatsApp to complete your KES {amount_kes:,.2f} payment."
        }

    def process_palplus_webhook(
        self,
        payment_link_id: str = "6e8de0bc-1284-4bba-a5de-f886665bf18f",
        payer_identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944",
        amount_kes: float = 2500.0,
        external_receipt_number: str = "PALPLUS-RC-88192",
        organization_id: str = "ORG-KARIS-RETAIL",
        target_order_id: str = "ORDER-PAL-001"
    ) -> Dict[str, Any]:
        """
        Reconciles incoming webhooks when a customer pays via `https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f`.
        Executes double-entry ledger reconciliation (`Rule 2 & Rule 9`), triggers KRT loyalty minting (`Rule 6 & Rule 7`),
        and marks the linked order or PAYG installment as SETTLED.
        """
        if amount_kes <= 0:
            raise ValueError("PalPlus webhook amount must be strictly greater than 0.")

        link = self.get_or_register_payment_link(payment_link_id=payment_link_id, merchant_org_id=organization_id, target_order_id=target_order_id)

        # Execute double-entry reconciliation via financial engine
        c2b_res = financial_engine.process_mpesa_c2b_callback(
            trans_id=external_receipt_number,
            amount_kes=amount_kes,
            bill_ref_number=target_order_id,
            msisdn="PALPLUS-HOSTED-LINK",
            organization_id=organization_id,
            payer_identity_id=payer_identity_id
        )

        tx = PaymentLinkTransactionModel(
            payment_link_id=link.payment_link_id,
            payer_identity_id=payer_identity_id,
            amount_kes=amount_kes,
            payment_method="PALPLUS_MPESA_EXPRESS",
            external_receipt_number=external_receipt_number,
            reconciled_ledger_hash=ledger_engine.last_hash
        )
        self.transactions[tx.transaction_id] = tx

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="PAYMENT_LINK_CHECKOUT_COMPLETED",
            event_category=EventCategory.PAYMENT,
            actor_identity_id=payer_identity_id,
            organization_id=organization_id,
            correlation_id=external_receipt_number,
            source_module="PALPLUS_PAYMENT_LINK_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "payment_link_id": link.payment_link_id,
                "external_link_url": link.external_link_url,
                "payer_identity_id": payer_identity_id,
                "amount_kes": amount_kes,
                "payment_method": "PALPLUS_MPESA_EXPRESS",
                "external_receipt_number": external_receipt_number,
                "target_order_id": target_order_id
            }
        )
        event_bus.publish(ev)

        return {
            "status": "SUCCESS",
            "transaction_id": tx.transaction_id,
            "payment_link_id": link.payment_link_id,
            "external_link_url": link.external_link_url,
            "reconciled_amount_kes": amount_kes,
            "external_receipt_number": external_receipt_number,
            "target_order_id": target_order_id,
            "loyalty_krt_earned": c2b_res.get("loyalty_krt_earned", round(amount_kes * 0.05, 4)),
            "audit_hash": ledger_engine.last_hash,
            "message": f"PalPlus checkout verified via {link.external_link_url}. Double-entry ledger reconciled under Rule 2 & Rule 9!"
        }

payment_link_engine = PaymentLinkCheckoutEngine()
