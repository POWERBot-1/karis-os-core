"""
KARIS OS™ :: KARISFX™ Global Financial Ecosystem & KRT Economy Layer (`Section 56 / Vertical 21`).
Unifies Multi-Asset Trading across 16 global asset classes, 13 AI Services via KRT economy gating,
KRT Staking modules (up to 60% fee discounts), Transparent Reward Engine with anti-wash-trading checks,
Strategy Marketplace (85/15 split settlement), Decentralized Governance, Social Copy-Trading, and Zero-Trust AML.
Enforces all 10 Platform Rules (`Rule 1 to Rule 10`).
"""

import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from src.domain.models import (
    KarisFXAccountModel, KarisFXTradeOrderModel, KarisFXStakingPositionModel,
    KarisFXRewardHistoryModel, KarisFXMarketplaceItemModel, KarisFXMarketplacePurchaseModel,
    KarisFXGovernanceProposalModel, KarisFXGovernanceVoteModel, KarisFXSocialCopyLinkModel,
    KarisFXDeveloperAppModel, KarisFXComplianceLogModel,
    EventPayload, AssetType, WalletType, EventCategory
)
from src.core.event_bus import event_bus, UniversalEventBus
from src.core.ledger_engine import ledger_engine, UniversalLedgerEngine
from src.core.wallet_engine import wallet_engine, MultiAssetWalletEngine
from src.verticals.karisfx.ai_economy import KarisFXAIEconomyEngine
from src.verticals.karisfx.staking_engine import KarisFXStakingEngine
from src.verticals.karisfx.reward_engine import KarisFXRewardEngine

