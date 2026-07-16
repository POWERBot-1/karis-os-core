import uuid
from typing import Callable, Dict, List
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.config import config

class DeclarativeRuleEngine:
    """
    KARIS OS™ Declarative Rule Engine & Workflow Orchestrator.
    Enforces Rule 7 (Configurable business rules) & Rule 10 (AI assists, automated configurable workflows).
    Listens to the Event Bus and executes actions when conditions are satisfied.
    """
    def __init__(self):
        self.rules: List[Dict] = []
        # Register Event Bus subscriptions
        event_bus.subscribe("PAYMENT_CONFIRMED", self._on_payment_confirmed)
        event_bus.subscribe("DELIVERY_COMPLETED", self._on_delivery_completed)

    def register_rule(self, rule_code: str, trigger_event: str, condition_fn: Callable, action_fn: Callable):
        self.rules.append({
            "rule_code": rule_code,
            "trigger_event": trigger_event,
            "condition_fn": condition_fn,
            "action_fn": action_fn
        })

    def _on_payment_confirmed(self, event: EventPayload):
        """
        Triggered when a PAYMENT_CONFIRMED event arrives from M-Pesa, Bank, or Wallet.
        Rule: Automated settlement & KRT Token Minting according to configured rules.
        """
        payload = event.payload
        order_id = payload["order_id"]
        payer_identity_id = payload["payer_identity_id"]
        amount_kes = payload["amount_kes"]
        organization_id = event.organization_id

        # 1. Look up or create Customer and Supplier Wallets for KES and KRT
        # In a full run, we extract supplier ID from order metadata or payload
        supplier_identity_id = payload.get("supplier_identity_id", "SUPPLIER_DEFAULT_ID")
        customer_kes_wallet = wallet_engine.get_wallet_by_keys(
            identity_id=payer_identity_id,
            organization_id=organization_id,
            wallet_type=WalletType.KES_WALLET,
            asset_type=AssetType.KES
        )
        supplier_kes_wallet = wallet_engine.get_wallet_by_keys(
            identity_id=supplier_identity_id,
            organization_id=organization_id,
            wallet_type=WalletType.KES_WALLET,
            asset_type=AssetType.KES
        )
        treasury_reserve_kes_wallet = wallet_engine.get_wallet_by_keys(
            identity_id="TREASURY_IDENTITY",
            organization_id=organization_id,
            wallet_type=WalletType.RESERVE_WALLET,
            asset_type=AssetType.KES
        )
        customer_krt_wallet = wallet_engine.get_wallet_by_keys(
            identity_id=payer_identity_id,
            organization_id=organization_id,
            wallet_type=WalletType.KRT_WALLET,
            asset_type=AssetType.KRT
        )
        treasury_reward_krt_wallet = wallet_engine.get_wallet_by_keys(
            identity_id="TREASURY_IDENTITY",
            organization_id=organization_id,
            wallet_type=WalletType.REWARD_POOL,
            asset_type=AssetType.KRT
        )

        # 2. Record KES Payment Settlement through Universal Ledger Engine (Rule 5 & Rule 2)
        if customer_kes_wallet and supplier_kes_wallet and amount_kes > 0:
            ledger_engine.record_transaction(
                transaction_id=str(uuid.uuid4()),
                asset_type=AssetType.KES,
                debit_wallet_id=customer_kes_wallet.wallet_id,
                credit_wallet_id=supplier_kes_wallet.wallet_id,
                amount=amount_kes,
                currency="KES",
                organization_id=organization_id,
                trigger_event_id=event.event_id,
                description=f"Payment settlement for order {order_id}"
            )

        # 3. Calculate KRT Reward based on Section 6 & Section 18 configurable reward ratio
        krt_reward_amount = round(amount_kes * config.KRT_MINT_ON_PURCHASE_RATIO, 4)
        if treasury_reward_krt_wallet and customer_krt_wallet and krt_reward_amount > 0:
            ledger_engine.record_transaction(
                transaction_id=str(uuid.uuid4()),
                asset_type=AssetType.KRT,
                debit_wallet_id=treasury_reward_krt_wallet.wallet_id,
                credit_wallet_id=customer_krt_wallet.wallet_id,
                amount=krt_reward_amount,
                currency="KRT",
                organization_id=organization_id,
                trigger_event_id=event.event_id,
                description=f"KRT Reward Grant for purchase order {order_id}"
            )

            # Emit TOKEN_MINTED event (Rule 6)
            token_event = EventPayload(
                event_type="TOKEN_MINTED",
                event_category=EventCategory.CURRENCY,
                actor_identity_id="TREASURY_ENGINE",
                organization_id=organization_id,
                correlation_id=event.correlation_id,
                source_module="RULE_ENGINE",
                payload={
                    "token_operation_id": str(uuid.uuid4()),
                    "treasury_reserve_id": treasury_reward_krt_wallet.wallet_id,
                    "target_wallet_id": customer_krt_wallet.wallet_id,
                    "recipient_identity_id": payer_identity_id,
                    "trigger_reason": "PURCHASE_COMPLETED",
                    "amount": krt_reward_amount,
                    "audit_hash": ledger_engine.last_hash
                }
            )
            event_bus.publish(token_event)

    def _on_delivery_completed(self, event: EventPayload):
        """
        Triggered when a DELIVERY_COMPLETED event arrives from the Rider / Logistics Engine.
        Rule 4: No Delivery Confirmation -> No Rider Payment.
        Now that delivery is confirmed, automatically settle rider payout from escrow/operations.
        """
        payload = event.payload
        delivery_id = payload["delivery_id"]
        rider_identity_id = payload["rider_identity_id"]
        delivery_fee_kes = payload["delivery_fee_kes"]
        organization_id = event.organization_id

        rider_kes_wallet = wallet_engine.get_wallet_by_keys(
            identity_id=rider_identity_id,
            organization_id=organization_id,
            wallet_type=WalletType.KES_WALLET,
            asset_type=AssetType.KES
        )
        operations_kes_wallet = wallet_engine.get_wallet_by_keys(
            identity_id="OPERATIONS_IDENTITY",
            organization_id=organization_id,
            wallet_type=WalletType.RESERVE_WALLET,
            asset_type=AssetType.KES
        )

        if rider_kes_wallet and operations_kes_wallet and delivery_fee_kes > 0:
            ledger_engine.record_transaction(
                transaction_id=str(uuid.uuid4()),
                asset_type=AssetType.KES,
                debit_wallet_id=operations_kes_wallet.wallet_id,
                credit_wallet_id=rider_kes_wallet.wallet_id,
                amount=delivery_fee_kes,
                currency="KES",
                organization_id=organization_id,
                trigger_event_id=event.event_id,
                description=f"Rider payout settlement for delivery {delivery_id}"
            )

# Global Singleton for rule evaluation
rule_engine = DeclarativeRuleEngine()
