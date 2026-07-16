import uuid
from datetime import datetime, timezone
from typing import Dict
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine

class EscrowAndDisputeClearingEngine:
    """
    KARIS OS™ Unified Cross-Vertical Enterprise Clearing House & Escrow Dispute Engine (Section 31.1 & 11.2).
    Holds funds in secure escrow during high-value checkouts (`KES 250k machinery order`),
    and resolves produce quality/delivery disputes by executing atomic double-entry splits (`Rule 2, 5 & 9`).
    """
    def __init__(self):
        self.escrows: Dict[str, Dict] = {}
        self.disputes: Dict[str, Dict] = {}

    def hold_funds_in_escrow(
        self,
        order_id: str,
        buyer_identity_id: str,
        seller_identity_id: str,
        amount_kes: float,
        organization_id: str = "ORG-KARIS-FARM"
    ) -> Dict:
        if amount_kes <= 0:
            raise ValueError("Escrow amount must be strictly positive.")

        escrow_id = f"ESC-HOLD-{uuid.uuid4().hex[:8].upper()}"
        escrow_code = f"ESCROW-2026-{uuid.uuid4().hex[:6].upper()}"
        now = datetime.now(timezone.utc)

        # Ensure buyer and Operations/Escrow wallets exist
        buyer_kes = wallet_engine.get_wallet_by_keys(buyer_identity_id, organization_id, WalletType.KES_WALLET, AssetType.KES)
        if not buyer_kes:
            buyer_kes = wallet_engine.create_wallet(buyer_identity_id, organization_id, WalletType.KES_WALLET, AssetType.KES, amount_kes)
        
        escrow_kes = wallet_engine.get_wallet_by_keys("OPERATIONS_IDENTITY", organization_id, WalletType.RESERVE_WALLET, AssetType.KES)
        if not escrow_kes:
            escrow_kes = wallet_engine.create_wallet("OPERATIONS_IDENTITY", organization_id, WalletType.RESERVE_WALLET, AssetType.KES, 100_000.0)

        tx_id = str(uuid.uuid4())
        ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KES,
            debit_wallet_id=buyer_kes.wallet_id,
            credit_wallet_id=escrow_kes.wallet_id,
            amount=amount_kes,
            currency="KES",
            organization_id=organization_id,
            trigger_event_id=tx_id,
            description=f"Escrow Hold ({escrow_code}) for order {order_id}"
        )

        record = {
            "escrow_id": escrow_id,
            "escrow_code": escrow_code,
            "organization_id": organization_id,
            "order_id": order_id,
            "buyer_identity_id": buyer_identity_id,
            "seller_identity_id": seller_identity_id,
            "escrowed_amount_kes": amount_kes,
            "escrow_wallet_id": escrow_kes.wallet_id,
            "status": "HELD_IN_ESCROW",
            "created_at": now.isoformat()
        }
        self.escrows[escrow_id] = record
        return record

    def raise_and_resolve_dispute(
        self,
        escrow_id: str,
        dispute_reason: str = "PRODUCE_QUALITY_CLAIM",
        dispute_summary: str = "Received 500 KG Avocados, but 150 KG were bruised",
        seller_payout_pct: float = 60.0,
        buyer_refund_pct: float = 40.0,
        resolver_identity_id: str = "ADMIN-DISPUTE-01"
    ) -> Dict:
        """Resolves dispute via partial refund/release splits across double-entry transfers (`Rule 2, 5 & 9`)."""
        if escrow_id not in self.escrows:
            raise KeyError(f"Escrow ID {escrow_id} not found.")

        esc = self.escrows[escrow_id]
        if esc["status"] != "HELD_IN_ESCROW":
            raise ValueError(f"Escrow status is {esc['status']}, cannot resolve dispute.")

        gross = esc["escrowed_amount_kes"]
        seller_kes_amt = round(gross * (seller_payout_pct / 100.0), 2)
        buyer_kes_amt = round(gross * (buyer_refund_pct / 100.0), 2)
        org = esc["organization_id"]

        escrow_kes = wallet_engine.get_wallet(esc["escrow_wallet_id"])
        seller_kes = wallet_engine.get_wallet_by_keys(esc["seller_identity_id"], org, WalletType.KES_WALLET, AssetType.KES)
        if not seller_kes:
            seller_kes = wallet_engine.create_wallet(esc["seller_identity_id"], org, WalletType.KES_WALLET, AssetType.KES, 0.0)
        buyer_kes = wallet_engine.get_wallet_by_keys(esc["buyer_identity_id"], org, WalletType.KES_WALLET, AssetType.KES)

        # Leg A: Release to Seller
        if seller_kes_amt > 0 and escrow_kes and seller_kes:
            ledger_engine.record_transaction(
                transaction_id=str(uuid.uuid4()),
                asset_type=AssetType.KES,
                debit_wallet_id=escrow_kes.wallet_id,
                credit_wallet_id=seller_kes.wallet_id,
                amount=seller_kes_amt,
                currency="KES",
                organization_id=org,
                trigger_event_id=escrow_id,
                description=f"Dispute Split Resolution: {seller_payout_pct}% released to seller"
            )

        # Leg B: Refund to Buyer
        if buyer_kes_amt > 0 and escrow_kes and buyer_kes:
            ledger_engine.record_transaction(
                transaction_id=str(uuid.uuid4()),
                asset_type=AssetType.KES,
                debit_wallet_id=escrow_kes.wallet_id,
                credit_wallet_id=buyer_kes.wallet_id,
                amount=buyer_kes_amt,
                currency="KES",
                organization_id=org,
                trigger_event_id=escrow_id,
                description=f"Dispute Split Resolution: {buyer_refund_pct}% refunded to buyer"
            )

        esc["status"] = "SPLIT_RESOLVED_DISPUTE"
        disp_id = f"DISPUTE-{uuid.uuid4().hex[:8].upper()}"
        disp_code = f"DISP-AGRI-2026-{uuid.uuid4().hex[:6].upper()}"

        dispute_case = {
            "dispute_id": disp_id,
            "dispute_code": disp_code,
            "escrow_id": escrow_id,
            "order_id": esc["order_id"],
            "raised_by_identity_id": esc["buyer_identity_id"],
            "dispute_reason": dispute_reason,
            "dispute_summary": dispute_summary,
            "status": "RESOLVED_SPLIT_REFUND",
            "seller_payout_kes": seller_kes_amt,
            "buyer_refund_kes": buyer_kes_amt,
            "resolved_by_identity_id": resolver_identity_id,
            "resolved_at": datetime.now(timezone.utc).isoformat()
        }
        self.disputes[disp_id] = dispute_case

        ev = EventPayload(
            event_type="ESCROW_DISPUTE_RESOLVED",
            event_category=EventCategory.GOVERNANCE,
            actor_identity_id=resolver_identity_id,
            organization_id=org,
            correlation_id=disp_id,
            source_module="ESCROW_DISPUTE_CLEARING_ENGINE",
            payload={
                "dispute_id": disp_id,
                "dispute_code": disp_code,
                "escrow_id": escrow_id,
                "seller_payout_kes": seller_kes_amt,
                "buyer_refund_kes": buyer_kes_amt,
                "status": "RESOLVED_SPLIT_REFUND"
            }
        )
        event_bus.publish(ev)
        return dispute_case

escrow_dispute_engine = EscrowAndDisputeClearingEngine()
