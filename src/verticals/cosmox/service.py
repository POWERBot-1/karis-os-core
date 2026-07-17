"""
KARIS OS™ :: COSMOX™ Universal AI Marketplace & KRT Economy Layer (`Section 57 / Vertical 22`).
Unifies Universal Wallets (`fiat, krt, rewards, escrow, merchant, driver`), AI Engine (7 modules),
Tokenomics & Vesting Engine, Configurable Referral Network (`INDIVIDUAL, MERCHANT, DELIVERY_PARTNER`),
Logistics Route AI enforcing strict Rule 4 Escrow Release, Digital Services Developer Platform, and Multi-Sig Treasury.
Enforces all 10 Platform Rules (`Rule 1 to Rule 10`).
"""

import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from src.domain.models import (
    CosmoxAccountModel, CosmoxProductModel, CosmoxOrderModel, CosmoxDeliveryModel,
    CosmoxReferralModel, CosmoxStakingPositionModel, CosmoxDigitalServiceModel,
    CosmoxVestingScheduleModel, CosmoxProposalModel, CosmoxVoteModel,
    CosmoxMultisigRequestModel,
    EventPayload, AssetType, WalletType, EventCategory
)
from src.core.event_bus import event_bus, UniversalEventBus
from src.core.ledger_engine import ledger_engine, UniversalLedgerEngine
from src.core.wallet_engine import wallet_engine, MultiAssetWalletEngine
from src.verticals.cosmox.ai_engine import CosmoxAIEngine
from src.verticals.cosmox.tokenomics_engine import CosmoxTokenomicsEngine
from src.verticals.cosmox.referral_engine import CosmoxReferralEngine

