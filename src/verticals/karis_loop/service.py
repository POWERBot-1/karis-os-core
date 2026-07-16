import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from src.domain.models import (
    KarisLoopProfileModel, KarisLoopCommunityModel, KarisLoopPostModel,
    KarisLoopTipTransactionModel, KarisLoopMessageModel,
    EventPayload, AssetType, WalletType
)
from src.core.event_bus import event_bus, UniversalEventBus
from src.core.ledger_engine import ledger_engine, UniversalLedgerEngine
from src.core.wallet_engine import wallet_engine, MultiAssetWalletEngine
from src.verticals.karis_loop.ai_copilot import KarisLoopAICopilot
from src.verticals.karis_loop.graph_engine import KarisLoopGraphEngine

class KarisLoopService:
    """
    KARIS OS™ :: KARIS LOOP™ Social Intelligence Layer (`Section 54 / Vertical 19`).
    Unifies 7 Interconnected Graphs, Multi-Priority Feeds, Creator Tipping (`Rule 9 double entry`),
    Shoppable Checkouts (`One Wallet Economy`), and AI Moderation (`Rule 10`).
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
        self.ai_copilot = KarisLoopAICopilot()
        self.graph_engine = KarisLoopGraphEngine()

        self.profiles: Dict[str, KarisLoopProfileModel] = {}
        self.communities: Dict[str, KarisLoopCommunityModel] = {}
        self.posts: Dict[str, KarisLoopPostModel] = {}
        self.tips: Dict[str, KarisLoopTipTransactionModel] = {}
        self.messages: Dict[str, KarisLoopMessageModel] = {}

    def register_profile(
        self,
        user_identity_id: str,
        organization_id: str,
        handle_username: str,
        display_name: str,
        account_type: str = "CREATOR_USER"
    ) -> KarisLoopProfileModel:
        """Registers a user, creator, or verified business profile on Karis Loop (`Section 54.2`)."""
        prof = KarisLoopProfileModel(
            user_identity_id=user_identity_id,
            organization_id=organization_id,
            handle_username=handle_username,
            display_name=display_name,
            account_type=account_type
        )
        self.profiles[prof.profile_id] = prof
        self.graph_engine.link_relationship("SOCIAL", user_identity_id, user_identity_id)

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="LOOP_PROFILE_REGISTERED",
            event_category="SOCIAL",
            actor_identity_id=user_identity_id,
            organization_id=organization_id,
            correlation_id=prof.profile_id,
            source_module="KARIS_LOOP_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload=prof.model_dump(mode="json")
        )
        self.event_bus.publish(ev)
        return prof

    def create_community(
        self,
        name: str,
        community_type: str,
        region_county: str,
        creator_identity_id: str,
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> KarisLoopCommunityModel:
        """Creates a public, private, regional, or educational community (`Section 54.6`)."""
        comm = KarisLoopCommunityModel(
            organization_id=organization_id,
            name=name,
            community_type=community_type,
            region_county=region_county,
            creator_identity_id=creator_identity_id
        )
        self.communities[comm.community_id] = comm
        self.graph_engine.link_relationship("COMMUNITY", creator_identity_id, comm.community_id)

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="LOOP_COMMUNITY_CREATED",
            event_category="SOCIAL",
            actor_identity_id=creator_identity_id,
            organization_id=organization_id,
            correlation_id=comm.community_id,
            source_module="KARIS_LOOP_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload=comm.model_dump(mode="json")
        )
        self.event_bus.publish(ev)
        return comm

    def create_post(
        self,
        creator_identity_id: str,
        community_id: str,
        content_type: str,
        caption_text: str,
        media_payload_json: str,
        linked_product_id: Optional[str] = None,
        shoppable_price_kes: float = 0.0
    ) -> KarisLoopPostModel:
        """
        Publishes short-form video, story, or shoppable post (`Rule 6`).
        Executes AI Moderation toxicity evaluation (`Rule 10`).
        """
        mod_res = self.ai_copilot.evaluate_content_toxicity(caption_text, content_type)
        status = mod_res["ai_moderation_status"]

        post = KarisLoopPostModel(
            creator_identity_id=creator_identity_id,
            community_id=community_id,
            content_type=content_type,
            caption_text=caption_text,
            media_payload_json=media_payload_json,
            linked_product_id=linked_product_id,
            shoppable_price_kes=shoppable_price_kes,
            ai_moderation_status=status
        )
        self.posts[post.post_id] = post

        if linked_product_id:
            self.graph_engine.link_relationship("COMMERCE", post.post_id, linked_product_id)

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="LOOP_CONTENT_POSTED",
            event_category="SOCIAL",
            actor_identity_id=creator_identity_id,
            organization_id="ORG-KARIS-RETAIL",
            correlation_id=post.post_id,
            source_module="KARIS_LOOP_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "post_id": post.post_id,
                "creator_identity_id": creator_identity_id,
                "content_type": content_type,
                "caption_text": caption_text,
                "linked_product_id": linked_product_id or "NONE",
                "shoppable_price_kes": shoppable_price_kes,
                "ai_moderation_status": status
            }
        )
        self.event_bus.publish(ev)
        return post

    def tip_creator(
        self,
        tipper_identity_id: str,
        creator_identity_id: str,
        post_id: str,
        amount_krt: float
    ) -> Dict[str, Any]:
        """
        Processes double-entry KRT tipping (`Rule 5 & Rule 9`).
        Tipper KRT wallet debited, Creator KRT wallet credited.
        """
        if amount_krt <= 0:
            raise ValueError("Tip amount must be strictly greater than 0 KRT.")

        if post_id not in self.posts:
            raise KeyError(f"Post ID {post_id} not found.")
        post = self.posts[post_id]

        tipper_wallet = self.wallet_engine.get_or_create_wallet(tipper_identity_id, "ORG-KARIS-RETAIL", WalletType.KRT_WALLET, AssetType.KRT, 0.0)
        if tipper_wallet.balance < amount_krt:
            raise ValueError(f"Insufficient KRT balance for tip. Balance: {tipper_wallet.balance}, Required: {amount_krt}")

        creator_wallet = self.wallet_engine.get_or_create_wallet(creator_identity_id, "ORG-KARIS-RETAIL", WalletType.KRT_WALLET, AssetType.KRT, 0.0)

        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=tipper_wallet.wallet_id,
            credit_wallet_id=creator_wallet.wallet_id,
            amount=amount_krt,
            currency="KRT",
            organization_id="ORG-KARIS-RETAIL",
            trigger_event_id=f"TIP-{post_id[:8]}",
            description=f"Karis Loop Creator Tip ({amount_krt} KRT) for post {post_id}"
        )

        post.tips_krt_total = round(post.tips_krt_total + amount_krt, 4)
        if creator_identity_id in self.profiles:
            self.profiles[creator_identity_id].total_krt_tips_received = round(self.profiles[creator_identity_id].total_krt_tips_received + amount_krt, 4)

        tip_rec = KarisLoopTipTransactionModel(
            post_id=post_id,
            tipper_identity_id=tipper_identity_id,
            creator_identity_id=creator_identity_id,
            amount_krt=amount_krt,
            reconciled_ledger_hash=self.ledger_engine.last_hash
        )
        self.tips[tip_rec.tip_id] = tip_rec
        self.graph_engine.link_relationship("CREATOR", tipper_identity_id, creator_identity_id)

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="LOOP_CREATOR_TIPPED",
            event_category="SOCIAL",
            actor_identity_id=tipper_identity_id,
            organization_id="ORG-KARIS-RETAIL",
            correlation_id=tx_id,
            source_module="KARIS_LOOP_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "tip_id": tip_rec.tip_id,
                "post_id": post_id,
                "tipper_identity_id": tipper_identity_id,
                "creator_identity_id": creator_identity_id,
                "amount_krt": amount_krt,
                "reference_transaction_id": tx_id
            }
        )
        self.event_bus.publish(ev)

        return {
            "status": "TIP_SETTLED_SUCCESS",
            "tip_id": tip_rec.tip_id,
            "amount_krt_tipped": amount_krt,
            "creator_identity_id": creator_identity_id,
            "remaining_tipper_krt_balance": tipper_wallet.balance,
            "creator_new_krt_balance": creator_wallet.balance,
            "audit_hash": self.ledger_engine.last_hash
        }

    def checkout_shoppable_product(
        self,
        buyer_identity_id: str,
        post_id: str,
        linked_product_id: str,
        merchant_organization_id: str,
        amount_kes_or_krt: float,
        payment_method: str = "KRT_WALLET"
    ) -> Dict[str, Any]:
        """
        Direct shoppable checkout (`One Wallet Economy`).
        Reconciles KES or KRT via double-entry ledger (`Rule 5 & 9`) and awards `+5% KRT` loyalty reward (`Rule 7`)!
        """
        if amount_kes_or_krt <= 0:
            raise ValueError("Checkout amount must be greater than 0.")

        asset = AssetType.KRT if payment_method == "KRT_WALLET" else AssetType.KES
        w_type = WalletType.KRT_WALLET if asset == AssetType.KRT else WalletType.KES_WALLET

        buyer_wallet = self.wallet_engine.get_or_create_wallet(buyer_identity_id, merchant_organization_id, w_type, asset, 0.0)
        if buyer_wallet.balance < amount_kes_or_krt:
            raise ValueError(f"Insufficient balance in buyer wallet. Balance: {buyer_wallet.balance}, Required: {amount_kes_or_krt}")

        merchant_wallet = self.wallet_engine.get_or_create_wallet(merchant_organization_id, merchant_organization_id, w_type, asset, 0.0)

        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=asset,
            debit_wallet_id=buyer_wallet.wallet_id,
            credit_wallet_id=merchant_wallet.wallet_id,
            amount=amount_kes_or_krt,
            currency=asset.value,
            organization_id=merchant_organization_id,
            trigger_event_id=f"LOOP-BUY-{post_id[:8]}",
            description=f"Karis Loop Shoppable Checkout ({amount_kes_or_krt} {asset.value}) for product {linked_product_id}"
        )

        loyalty_krt = round(amount_kes_or_krt * 0.05, 4)
        if loyalty_krt > 0:
            treasury_w = self.wallet_engine.get_or_create_wallet("ORG-TREASURY-MAIN", merchant_organization_id, WalletType.RESERVE_WALLET, AssetType.KRT, 1000000.0)
            buyer_krt = self.wallet_engine.get_or_create_wallet(buyer_identity_id, merchant_organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)
            self.ledger_engine.record_transaction(
                transaction_id=str(uuid.uuid4()),
                asset_type=AssetType.KRT,
                debit_wallet_id=treasury_w.wallet_id,
                credit_wallet_id=buyer_krt.wallet_id,
                amount=loyalty_krt,
                currency="KRT",
                organization_id=merchant_organization_id,
                trigger_event_id=f"LOOP-LOYALTY-{post_id[:8]}",
                description=f"Karis Loop Shoppable Loyalty Reward (+5% KRT)"
            )

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="LOOP_SHOPPABLE_CHECKOUT_COMPLETED",
            event_category="SOCIAL",
            actor_identity_id=buyer_identity_id,
            organization_id=merchant_organization_id,
            correlation_id=tx_id,
            source_module="KARIS_LOOP_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "post_id": post_id,
                "buyer_identity_id": buyer_identity_id,
                "linked_product_id": linked_product_id,
                "merchant_organization_id": merchant_organization_id,
                "amount_kes_or_krt": amount_kes_or_krt,
                "payment_method": payment_method
            }
        )
        self.event_bus.publish(ev)

        return {
            "status": "SHOPPABLE_CHECKOUT_SUCCESS",
            "post_id": post_id,
            "linked_product_id": linked_product_id,
            "amount_paid": amount_kes_or_krt,
            "currency": asset.value,
            "loyalty_krt_reward_earned": loyalty_krt,
            "remaining_buyer_balance": buyer_wallet.balance,
            "audit_hash": self.ledger_engine.last_hash
        }

karis_loop_service = KarisLoopService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
