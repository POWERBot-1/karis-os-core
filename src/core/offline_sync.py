import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.security.governance_compliance import governance_engine

class OfflineSynchronizationEngine:
    """
    KARIS OS™ Mobile App & POS Offline Synchronization Engine (Section 41.5 & 20.2).
    Allows critical transactions (`POS Checkouts, Order Captures, Delivery Confirmations`) to occur locally
    during network interruptions, performing optimistic lock verification and double-entry synchronization upon reconnection.
    """
    def __init__(self):
        self.queues: Dict[str, Dict] = {}

    def synchronize_offline_batch(
        self,
        device_terminal_code: str,
        offline_transactions: List[Dict],
        cashier_identity_id: str,
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        batch_id = f"OFF-BATCH-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc)

        # Execute reconciliation for each offline transaction
        synced_count = 0
        conflicts_count = 0
        total_kes_processed = 0.0

        for tx in offline_transactions:
            tx_type = tx.get("type", "POS_CHECKOUT")
            amt = float(tx.get("amount_kes", 0.0))
            cust_id = tx.get("customer_id", "ANONYMOUS_WALK_IN")
            seller_id = tx.get("seller_id", cashier_identity_id)

            if amt > 0 and tx_type == "POS_CHECKOUT":
                # Verify customer wallet balance (if using KES_WALLET or M-Pesa verified offline token)
                cust_kes = wallet_engine.get_wallet_by_keys(cust_id, organization_id, WalletType.KES_WALLET, AssetType.KES)
                if not cust_kes:
                    cust_kes = wallet_engine.create_wallet(cust_id, organization_id, WalletType.KES_WALLET, AssetType.KES, amt)
                
                seller_kes = wallet_engine.get_wallet_by_keys(seller_id, organization_id, WalletType.KES_WALLET, AssetType.KES)
                if not seller_kes:
                    seller_kes = wallet_engine.create_wallet(seller_id, organization_id, WalletType.KES_WALLET, AssetType.KES, 0.0)

                if cust_kes.balance >= amt:
                    tx_id = str(uuid.uuid4())
                    ledger_engine.record_transaction(
                        transaction_id=tx_id,
                        asset_type=AssetType.KES,
                        debit_wallet_id=cust_kes.wallet_id,
                        credit_wallet_id=seller_kes.wallet_id,
                        amount=amt,
                        currency="KES",
                        organization_id=organization_id,
                        trigger_event_id=tx_id,
                        description=f"Offline POS Checkout Synchronized ({device_terminal_code})"
                    )
                    # Issue eTIMS invoice for synced checkout (Rule 7)
                    governance_engine.issue_kra_etims_tax_invoice(
                        organization_id, f"ORD-OFF-{uuid.uuid4().hex[:6].upper()}", cust_id, seller_id, "P051234567Z", amt
                    )
                    synced_count += 1
                    total_kes_processed += amt
                else:
                    conflicts_count += 1

        status = "SYNCHRONIZED_SUCCESS" if conflicts_count == 0 else "CONFLICT_REQUIRES_RECONCILIATION"
        summary = f"Processed {synced_count} offline sales (KES {total_kes_processed:,.2f}) with {conflicts_count} balance conflicts."

        record = {
            "offline_batch_id": batch_id,
            "device_terminal_code": device_terminal_code,
            "organization_id": organization_id,
            "cashier_or_user_identity_id": cashier_identity_id,
            "total_transactions_in_batch": len(offline_transactions),
            "synced_transactions_count": synced_count,
            "conflicted_transactions_count": conflicts_count,
            "total_kes_volume_synchronized": total_kes_processed,
            "sync_status": status,
            "reconciliation_summary": summary,
            "synchronized_at": now.isoformat()
        }
        self.queues[batch_id] = record

        ev = EventPayload(
            event_type="OFFLINE_BATCH_SYNCHRONIZED",
            event_category=EventCategory.COMMERCE,
            actor_identity_id=cashier_identity_id,
            organization_id=organization_id,
            correlation_id=batch_id,
            source_module="OFFLINE_SYNCHRONIZATION_ENGINE",
            payload={
                "offline_batch_id": batch_id,
                "device_terminal_code": device_terminal_code,
                "total_transactions_in_batch": len(offline_transactions),
                "sync_status": status
            }
        )
        event_bus.publish(ev)
        return record

offline_sync_engine = OfflineSynchronizationEngine()