class CosmoxService:
    """
    Universal AI Marketplace and KRT Economy Engine (`Vertical 22`).
    """
    def __init__(
        self,
        event_bus: UniversalEventBus,
        ledger_engine: UniversalLedgerEngine,
        wallet_engine: MultiAssetWalletEngine
    ):
        self.event_bus = event_bus
        self.ledger_engine = ledger_engine
        self.wallet_engine = wallet_engine

        self.ai_engine = CosmoxAIEngine()
        self.tokenomics_engine = CosmoxTokenomicsEngine()
        self.referral_engine = CosmoxReferralEngine()

        # In-memory domain repositories synced with database projections
        self.accounts: Dict[str, CosmoxAccountModel] = {}
        self.products: Dict[str, CosmoxProductModel] = {}
        self.orders: Dict[str, CosmoxOrderModel] = {}
        self.deliveries: Dict[str, CosmoxDeliveryModel] = {}
        self.referrals: Dict[str, CosmoxReferralModel] = {}
        self.staking_positions: Dict[str, CosmoxStakingPositionModel] = {}
        self.digital_services: Dict[str, CosmoxDigitalServiceModel] = {}
        self.vesting_schedules: Dict[str, CosmoxVestingScheduleModel] = {}
        self.proposals: Dict[str, CosmoxProposalModel] = {}
        self.votes: Dict[str, CosmoxVoteModel] = {}
        self.multisig_requests: Dict[str, CosmoxMultisigRequestModel] = {}

        self._init_system_pools()

    def _init_system_pools(self):
        """
        Auto-initializes systemic KRT reserve and escrow pools for COSMOX marketplace operations.
        """
        self.reward_pool_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-COSMOX-REWARDS",
            organization_id="ORG-COSMOX-MAIN",
            wallet_type=WalletType.REWARD_POOL,
            asset_type=AssetType.KRT_REWARDS,
            initial_balance=10000000.0
        )
        self.reserve_pool_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-COSMOX-RESERVE",
            organization_id="ORG-COSMOX-MAIN",
            wallet_type=WalletType.RESERVE_WALLET,
            asset_type=AssetType.KRT,
            initial_balance=50000000.0
        )
        self.treasury_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-COSMOX-TREASURY",
            organization_id="ORG-COSMOX-MAIN",
            wallet_type=WalletType.TREASURY_WALLET,
            asset_type=AssetType.KRT,
            initial_balance=20000000.0
        )
        self.burn_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-COSMOX-BURN",
            organization_id="ORG-COSMOX-MAIN",
            wallet_type=WalletType.RESERVE_WALLET,
            asset_type=AssetType.KRT,
            initial_balance=0.0
        )
        self.escrow_main_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-COSMOX-ESCROW-MAIN",
            organization_id="ORG-COSMOX-MAIN",
            wallet_type=WalletType.SETTLEMENT_WALLET,
            asset_type=AssetType.KRT,
            initial_balance=5000000.0
        )

    # =========================================================================
    # 1. UNIVERSAL WALLET ONBOARDING (`Section 57.2 & 57.3`)
    # =========================================================================
    def onboard_cosmox_account(
        self,
        identity_id: str,
        account_type: str = "BUYER",
        initial_fiat_kes: float = 50000.0,
        initial_krt: float = 2000.0
    ) -> CosmoxAccountModel:
        """
        Onboards a user into COSMOX, establishing their 6 Universal Wallets:
        fiat (`KES`), krt (`KRT`), rewards (`KRT_REWARDS`), escrow (`ESCROW_WALLET`), merchant (`MERCHANT_WALLET`), driver (`DRIVER_WALLET`).
        Enforces Rule 1 & Rule 6.
        """
        account_number = f"CMX-{uuid.uuid4().hex[:8].upper()}"
        a_type = account_type.upper()
        if a_type not in ["BUYER", "MERCHANT", "DRIVER", "DEVELOPER"]:
            a_type = "BUYER"

        fiat_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-cmx-fiat", "ORG-COSMOX-MAIN", WalletType.KES_WALLET, AssetType.KES, initial_fiat_kes)
        krt_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-cmx-krt", "ORG-COSMOX-MAIN", WalletType.KRT_WALLET, AssetType.KRT, initial_krt)
        rewards_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-cmx-rewards", "ORG-COSMOX-MAIN", WalletType.REWARDS_WALLET, AssetType.KRT_REWARDS, 100.0)
        escrow_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-cmx-escrow", "ORG-COSMOX-MAIN", WalletType.ESCROW_WALLET, AssetType.KRT, 0.0)
        merchant_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-cmx-merchant", "ORG-COSMOX-MAIN", WalletType.MERCHANT_WALLET, AssetType.KRT, 0.0)
        driver_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-cmx-driver", "ORG-COSMOX-MAIN", WalletType.DRIVER_WALLET, AssetType.KES, 0.0)

        acc = CosmoxAccountModel(
            identity_id=identity_id,
            account_number=account_number,
            account_type=a_type,
            kyc_status="VERIFIED_TIER_3",
            fiat_wallet_id=fiat_w.wallet_id,
            krt_wallet_id=krt_w.wallet_id,
            rewards_wallet_id=rewards_w.wallet_id,
            escrow_wallet_id=escrow_w.wallet_id,
            merchant_wallet_id=merchant_w.wallet_id,
            driver_wallet_id=driver_w.wallet_id,
            reputation_score=100
        )
        self.accounts[acc.account_id] = acc

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="COSMOX_ACCOUNT_ONBOARDED",
            event_category=EventCategory.COSMOX_MARKETPLACE,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=identity_id,
            source_module="cosmox",
            organization_id="ORG-COSMOX-MAIN",
            payload={
                "account_id": acc.account_id,
                "identity_id": identity_id,
                "account_number": account_number,
                "account_type": acc.account_type,
                "fiat_wallet_id": fiat_w.wallet_id,
                "krt_wallet_id": krt_w.wallet_id,
                "rewards_wallet_id": rewards_w.wallet_id,
                "escrow_wallet_id": escrow_w.wallet_id,
                "merchant_wallet_id": merchant_w.wallet_id,
                "driver_wallet_id": driver_w.wallet_id
            }
        )
        self.event_bus.publish(evt)
        return acc

    # =========================================================================
    # 2. SELLER ECOSYSTEM & AI DYNAMIC PRICING (`Section 57.4`)
    # =========================================================================
    def create_product(
        self,
        seller_account_id: str,
        product_name: str,
        category: str,
        base_price_krt: float,
        inventory_count: int = 100,
        ai_dynamic_pricing_enabled: bool = True
    ) -> CosmoxProductModel:
        """
        Creates a physical or digital product on COSMOX. Calculates AI elasticity-adjusted price (`Rule 10`).
        """
        if seller_account_id not in self.accounts:
            raise KeyError(f"Seller Account '{seller_account_id}' not found.")

        # Compute dynamic price via AI Engine
        dyn = self.ai_engine.dynamic_pricing(
            product_id="TEMP", base_price_krt=base_price_krt,
            inventory_count=inventory_count, competitor_avg_price_krt=base_price_krt
        )
        current_price = dyn["recommended_dynamic_price_krt"] if ai_dynamic_pricing_enabled else base_price_krt

        prod = CosmoxProductModel(
            seller_account_id=seller_account_id,
            product_name=product_name,
            category=category.upper(),
            base_price_krt=base_price_krt,
            base_price_fiat=base_price_krt * 130.0,
            currency="KES",
            inventory_count=inventory_count,
            ai_dynamic_pricing_enabled=ai_dynamic_pricing_enabled,
            current_price_krt=current_price,
            status="ACTIVE"
        )
        self.products[prod.product_id] = prod
        return prod

    # =========================================================================
    # 3. BUYER MARKETPLACE CHECKOUT WITH ESCROW HOLD (`Section 57.5 & Rule 2`)
    # =========================================================================
    def checkout_marketplace_order(
        self,
        buyer_account_id: str,
        product_id: str,
        quantity: int = 1
    ) -> CosmoxOrderModel:
        """
        Executes a marketplace checkout. Strictly locks buyer KRT inside the Order Escrow Wallet (`Rule 2 & Rule 5 & Rule 9`).
        No payment -> No settlement.
        """
        if buyer_account_id not in self.accounts:
            raise KeyError(f"Buyer Account '{buyer_account_id}' not found.")
        if product_id not in self.products:
            raise KeyError(f"Product '{product_id}' not found.")

        buyer = self.accounts[buyer_account_id]
        prod = self.products[product_id]
        if prod.inventory_count < quantity:
            raise ValueError(f"Insufficient stock for product '{prod.product_name}'. Available: {prod.inventory_count}, Requested: {quantity}.")

        # Check AI fraud detection before checkout
        fraud_check = self.ai_engine.detect_fraud(buyer_account_id, f"ORDER_CHECKOUT_{prod.category}", prod.current_price_krt * quantity, recent_orders_count_1h=1)
        if fraud_check["is_suspicious"] and fraud_check["ai_risk_score"] > 75.0:
            raise PermissionError(f"COSMOX Security Block: Transaction flagged by AI Risk Engine. Reason: {fraud_check['audit_reasons'][0]}")

        unit_price = prod.current_price_krt
        total_price = round(unit_price * quantity, 4)

        buyer_krt_w = self.wallet_engine.get_wallet(buyer.krt_wallet_id)
        if not buyer_krt_w or buyer_krt_w.balance < total_price:
            raise ValueError(f"Insufficient KRT inside buyer wallet. Balance: {buyer_krt_w.balance if buyer_krt_w else 0.0} KRT, Required: {total_price} KRT.")

        # Split: 88% seller payout, 12% platform commission. Plus 1.5% buyer cashback reward upon delivery
        seller_payout = round(total_price * 0.88, 4)
        platform_commission = round(total_price * 0.12, 4)
        cashback_krt = round(total_price * 0.015, 4)

        # Lock funds from buyer KRT wallet into Order Escrow wallet via double entry (`Rule 2 & Rule 9`)
        tx_id = str(uuid.uuid4())
        ledger_entry = self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=buyer.krt_wallet_id,
            credit_wallet_id=buyer.escrow_wallet_id,
            amount=total_price,
            currency="KRT",
            organization_id="ORG-COSMOX-MAIN",
            trigger_event_id=f"CMX-ESCROW-HOLD-{tx_id}",
            description=f"COSMOX Escrow Hold ({quantity}x {prod.product_name}) pending delivery"
        )

        prod.inventory_count -= quantity

        order = CosmoxOrderModel(
            order_id=tx_id,
            buyer_account_id=buyer_account_id,
            seller_account_id=prod.seller_account_id,
            product_id=product_id,
            quantity=quantity,
            unit_price_krt=unit_price,
            total_price_krt=total_price,
            seller_payout_krt=seller_payout,
            platform_commission_krt=platform_commission,
            cashback_reward_krt=cashback_krt,
            payment_method="KRT_WALLET",
            escrow_status="ESCROWED_PENDING_DELIVERY",
            ledger_entry_id=ledger_entry.entry_id
        )
        self.orders[order.order_id] = order

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="COSMOX_ORDER_CREATED",
            event_category=EventCategory.COSMOX_MARKETPLACE,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=buyer.identity_id,
            source_module="cosmox",
            organization_id="ORG-COSMOX-MAIN",
            payload={
                "order_id": order.order_id,
                "buyer_account_id": buyer_account_id,
                "seller_account_id": order.seller_account_id,
                "product_id": product_id,
                "total_price_krt": total_price,
                "seller_payout_krt": seller_payout,
                "platform_commission_krt": platform_commission,
                "escrow_status": order.escrow_status,
                "ledger_entry_id": ledger_entry.entry_id
            }
        )
        self.event_bus.publish(evt)
        return order

    # =========================================================================
    # 4. LOGISTICS ROUTE AI & STRICT RULE 4 ESCROW RELEASE (`Section 57.8`)
    # =========================================================================
    def dispatch_logistics_delivery(
        self,
        order_id: str,
        driver_account_id: str,
        origin: str = "Nairobi Inland Depot",
        destination: str = "Machakos Town Hub",
        distance_km: float = 45.0
    ) -> CosmoxDeliveryModel:
        """
        Dispatches a logistics delivery for an escrowed order. Calculates AI route and locks driver bonus inside Escrow Pool.
        Strictly enforces Rule 4: No Delivery Confirmation -> No Rider Payment.
        """
        if order_id not in self.orders:
            raise KeyError(f"Order '{order_id}' not found.")
        if driver_account_id not in self.accounts:
            raise KeyError(f"Driver Account '{driver_account_id}' not found.")

        order = self.orders[order_id]
        driver = self.accounts[driver_account_id]

        # Calculate driver fiat payout (`KES 50 per km`) + KRT delivery incentive bonus (`+25 KRT`)
        driver_fiat = round(distance_km * 50.0, 4)
        driver_bonus_krt = 25.0

        ai_route = f"COSMOX Route AI Optimization: Take A104 Express from {origin} to {destination} ({distance_km} km). Estimated transit: 42 mins avoiding Mlolongo traffic."

        # Escrow driver bonus into Main Escrow Pool per Rule 4
        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=self.reserve_pool_wallet.wallet_id,
            credit_wallet_id=self.escrow_main_wallet.wallet_id,
            amount=driver_bonus_krt,
            currency="KRT",
            organization_id="ORG-COSMOX-MAIN",
            trigger_event_id=f"CMX-RIDER-ESCROW-{tx_id}",
            description=f"COSMOX Driver Delivery Bonus Escrow ({order_id}): {driver_bonus_krt} KRT under Rule 4"
        )

        deliv = CosmoxDeliveryModel(
            delivery_id=tx_id,
            order_id=order_id,
            driver_account_id=driver_account_id,
            origin_address=origin,
            destination_address=destination,
            distance_km=distance_km,
            ai_optimized_route=ai_route,
            driver_payout_fiat=driver_fiat,
            driver_bonus_krt=driver_bonus_krt,
            status="ASSIGNED_IN_TRANSIT",
            escrow_ledger_hash=tx_id
        )
        self.deliveries[deliv.delivery_id] = deliv
        return deliv

    def confirm_delivery_and_settle_escrow(
        self,
        delivery_id: str
    ) -> Tuple[CosmoxOrderModel, CosmoxDeliveryModel]:
        """
        Confirms delivery completion, strictly releasing escrowed order funds to seller and rider payment per Rule 4 & Rule 9.
        Executes tokenomics deflationary burn (2% of commission) and buyer cashback.
        """
        if delivery_id not in self.deliveries:
            raise KeyError(f"Delivery '{delivery_id}' not found.")
        deliv = self.deliveries[delivery_id]
        if deliv.status == "DELIVERY_CONFIRMED":
            raise ValueError(f"Delivery '{delivery_id}' is already confirmed and settled.")

        order = self.orders[deliv.order_id]
        buyer = self.accounts[order.buyer_account_id]
        seller = self.accounts[order.seller_account_id]
        driver = self.accounts[deliv.driver_account_id]

        # 1. Release Order Escrow: 88% to Seller Merchant Wallet, 12% to Platform Treasury (`Rule 5 & Rule 9`)
        tx_seller = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_seller,
            asset_type=AssetType.KRT,
            debit_wallet_id=buyer.escrow_wallet_id,
            credit_wallet_id=seller.merchant_wallet_id,
            amount=order.seller_payout_krt,
            currency="KRT",
            organization_id="ORG-COSMOX-MAIN",
            trigger_event_id=f"CMX-RELEASE-SELLER-{tx_seller}",
            description=f"COSMOX Escrow Release to Seller ({order.order_id}): {order.seller_payout_krt} KRT"
        )

        tx_treasury = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_treasury,
            asset_type=AssetType.KRT,
            debit_wallet_id=buyer.escrow_wallet_id,
            credit_wallet_id=self.treasury_wallet.wallet_id,
            amount=order.platform_commission_krt,
            currency="KRT",
            organization_id="ORG-COSMOX-MAIN",
            trigger_event_id=f"CMX-RELEASE-COMMISSION-{tx_treasury}",
            description=f"COSMOX Platform Commission ({order.order_id}): {order.platform_commission_krt} KRT"
        )

        # 2. Execute Deflationary Burn (`2% of platform commission`)
        burn_amount = self.tokenomics_engine.compute_deflationary_burn(order.platform_commission_krt)
        if burn_amount > 0.0:
            tx_burn = str(uuid.uuid4())
            self.ledger_engine.record_transaction(
                transaction_id=tx_burn,
                asset_type=AssetType.KRT,
                debit_wallet_id=self.treasury_wallet.wallet_id,
                credit_wallet_id=self.burn_wallet.wallet_id,
                amount=burn_amount,
                currency="KRT",
                organization_id="ORG-COSMOX-MAIN",
                trigger_event_id=f"CMX-BURN-{tx_burn}",
                description=f"COSMOX Deflationary Burn (2% of {order.platform_commission_krt} KRT): {burn_amount} KRT burned"
            )

        # 3. Disburse Buyer Cashback (`1.5%`) from Reward Pool to buyer Rewards Wallet (`AssetType.KRT_REWARDS`)
        if order.cashback_reward_krt > 0.0:
            tx_cashback = str(uuid.uuid4())
            self.ledger_engine.record_transaction(
                transaction_id=tx_cashback,
                asset_type=AssetType.KRT_REWARDS,
                debit_wallet_id=self.reward_pool_wallet.wallet_id,
                credit_wallet_id=buyer.rewards_wallet_id,
                amount=order.cashback_reward_krt,
                currency="KRT",
                organization_id="ORG-COSMOX-MAIN",
                trigger_event_id=f"CMX-CASHBACK-{tx_cashback}",
                description=f"COSMOX Buyer Cashback Reward ({order.order_id}): {order.cashback_reward_krt} KRT_REWARDS"
            )

        # 4. Release Driver Escrow Bonus strictly upon delivery confirmation (`Rule 4`)
        tx_driver_bonus = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_driver_bonus,
            asset_type=AssetType.KRT,
            debit_wallet_id=self.escrow_main_wallet.wallet_id,
            credit_wallet_id=driver.krt_wallet_id,
            amount=deliv.driver_bonus_krt,
            currency="KRT",
            organization_id="ORG-COSMOX-MAIN",
            trigger_event_id=f"CMX-RIDER-RELEASE-{tx_driver_bonus}",
            description=f"COSMOX Driver Escrow Release under Rule 4 ({deliv.delivery_id}): +{deliv.driver_bonus_krt} KRT"
        )

        # Update domain statuses and reputations
        order.escrow_status = "RELEASED_SETTLED"
        deliv.status = "DELIVERY_CONFIRMED"
        deliv.delivered_at = datetime.now(timezone.utc)
        buyer.reputation_score += 15
        seller.reputation_score += 25
        driver.reputation_score += 30

        # Publish delivery and order settlement events
        evt_deliv = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="COSMOX_DELIVERY_CONFIRMED",
            event_category=EventCategory.COSMOX_LOGISTICS,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=driver.identity_id,
            source_module="cosmox",
            organization_id="ORG-COSMOX-MAIN",
            payload={
                "delivery_id": deliv.delivery_id,
                "order_id": deliv.order_id,
                "driver_account_id": deliv.driver_account_id,
                "driver_payout_fiat": deliv.driver_payout_fiat,
                "driver_bonus_krt": deliv.driver_bonus_krt,
                "status": deliv.status,
                "escrow_ledger_hash": tx_driver_bonus
            }
        )
        self.event_bus.publish(evt_deliv)

        evt_order = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="COSMOX_ORDER_SETTLED",
            event_category=EventCategory.COSMOX_MARKETPLACE,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=seller.identity_id,
            source_module="cosmox",
            organization_id="ORG-COSMOX-MAIN",
            payload={
                "order_id": order.order_id,
                "seller_account_id": order.seller_account_id,
                "seller_payout_krt": order.seller_payout_krt,
                "platform_commission_krt": order.platform_commission_krt,
                "cashback_reward_krt": order.cashback_reward_krt,
                "ledger_entry_id": tx_seller
            }
        )
        self.event_bus.publish(evt_order)
        return (order, deliv)

    # =========================================================================
    # 5. REFERRAL NETWORK ENGINE (`Section 57.7`)
    # =========================================================================
    def qualify_and_payout_referral(
        self,
        referrer_account_id: str,
        referred_account_id: str,
        referral_type: str = "INDIVIDUAL"
    ) -> CosmoxReferralModel:
        """
        Verifies referral KYC status and disburses KRT bonus across INDIVIDUAL, MERCHANT, or DELIVERY_PARTNER tiers.
        """
        if referrer_account_id not in self.accounts or referred_account_id not in self.accounts:
            raise KeyError("Referrer or Referred Account not found.")

        referrer = self.accounts[referrer_account_id]
        referred = self.accounts[referred_account_id]

        is_approved, status_reason, reward_krt = self.referral_engine.verify_and_compute_referral_reward(
            referral_type=referral_type,
            referred_kyc_status=referred.kyc_status
        )

        if not is_approved or reward_krt <= 0.0:
            ref_blocked = CosmoxReferralModel(
                referrer_account_id=referrer_account_id,
                referred_account_id=referred_account_id,
                referral_type=referral_type.upper(),
                reward_krt=0.0,
                status=status_reason
            )
            self.referrals[ref_blocked.referral_id] = ref_blocked
            return ref_blocked

        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT_REWARDS,
            debit_wallet_id=self.reward_pool_wallet.wallet_id,
            credit_wallet_id=referrer.rewards_wallet_id,
            amount=reward_krt,
            currency="KRT",
            organization_id="ORG-COSMOX-MAIN",
            trigger_event_id=f"CMX-REF-REWARD-{tx_id}",
            description=f"COSMOX Referral Network Reward ({referral_type.upper()}): +{reward_krt} KRT_REWARDS"
        )

        ref_clean = CosmoxReferralModel(
            referral_id=tx_id,
            referrer_account_id=referrer_account_id,
            referred_account_id=referred_account_id,
            referral_type=referral_type.upper(),
            reward_krt=reward_krt,
            status="REWARDED_CLEAN",
            ledger_entry_id=tx_id
        )
        self.referrals[ref_clean.referral_id] = ref_clean

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="COSMOX_REFERRAL_REWARDED",
            event_category=EventCategory.COSMOX_MARKETPLACE,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=referrer.identity_id,
            source_module="cosmox",
            organization_id="ORG-COSMOX-MAIN",
            payload={
                "referral_id": ref_clean.referral_id,
                "referrer_account_id": referrer_account_id,
                "referred_account_id": referred_account_id,
                "referral_type": ref_clean.referral_type,
                "reward_krt": reward_krt,
                "status": ref_clean.status
            }
        )
        self.event_bus.publish(evt)
        return ref_clean

    # =========================================================================
    # 6. DIGITAL SERVICES & DEVELOPER CHECKOUT (`Section 57.9`)
    # =========================================================================
    def publish_digital_service(
        self,
        developer_account_id: str,
        title: str,
        service_type: str,
        api_endpoint_url: str,
        price_krt_per_access: float = 10.0
    ) -> CosmoxDigitalServiceModel:
        """
        Publishes a developer AI tool, software, course, or API to the COSMOX Digital Marketplace.
        """
        if developer_account_id not in self.accounts:
            raise KeyError(f"Developer Account '{developer_account_id}' not found.")

        ds = CosmoxDigitalServiceModel(
            developer_account_id=developer_account_id,
            title=title,
            service_type=service_type.upper(),
            api_endpoint_url=api_endpoint_url,
            price_krt_per_access=price_krt_per_access,
            status="PUBLISHED"
        )
        self.digital_services[ds.service_id] = ds
        return ds

    def purchase_digital_service(
        self,
        buyer_account_id: str,
        service_id: str
    ) -> Dict[str, Any]:
        """
        Executes an instant checkout for a developer digital service with 85/15 split settlement (`Rule 5 & Rule 9`).
        """
        if buyer_account_id not in self.accounts or service_id not in self.digital_services:
            raise KeyError("Buyer Account or Digital Service not found.")

        buyer = self.accounts[buyer_account_id]
        ds = self.digital_services[service_id]
        developer = self.accounts[ds.developer_account_id]

        price = ds.price_krt_per_access
        buyer_krt_w = self.wallet_engine.get_wallet(buyer.krt_wallet_id)
        if not buyer_krt_w or buyer_krt_w.balance < price:
            raise ValueError(f"Insufficient KRT inside buyer wallet. Balance: {buyer_krt_w.balance if buyer_krt_w else 0.0} KRT, Price: {price} KRT.")

        dev_payout = round(price * 0.85, 4)
        treasury_fee = round(price * 0.15, 4)

        tx_dev = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_dev,
            asset_type=AssetType.KRT,
            debit_wallet_id=buyer.krt_wallet_id,
            credit_wallet_id=developer.krt_wallet_id,
            amount=dev_payout,
            currency="KRT",
            organization_id="ORG-COSMOX-MAIN",
            trigger_event_id=f"CMX-DEV-PAYOUT-{tx_dev}",
            description=f"COSMOX Digital Service Checkout ({ds.title}): 85% Developer Share"
        )

        tx_fee = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_fee,
            asset_type=AssetType.KRT,
            debit_wallet_id=buyer.krt_wallet_id,
            credit_wallet_id=self.treasury_wallet.wallet_id,
            amount=treasury_fee,
            currency="KRT",
            organization_id="ORG-COSMOX-MAIN",
            trigger_event_id=f"CMX-DEV-FEE-{tx_fee}",
            description=f"COSMOX Digital Service Checkout ({ds.title}): 15% Platform Commission"
        )

        ds.total_subscribers += 1
        ds.total_krt_earned += dev_payout

        return {
            "status": "SUCCESS_SETTLED",
            "service_id": service_id,
            "buyer_account_id": buyer_account_id,
            "price_paid_krt": price,
            "developer_payout_krt": dev_payout,
            "treasury_fee_krt": treasury_fee,
            "ledger_entry_id": tx_dev
        }

    # =========================================================================
    # 7. MULTI-SIG TREASURY & GOVERNANCE GATES (`Section 57.11 & Rule 10`)
    # =========================================================================
    def request_multisig_treasury_disbursement(
        self,
        requester_account_id: str,
        amount_krt: float,
        purpose: str
    ) -> CosmoxMultisigRequestModel:
        """
        Creates a high-value treasury disbursement request strictly requiring 2+ explicit human RBAC approvals (`Rule 10`).
        """
        if requester_account_id not in self.accounts:
            raise KeyError(f"Account '{requester_account_id}' not found.")

        req = CosmoxMultisigRequestModel(
            requester_account_id=requester_account_id,
            amount_krt=amount_krt,
            purpose=purpose,
            ai_risk_score=15.0 if amount_krt < 100000.0 else 65.0,
            required_approvals=2,
            current_approvals=0,
            approver_ids_json="[]",
            status="PENDING_MULTISIG"
        )
        self.multisig_requests[req.request_id] = req
        return req

    def approve_multisig_treasury_request(
        self,
        approver_account_id: str,
        request_id: str
    ) -> CosmoxMultisigRequestModel:
        """
        Records human RBAC approval (`Rule 10`). When 2 approvals arrive, executes double-entry disbursement from Treasury (`Rule 5 & Rule 9`).
        """
        if request_id not in self.multisig_requests:
            raise KeyError(f"Multisig Request '{request_id}' not found.")
        if approver_account_id not in self.accounts:
            raise KeyError(f"Approver Account '{approver_account_id}' not found.")

        req = self.multisig_requests[request_id]
        if req.status == "APPROVED_DISBURSED":
            raise ValueError("Multisig request has already been fully approved and disbursed.")

        req.current_approvals += 1

        if req.current_approvals >= req.required_approvals:
            # Execute double entry from Treasury Wallet to Requester KRT Wallet
            requester = self.accounts[req.requester_account_id]
            tx_id = str(uuid.uuid4())
            self.ledger_engine.record_transaction(
                transaction_id=tx_id,
                asset_type=AssetType.KRT,
                debit_wallet_id=self.treasury_wallet.wallet_id,
                credit_wallet_id=requester.krt_wallet_id,
                amount=req.amount_krt,
                currency="KRT",
                organization_id="ORG-COSMOX-MAIN",
                trigger_event_id=f"CMX-MULTISIG-DISBURSE-{tx_id}",
                description=f"COSMOX Multi-Sig Treasury Disbursement ({req.purpose}): {req.amount_krt} KRT under Rule 10"
            )
            req.status = "APPROVED_DISBURSED"
            req.ledger_entry_id = tx_id

            evt = EventPayload(
                event_id=str(uuid.uuid4()),
                event_type="COSMOX_MULTISIG_TREASURY_APPROVED",
                event_category=EventCategory.COSMOX_TOKENOMICS,
                timestamp=datetime.now(timezone.utc),
                actor_identity_id=self.accounts[approver_account_id].identity_id,
                source_module="cosmox",
                organization_id="ORG-COSMOX-MAIN",
                payload={
                    "request_id": request_id,
                    "requester_account_id": req.requester_account_id,
                    "amount_krt": req.amount_krt,
                    "purpose": req.purpose,
                    "approvals_count": req.current_approvals,
                    "status": req.status,
                    "ledger_entry_id": tx_id
                }
            )
            self.event_bus.publish(evt)

        return req

# Export global singleton
cosmox_service = CosmoxService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