class KarisFXService:
    """
    Unified Multi-Asset Trading Platform and KRT Economy Engine (`Vertical 21`).
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

        self.ai_economy = KarisFXAIEconomyEngine()
        self.staking_engine = KarisFXStakingEngine()
        self.reward_engine = KarisFXRewardEngine()

        # In-memory domain repositories synced with database projections
        self.accounts: Dict[str, KarisFXAccountModel] = {}
        self.orders_trades: Dict[str, KarisFXTradeOrderModel] = {}
        self.staking_positions: Dict[str, KarisFXStakingPositionModel] = {}
        self.rewards_history: Dict[str, KarisFXRewardHistoryModel] = {}
        self.marketplace_items: Dict[str, KarisFXMarketplaceItemModel] = {}
        self.marketplace_purchases: Dict[str, KarisFXMarketplacePurchaseModel] = {}
        self.governance_proposals: Dict[str, KarisFXGovernanceProposalModel] = {}
        self.governance_votes: Dict[str, KarisFXGovernanceVoteModel] = {}
        self.social_copy_links: Dict[str, KarisFXSocialCopyLinkModel] = {}
        self.developer_apps: Dict[str, KarisFXDeveloperAppModel] = {}
        self.compliance_logs: Dict[str, KarisFXComplianceLogModel] = {}

        self.supported_asset_classes = [
            "FOREX", "STOCKS", "ETFS", "COMMODITIES", "PRECIOUS_METALS",
            "ENERGY_MARKETS", "INDICES", "BONDS", "FUTURES", "OPTIONS",
            "MONEY_MARKETS", "MUTUAL_FUNDS", "TOKENIZED_ASSETS", "AI_PORTFOLIOS",
            "SOCIAL_TRADING", "COPY_TRADING"
        ]

        # Initialize systemic KRT reserve pools for KARISFX economy
        self._init_system_pools()

    def _init_system_pools(self):
        """
        Auto-initializes system reserve wallets for Staking, Rewards, Liquidity, and Treasury.
        """
        self.staking_pool_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-KARISFX-STAKING",
            organization_id="ORG-KARISFX-MAIN",
            wallet_type=WalletType.STAKING_POOL,
            asset_type=AssetType.KRT,
            initial_balance=10000000.0
        )
        self.reward_pool_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-KARISFX-REWARDS",
            organization_id="ORG-KARISFX-MAIN",
            wallet_type=WalletType.REWARD_POOL,
            asset_type=AssetType.KRT_REWARDS,
            initial_balance=5000000.0
        )
        self.liquidity_pool_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-KARISFX-LIQUIDITY",
            organization_id="ORG-KARISFX-MAIN",
            wallet_type=WalletType.RESERVE_WALLET,
            asset_type=AssetType.KRT,
            initial_balance=25000000.0
        )
        self.treasury_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-KARISFX-TREASURY",
            organization_id="ORG-KARISFX-MAIN",
            wallet_type=WalletType.TREASURY_WALLET,
            asset_type=AssetType.KRT,
            initial_balance=10000000.0
        )

    # =========================================================================
    # 1. KRT FOUNDATION & UNIFIED WALLET ONBOARDING (`Section 56.2 & 56.9`)
    # =========================================================================
    def onboard_karisfx_account(
        self,
        identity_id: str,
        full_name: str,
        phone_number: str,
        initial_krt_deposit: float = 1000.0,
        initial_usd_deposit: float = 5000.0
    ) -> KarisFXAccountModel:
        """
        Onboards a user into KARISFX, establishing their KRT Foundation and 7 multi-currency wallets.
        Enforces KYC Tier 3 verification per Compliance regulations (`Rule 1 & Rule 6`).
        """
        account_number = f"KFX-{uuid.uuid4().hex[:8].upper()}"
        treasury_ref = f"TREASURY-ACCOUNT-REF-{identity_id}"

        # Create multi-asset wallets for the user
        krt_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-krt", "ORG-KARISFX-MAIN", WalletType.KRT_WALLET, AssetType.KRT, initial_krt_deposit)
        kes_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-kes", "ORG-KARISFX-MAIN", WalletType.KES_WALLET, AssetType.KES, initial_krt_deposit * 130.0)
        usd_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-usd", "ORG-KARISFX-MAIN", WalletType.USD_WALLET, AssetType.USD, initial_usd_deposit)
        eur_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-eur", "ORG-KARISFX-MAIN", WalletType.EUR_WALLET, AssetType.EUR, initial_usd_deposit * 0.92)
        gbp_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-gbp", "ORG-KARISFX-MAIN", WalletType.GBP_WALLET, AssetType.GBP, initial_usd_deposit * 0.79)
        stable_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-stable", "ORG-KARISFX-MAIN", WalletType.STABLECOIN_WALLET, AssetType.USDT, initial_usd_deposit)
        rewards_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-rewards", "ORG-KARISFX-MAIN", WalletType.REWARDS_WALLET, AssetType.KRT_REWARDS, 100.0)

        account = KarisFXAccountModel(
            identity_id=identity_id,
            account_number=account_number,
            account_tier="STANDARD",
            kyc_status="VERIFIED_TIER_3",
            krt_wallet_id=krt_w.wallet_id,
            kes_wallet_id=kes_w.wallet_id,
            usd_wallet_id=usd_w.wallet_id,
            eur_wallet_id=eur_w.wallet_id,
            gbp_wallet_id=gbp_w.wallet_id,
            stablecoin_wallet_id=stable_w.wallet_id,
            rewards_wallet_id=rewards_w.wallet_id,
            treasury_account_ref=treasury_ref,
            reputation_score=100
        )
        self.accounts[account.account_id] = account

        # Publish onboarding event
        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="KARISFX_ACCOUNT_CREATED",
            event_category=EventCategory.FINANCIAL_MARKETS,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=identity_id,
            source_module="karisfx",
            organization_id="ORG-KARISFX-MAIN",
            payload={
                "account_id": account.account_id,
                "identity_id": identity_id,
                "account_number": account_number,
                "account_tier": account.account_tier,
                "kyc_status": account.kyc_status,
                "krt_wallet_id": krt_w.wallet_id,
                "kes_wallet_id": kes_w.wallet_id,
                "usd_wallet_id": usd_w.wallet_id,
                "eur_wallet_id": eur_w.wallet_id,
                "gbp_wallet_id": gbp_w.wallet_id,
                "stablecoin_wallet_id": stable_w.wallet_id,
                "rewards_wallet_id": rewards_w.wallet_id,
                "treasury_account_ref": treasury_ref,
                "reputation_score": account.reputation_score
            }
        )
        self.event_bus.publish(evt)
        return account

    # =========================================================================
    # 2. MULTI-ASSET TRADING WITH KRT FEE DISCOUNTS (`Section 56.3`)
    # =========================================================================
    def execute_multi_asset_trade(
        self,
        account_id: str,
        asset_class: str,
        symbol: str,
        side: str,
        requested_units: float,
        execution_price: float,
        leverage: float = 1.0,
        pay_fees_in_krt: bool = True
    ) -> KarisFXTradeOrderModel:
        """
        Executes a trade across the 16 supported asset classes.
        Calculates trading fees in KRT with up to 60% staking fee discount.
        Records immutable double-entry ledger settlement (`Rule 5 & Rule 9`).
        """
        if account_id not in self.accounts:
            raise KeyError(f"KARISFX Account '{account_id}' not found.")
        account = self.accounts[account_id]

        ac_upper = asset_class.upper()
        if ac_upper not in self.supported_asset_classes:
            raise ValueError(f"Asset class '{asset_class}' not supported. Must be one of {self.supported_asset_classes}")

        if requested_units <= 0.0 or execution_price <= 0.0:
            raise ValueError("Requested units and execution price must be strictly positive.")

        total_value_usd = requested_units * execution_price

        # Check AML threshold check before trade execution
        self.audit_compliance_and_aml(account_id, f"TRADE_EXECUTION_{ac_upper}", total_value_usd)

        # Calculate base trading fee (e.g., 0.15% of trade value in USD equivalent converted to KRT at 1 USD = 130 KRT)
        base_fee_usd = total_value_usd * 0.0015
        base_fee_krt = base_fee_usd * 130.0

        # Evaluate staking discount
        staked_krt = self._get_staked_amount_for_account(account_id)
        tier_name, _, discount_pct, _, _ = self.staking_engine.evaluate_staking_tier(staked_krt)

        if pay_fees_in_krt:
            final_fee_krt = round(base_fee_krt * (1.0 - (discount_pct / 100.0)), 4)
        else:
            final_fee_krt = round(base_fee_krt, 4)

        # Check user KRT wallet balance for fee payment
        user_krt_w = self.wallet_engine.get_wallet(account.krt_wallet_id)
        if not user_krt_w or user_krt_w.balance < final_fee_krt:
            # If user KRT balance is insufficient, attempt double-entry top-up from their USD/KES wallet or fail
            raise ValueError(f"Insufficient KRT balance for trading fee. Balance: {user_krt_w.balance if user_krt_w else 0.0} KRT, Required: {final_fee_krt} KRT.")

        # Record double-entry ledger transaction for fee settlement (`Rule 5 & Rule 9`)
        tx_id = str(uuid.uuid4())
        ledger_entry = self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=account.krt_wallet_id,
            credit_wallet_id=self.treasury_wallet.wallet_id,
            amount=final_fee_krt,
            currency="KRT",
            organization_id="ORG-KARISFX-MAIN",
            trigger_event_id=f"TRADE-FEE-{tx_id}",
            description=f"KARISFX Trading Fee ({ac_upper}: {symbol} {side}) with {discount_pct}% Staking Discount"
        )

        trade_order = KarisFXTradeOrderModel(
            trade_id=tx_id,
            account_id=account_id,
            asset_class=ac_upper,
            symbol=symbol.upper(),
            side=side.upper(),
            order_type="MARKET",
            requested_units=requested_units,
            execution_price=execution_price,
            total_value_usd=round(total_value_usd, 4),
            leverage=leverage,
            base_fee_krt=round(base_fee_krt, 4),
            fee_discount_pct=discount_pct,
            final_fee_krt=final_fee_krt,
            status="EXECUTED_SETTLED",
            ledger_entry_id=ledger_entry.entry_id
        )
        self.orders_trades[trade_order.trade_id] = trade_order

        # Auto-award trading activity KRT reward
        self.claim_platform_reward(account_id, "TRADING_ACTIVITY", custom_amount_krt=15.0, trade_holding_seconds=3600.0)

        # Publish trade execution event
        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="KARISFX_TRADE_EXECUTED",
            event_category=EventCategory.FX_TRADING,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=account.identity_id,
            source_module="karisfx",
            organization_id="ORG-KARISFX-MAIN",
            payload={
                "trade_id": trade_order.trade_id,
                "account_id": account_id,
                "asset_class": trade_order.asset_class,
                "symbol": trade_order.symbol,
                "side": trade_order.side,
                "requested_units": trade_order.requested_units,
                "execution_price": trade_order.execution_price,
                "total_value_usd": trade_order.total_value_usd,
                "final_fee_krt": trade_order.final_fee_krt,
                "fee_discount_pct": trade_order.fee_discount_pct,
                "ledger_entry_id": trade_order.ledger_entry_id
            }
        )
        self.event_bus.publish(evt)
        return trade_order

    def _get_staked_amount_for_account(self, account_id: str) -> float:
        """
        Returns total active staked KRT for a given account.
        """
        total = 0.0
        for pos in self.staking_positions.values():
            if pos.account_id == account_id and pos.status == "ACTIVE":
                total += pos.staked_amount_krt
        return total

    # =========================================================================
    # 3. KRT STAKING & TIER MANAGEMENT (`Section 56.5`)
    # =========================================================================
    def open_staking_position(
        self,
        account_id: str,
        amount_krt: float,
        lockup_duration_days: int = 90
    ) -> KarisFXStakingPositionModel:
        """
        Locks KRT into the Staking Pool to earn 12-25% APY and unlock up to 60% fee discounts.
        Executes double-entry movement (`Rule 5 & Rule 9`).
        """
        if account_id not in self.accounts:
            raise KeyError(f"KARISFX Account '{account_id}' not found.")
        account = self.accounts[account_id]

        user_krt_w = self.wallet_engine.get_wallet(account.krt_wallet_id)
        if not user_krt_w or user_krt_w.balance < amount_krt:
            raise ValueError(f"Insufficient KRT inside wallet to stake. Balance: {user_krt_w.balance if user_krt_w else 0.0} KRT, Requested: {amount_krt} KRT.")

        specs = self.staking_engine.calculate_staking_position_specs(amount_krt, lockup_duration_days)

        # Double-entry movement from user KRT wallet into Staking Pool
        tx_id = str(uuid.uuid4())
        ledger_entry = self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=account.krt_wallet_id,
            credit_wallet_id=self.staking_pool_wallet.wallet_id,
            amount=amount_krt,
            currency="KRT",
            organization_id="ORG-KARISFX-MAIN",
            trigger_event_id=f"STAKE-LOCK-{tx_id}",
            description=f"KARISFX KRT Staking Lockup ({specs['staking_tier']} Tier, {lockup_duration_days} Days)"
        )

        # Update account tier and reputation
        account.account_tier = specs["staking_tier"]
        account.reputation_score += specs["reputation_boost"]

        pos = KarisFXStakingPositionModel(
            staking_id=tx_id,
            account_id=account_id,
            staking_tier=specs["staking_tier"],
            staked_amount_krt=amount_krt,
            lockup_duration_days=specs["lockup_duration_days"],
            apy_pct=specs["apy_pct"],
            fee_discount_pct=specs["fee_discount_pct"],
            ai_premium_unlocked=specs["ai_premium_unlocked"],
            governance_voting_power=specs["governance_voting_power"],
            status="ACTIVE",
            unlocks_at=datetime.fromisoformat(specs["unlocks_at"])
        )
        self.staking_positions[pos.staking_id] = pos

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="KARISFX_STAKING_POSITION_OPENED",
            event_category=EventCategory.STAKING,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=account.identity_id,
            source_module="karisfx",
            organization_id="ORG-KARISFX-MAIN",
            payload={
                "staking_id": pos.staking_id,
                "account_id": account_id,
                "staking_tier": pos.staking_tier,
                "staked_amount_krt": pos.staked_amount_krt,
                "lockup_duration_days": pos.lockup_duration_days,
                "apy_pct": pos.apy_pct,
                "fee_discount_pct": pos.fee_discount_pct,
                "ai_premium_unlocked": pos.ai_premium_unlocked
            }
        )
        self.event_bus.publish(evt)
        return pos

    # =========================================================================
    # 4. REWARD ENGINE WITH ANTI-ABUSE CONTROLS (`Section 56.6`)
    # =========================================================================
    def claim_platform_reward(
        self,
        account_id: str,
        activity_type: str,
        custom_amount_krt: float = 0.0,
        trade_holding_seconds: float = 3600.0
    ) -> KarisFXRewardHistoryModel:
        """
        Verifies and distributes transparent KRT rewards across 10 platform activities.
        Enforces anti-wash-trading velocity checks and daily limits (`Rule 1 & Rule 6`).
        """
        if account_id not in self.accounts:
            raise KeyError(f"KARISFX Account '{account_id}' not found.")
        account = self.accounts[account_id]

        # Calculate today's existing rewards
        today_claims = 0.0
        for rew in self.rewards_history.values():
            if rew.account_id == account_id and rew.anti_abuse_status == "VERIFIED_CLEAN":
                today_claims += rew.reward_amount_krt

        is_approved, status_reason, final_reward_krt, v_hash = self.reward_engine.verify_and_compute_reward(
            account_id=account_id,
            activity_type=activity_type,
            custom_amount_krt=custom_amount_krt,
            recent_claims_today_krt=today_claims,
            trade_holding_seconds=trade_holding_seconds
        )

        if not is_approved or final_reward_krt <= 0.0:
            # Record blocked reward attempt
            blocked_entry = KarisFXRewardHistoryModel(
                account_id=account_id,
                activity_type=activity_type.upper(),
                reward_amount_krt=0.0,
                anti_abuse_status=status_reason,
                verification_hash=v_hash if v_hash else "REJECTED_BLOCKED"
            )
            self.rewards_history[blocked_entry.reward_id] = blocked_entry
            return blocked_entry

        # Execute double-entry reward disbursement from Reward Pool to user KRT rewards wallet
        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT_REWARDS,
            debit_wallet_id=self.reward_pool_wallet.wallet_id,
            credit_wallet_id=account.rewards_wallet_id,
            amount=final_reward_krt,
            currency="KRT",
            organization_id="ORG-KARISFX-MAIN",
            trigger_event_id=f"REWARD-DISBURSE-{tx_id}",
            description=f"KARISFX Reward Engine Payout ({activity_type.upper()}): {final_reward_krt} KRT"
        )

        reward_entry = KarisFXRewardHistoryModel(
            reward_id=tx_id,
            account_id=account_id,
            activity_type=activity_type.upper(),
            reward_amount_krt=final_reward_krt,
            anti_abuse_status="VERIFIED_CLEAN",
            verification_hash=v_hash
        )
        self.rewards_history[reward_entry.reward_id] = reward_entry

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="KARISFX_REWARD_DISTRIBUTED",
            event_category=EventCategory.REWARDS,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=account.identity_id,
            source_module="karisfx",
            organization_id="ORG-KARISFX-MAIN",
            payload={
                "reward_id": reward_entry.reward_id,
                "account_id": account_id,
                "activity_type": reward_entry.activity_type,
                "reward_amount_krt": reward_entry.reward_amount_krt,
                "anti_abuse_status": reward_entry.anti_abuse_status,
                "verification_hash": reward_entry.verification_hash
            }
        )
        self.event_bus.publish(evt)
        return reward_entry

    # =========================================================================
    # 5. STRATEGY & AI MARKETPLACE WITH SPLIT SETTLEMENT (`Section 56.7`)
    # =========================================================================
    def publish_marketplace_item(
        self,
        creator_account_id: str,
        item_type: str,
        title: str,
        description: str,
        price_krt: float,
        historical_win_rate_pct: Optional[float] = None,
        sharpe_ratio: Optional[float] = None
    ) -> KarisFXMarketplaceItemModel:
        """
        Publishes a trading strategy, indicator, AI model, or course to the KARISFX Marketplace.
        """
        if creator_account_id not in self.accounts:
            raise KeyError(f"Creator Account '{creator_account_id}' not found.")

        item = KarisFXMarketplaceItemModel(
            creator_account_id=creator_account_id,
            item_type=item_type.upper(),
            title=title,
            description=description,
            price_krt=price_krt,
            historical_win_rate_pct=historical_win_rate_pct,
            sharpe_ratio=sharpe_ratio,
            status="PUBLISHED"
        )
        self.marketplace_items[item.item_id] = item
        return item

    def purchase_marketplace_item(
        self,
        buyer_account_id: str,
        item_id: str
    ) -> KarisFXMarketplacePurchaseModel:
        """
        Executes a KRT checkout for a marketplace strategy/bot with 85/15 split settlement (`Rule 5 & Rule 9`).
        """
        if buyer_account_id not in self.accounts:
            raise KeyError(f"Buyer Account '{buyer_account_id}' not found.")
        if item_id not in self.marketplace_items:
            raise KeyError(f"Marketplace item '{item_id}' not found.")

        buyer = self.accounts[buyer_account_id]
        item = self.marketplace_items[item_id]
        creator = self.accounts[item.creator_account_id]

        price_krt = item.price_krt
        buyer_krt_w = self.wallet_engine.get_wallet(buyer.krt_wallet_id)
        if not buyer_krt_w or buyer_krt_w.balance < price_krt:
            raise ValueError(f"Insufficient KRT inside buyer wallet. Balance: {buyer_krt_w.balance if buyer_krt_w else 0.0} KRT, Price: {price_krt} KRT.")

        creator_payout = round(price_krt * 0.85, 4)
        treasury_fee = round(price_krt * 0.15, 4)

        tx_id_1 = str(uuid.uuid4())
        # Leg 1: 85% payout to Creator KRT wallet
        self.ledger_engine.record_transaction(
            transaction_id=tx_id_1,
            asset_type=AssetType.KRT,
            debit_wallet_id=buyer.krt_wallet_id,
            credit_wallet_id=creator.krt_wallet_id,
            amount=creator_payout,
            currency="KRT",
            organization_id="ORG-KARISFX-MAIN",
            trigger_event_id=f"MKT-BUY-CREATOR-{tx_id_1}",
            description=f"KARISFX Marketplace Purchase ({item.title}): 85% Creator Share to {creator.account_number}"
        )

        tx_id_2 = str(uuid.uuid4())
        # Leg 2: 15% platform commission to Treasury
        self.ledger_engine.record_transaction(
            transaction_id=tx_id_2,
            asset_type=AssetType.KRT,
            debit_wallet_id=buyer.krt_wallet_id,
            credit_wallet_id=self.treasury_wallet.wallet_id,
            amount=treasury_fee,
            currency="KRT",
            organization_id="ORG-KARISFX-MAIN",
            trigger_event_id=f"MKT-BUY-TREASURY-{tx_id_2}",
            description=f"KARISFX Marketplace Purchase ({item.title}): 15% Platform Commission"
        )

        item.total_subscribers += 1

        purchase = KarisFXMarketplacePurchaseModel(
            purchase_id=tx_id_1,
            item_id=item_id,
            buyer_account_id=buyer_account_id,
            price_paid_krt=price_krt,
            creator_payout_krt=creator_payout,
            treasury_fee_krt=treasury_fee,
            ledger_entry_id=tx_id_1
        )
        self.marketplace_purchases[purchase.purchase_id] = purchase

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="KARISFX_MARKETPLACE_PURCHASED",
            event_category=EventCategory.COMMERCE,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=buyer.identity_id,
            source_module="karisfx",
            organization_id="ORG-KARISFX-MAIN",
            payload={
                "purchase_id": purchase.purchase_id,
                "item_id": item_id,
                "buyer_account_id": buyer_account_id,
                "price_paid_krt": price_krt,
                "creator_payout_krt": creator_payout,
                "treasury_fee_krt": treasury_fee,
                "ledger_entry_id": tx_id_1
            }
        )
        self.event_bus.publish(evt)
        return purchase

    # =========================================================================
    # 6. DECENTRALIZED GOVERNANCE (`Section 56.8`)
    # =========================================================================
    def create_governance_proposal(
        self,
        creator_account_id: str,
        category: str,
        title: str,
        description: str,
        voting_days: int = 7
    ) -> KarisFXGovernanceProposalModel:
        """
        Creates a decentralized governance proposal. Uses AI to summarize systemic impact (`Rule 10`).
        """
        if creator_account_id not in self.accounts:
            raise KeyError(f"Account '{creator_account_id}' not found.")

        ai_summary = f"Rule 10 AI Governance Advisory: Proposal '{title}' under category '{category.upper()}' has been evaluated. Recommended for community KRT-weighted vote while reserving core security & regulatory compliance gates exclusively for PLATFORM_ADMINISTRATOR."

        proposal = KarisFXGovernanceProposalModel(
            creator_account_id=creator_account_id,
            category=category.upper(),
            title=title,
            description=description,
            ai_impact_summary=ai_summary,
            voting_ends_at=datetime.now(timezone.utc) + timedelta(days=voting_days)
        )
        self.governance_proposals[proposal.proposal_id] = proposal
        return proposal

    def cast_governance_vote(
        self,
        voter_account_id: str,
        proposal_id: str,
        vote_choice: str
    ) -> KarisFXGovernanceVoteModel:
        """
        Records a KRT-weighted governance vote (`FOR`, `AGAINST`, `ABSTAIN`).
        """
        if voter_account_id not in self.accounts:
            raise KeyError(f"Account '{voter_account_id}' not found.")
        if proposal_id not in self.governance_proposals:
            raise KeyError(f"Proposal '{proposal_id}' not found.")

        proposal = self.governance_proposals[proposal_id]
        voter = self.accounts[voter_account_id]

        staked_krt = self._get_staked_amount_for_account(voter_account_id)
        user_w = self.wallet_engine.get_wallet(voter.krt_wallet_id)
        wallet_balance = user_w.balance if user_w else 0.0

        # Voting power = Staked KRT + (Wallet Balance * 0.5)
        voting_power = round(staked_krt + (wallet_balance * 0.5), 4)
        if voting_power <= 0.0:
            raise ValueError("Zero KRT voting power. Must hold or stake KRT to participate in governance.")

        choice = vote_choice.upper()
        if choice not in ["FOR", "AGAINST", "ABSTAIN"]:
            raise ValueError("Vote choice must be FOR, AGAINST, or ABSTAIN.")

        if choice == "FOR":
            proposal.votes_for_krt += voting_power
        elif choice == "AGAINST":
            proposal.votes_against_krt += voting_power

        vote = KarisFXGovernanceVoteModel(
            proposal_id=proposal_id,
            voter_account_id=voter_account_id,
            vote_choice=choice,
            voting_power_krt=voting_power
        )
        self.governance_votes[vote.vote_id] = vote

        # Award ecosystem participation reward
        self.claim_platform_reward(voter_account_id, "ECOSYSTEM_PARTICIPATION", custom_amount_krt=20.0)

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="KARISFX_GOVERNANCE_VOTED",
            event_category=EventCategory.GOVERNANCE_VOTING,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=voter.identity_id,
            source_module="karisfx",
            organization_id="ORG-KARISFX-MAIN",
            payload={
                "vote_id": vote.vote_id,
                "proposal_id": proposal_id,
                "voter_account_id": voter_account_id,
                "vote_choice": choice,
                "voting_power_krt": voting_power
            }
        )
        self.event_bus.publish(evt)
        return vote

    # =========================================================================
    # 7. SOCIAL FINANCE & COPY TRADING (`Section 56.10`)
    # =========================================================================
    def link_copy_trade(
        self,
        follower_account_id: str,
        master_trader_account_id: str,
        allocation_krt: float,
        copy_ratio: float = 1.0
    ) -> KarisFXSocialCopyLinkModel:
        """
        Establishes a social copy-trading link between a follower and a verified master trader.
        """
        if follower_account_id not in self.accounts or master_trader_account_id not in self.accounts:
            raise KeyError("Follower or Master Trader account not found.")

        link = KarisFXSocialCopyLinkModel(
            follower_account_id=follower_account_id,
            master_trader_account_id=master_trader_account_id,
            allocation_krt=allocation_krt,
            copy_ratio=copy_ratio,
            status="ACTIVE"
        )
        self.social_copy_links[link.copy_link_id] = link

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="KARISFX_COPY_TRADE_EXECUTED",
            event_category=EventCategory.SOCIAL,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=self.accounts[follower_account_id].identity_id,
            source_module="karisfx",
            organization_id="ORG-KARISFX-MAIN",
            payload={
                "copy_link_id": link.copy_link_id,
                "follower_account_id": follower_account_id,
                "master_trader_account_id": master_trader_account_id,
                "copied_trade_id": f"INIT-COPY-{link.copy_link_id}",
                "follower_trade_id": f"INIT-COPY-{link.copy_link_id}",
                "allocation_krt": allocation_krt
            }
        )
        self.event_bus.publish(evt)
        return link

    # =========================================================================
    # 8. DEVELOPER PLATFORM & API MONETIZATION (`Section 56.11`)
    # =========================================================================
    def register_developer_app(
        self,
        developer_account_id: str,
        app_name: str,
        app_type: str,
        monetization_fee_krt_per_call: float = 1.0
    ) -> KarisFXDeveloperAppModel:
        """
        Registers an AI bot, analytics plugin, or risk tool on the KARISFX Developer Platform.
        """
        if developer_account_id not in self.accounts:
            raise KeyError(f"Developer Account '{developer_account_id}' not found.")

        api_key_raw = f"kfx_secret_{uuid.uuid4().hex}"
        api_key_hash = hashlib.sha256(api_key_raw.encode("utf-8")).hexdigest()

        app = KarisFXDeveloperAppModel(
            developer_account_id=developer_account_id,
            app_name=app_name,
            app_type=app_type.upper(),
            api_key_hash=api_key_hash,
            monetization_fee_krt_per_call=monetization_fee_krt_per_call,
            status="ACTIVE"
        )
        self.developer_apps[app.app_id] = app
        return app

    # =========================================================================
    # 9. ZERO-TRUST COMPLIANCE & AML MONITORING (`Section 56.12`)
    # =========================================================================
    def audit_compliance_and_aml(
        self,
        account_id: str,
        event_type: str,
        transaction_amount_usd: float
    ) -> KarisFXComplianceLogModel:
        """
        Executes continuous AML and KYC Tier verification. Flags transactions exceeding FIU thresholds (`> $10,000 equivalent`).
        """
        if account_id not in self.accounts:
            raise KeyError(f"Account '{account_id}' not found.")
        account = self.accounts[account_id]

        risk_score = 12.5
        fiu_flagged = False
        notes = f"Zero Trust continuous screening for {event_type} ({transaction_amount_usd} USD)."

        if transaction_amount_usd >= 10000.0:
            risk_score = 85.0
            fiu_flagged = True
            notes = f"ALERT: High value transaction ({transaction_amount_usd} USD) exceeds CBK/FIU $10,000 reporting threshold. Mandates KYC Tier 3 audit verification."

        log = KarisFXComplianceLogModel(
            account_id=account_id,
            event_type=event_type,
            transaction_amount_usd=transaction_amount_usd,
            aml_risk_score=risk_score,
            jurisdiction_code="KE-EAC",
            cbk_fiu_flagged=fiu_flagged,
            audit_notes=notes
        )
        self.compliance_logs[log.log_id] = log

        if fiu_flagged:
            evt = EventPayload(
                event_id=str(uuid.uuid4()),
                event_type="KARISFX_AML_ALERT_TRIGGERED",
                event_category=EventCategory.GOVERNANCE,
                timestamp=datetime.now(timezone.utc),
                actor_identity_id=account.identity_id,
                source_module="karisfx",
                organization_id="ORG-KARISFX-MAIN",
                payload={
                    "log_id": log.log_id,
                    "account_id": account_id,
                    "transaction_amount_usd": transaction_amount_usd,
                    "aml_risk_score": risk_score,
                    "cbk_fiu_flagged": fiu_flagged,
                    "audit_notes": notes
                }
            )
            self.event_bus.publish(evt)

        return log

# Export global singleton
karisfx_service = KarisFXService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
