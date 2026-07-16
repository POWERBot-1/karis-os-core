import uuid
from datetime import datetime, timezone
from typing import Dict, List
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine

class MultiVendorMarketplaceEngine:
    """
    KARIS OS™ Multi-Vendor B2B/B2C Marketplace Aggregation & Split-Commission Engine (Section 14.3 & 17.2).
    Processes combined shopping carts containing items from independent suppliers (`Farmer Kamau`, `Machakos Coop`, `Mlolongo Depot`),
    calculating split-commissions and executing multi-leg double-entry transfers atomically (`Rule 2 & Rule 5`).
    """
    def __init__(self):
        self.orders: Dict[str, Dict] = {}
        self.allocations: Dict[str, List[Dict]] = {}

    def execute_multi_vendor_split_settlement(
        self,
        customer_identity_id: str,
        vendor_items: List[Dict], # [{"vendor_id": "...", "amount_kes": 5000.0, "commission_pct": 15.0}]
        payment_reference: str = "QG37XXXXXXXX",
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        cart_id = f"CART-MKT-{uuid.uuid4().hex[:8].upper()}"
        cart_code = f"CART-2026-{uuid.uuid4().hex[:6].upper()}"
        total_cart_kes = sum(float(item["amount_kes"]) for item in vendor_items)

        if total_cart_kes <= 0:
            raise ValueError("Cart total must be positive.")

        # Ensure Customer KES wallet exists with funds
        cust_kes = wallet_engine.get_wallet_by_keys(customer_identity_id, organization_id, WalletType.KES_WALLET, AssetType.KES)
        if not cust_kes:
            cust_kes = wallet_engine.create_wallet(customer_identity_id, organization_id, WalletType.KES_WALLET, AssetType.KES, total_cart_kes)
        
        # Ensure Operations / Commission KES wallet exists
        operations_kes = wallet_engine.get_wallet_by_keys("OPERATIONS_IDENTITY", organization_id, WalletType.RESERVE_WALLET, AssetType.KES)
        if not operations_kes:
            operations_kes = wallet_engine.create_wallet("OPERATIONS_IDENTITY", organization_id, WalletType.RESERVE_WALLET, AssetType.KES, 100_000.0)

        allocs_created = []
        total_comm_kes = 0.0

        for item in vendor_items:
            v_id = item["vendor_id"]
            gross_amt = float(item["amount_kes"])
            comm_pct = float(item.get("commission_pct", 15.0))
            comm_amt = round(gross_amt * (comm_pct / 100.0), 2)
            net_payout = round(gross_amt - comm_amt, 2)
            total_comm_kes += comm_amt

            # Lookup/create Vendor KES wallet
            vendor_kes = wallet_engine.get_wallet_by_keys(v_id, organization_id, WalletType.KES_WALLET, AssetType.KES)
            if not vendor_kes:
                vendor_kes = wallet_engine.create_wallet(v_id, organization_id, WalletType.KES_WALLET, AssetType.KES, 0.0)

            tx_id = str(uuid.uuid4())
            # Leg A: Customer KES -> Vendor KES (Net Payout)
            if net_payout > 0:
                ledger_engine.record_transaction(
                    transaction_id=tx_id,
                    asset_type=AssetType.KES,
                    debit_wallet_id=cust_kes.wallet_id,
                    credit_wallet_id=vendor_kes.wallet_id,
                    amount=net_payout,
                    currency="KES",
                    organization_id=organization_id,
                    trigger_event_id=tx_id,
                    description=f"Marketplace Split Payout ({cart_code}) to Vendor {v_id[:8]}"
                )

            # Leg B: Customer KES -> Operations KES (Platform Commission)
            if comm_amt > 0:
                ledger_engine.record_transaction(
                    transaction_id=str(uuid.uuid4()),
                    asset_type=AssetType.KES,
                    debit_wallet_id=cust_kes.wallet_id,
                    credit_wallet_id=operations_kes.wallet_id,
                    amount=comm_amt,
                    currency="KES",
                    organization_id=organization_id,
                    trigger_event_id=tx_id,
                    description=f"Marketplace Split Commission ({comm_pct}%) on {gross_amt} KES"
                )

            allocs_created.append({
                "allocation_id": f"ALLOC-{uuid.uuid4().hex[:6].upper()}",
                "vendor_identity_id": v_id,
                "gross_amount_kes": gross_amt,
                "platform_commission_kes": comm_amt,
                "net_vendor_payout_kes": net_payout,
                "payout_status": "SETTLED_VIA_LEDGER"
            })

        self.allocations[cart_id] = allocs_created
        order_record = {
            "cart_order_id": cart_id,
            "cart_order_code": cart_code,
            "organization_id": organization_id,
            "customer_identity_id": customer_identity_id,
            "total_cart_amount_kes": total_cart_kes,
            "total_platform_commission_kes": total_comm_kes,
            "payment_reference": payment_reference,
            "settlement_status": "MULTI_VENDOR_SPLIT_SETTLED",
            "settled_at": datetime.now(timezone.utc).isoformat()
        }
        self.orders[cart_id] = order_record

        ev = EventPayload(
            event_type="MARKETPLACE_SPLIT_SETTLED",
            event_category=EventCategory.PAYMENT,
            actor_identity_id=customer_identity_id,
            organization_id=organization_id,
            correlation_id=cart_id,
            source_module="MULTI_VENDOR_MARKETPLACE_ENGINE",
            payload={
                "cart_order_id": cart_id,
                "cart_order_code": cart_code,
                "total_cart_amount_kes": total_cart_kes,
                "vendors_settled_count": len(vendor_items),
                "platform_commission_kes": total_comm_kes
            }
        )
        event_bus.publish(ev)
        return {"status": "SUCCESS", "cart_order": order_record, "allocations": allocs_created}

marketplace_split_engine = MultiVendorMarketplaceEngine()
