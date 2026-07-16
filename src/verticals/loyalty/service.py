import uuid
from typing import Dict
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine

class LoyaltyIncentiveEngine:
    """
    KARIS OS™ Loyalty & Incentive Engine (Section 26).
    Manages promotional campaigns, reward tiers, and incentive distributions across all stakeholders.
    """
    def __init__(self):
        self.campaigns: Dict[str, Dict] = {}

    def create_campaign(
        self,
        organization_id: str,
        campaign_code: str,
        campaign_name: str,
        target_stakeholder: str = "ALL",
        reward_type: str = "KARIS_TOKENS_KRT",
        multiplier: float = 2.0,
        fixed_bonus: float = 50.0
    ) -> Dict:
        camp = {
            "campaign_id": str(uuid.uuid4()),
            "organization_id": organization_id,
            "campaign_code": campaign_code,
            "campaign_name": campaign_name,
            "target_stakeholder_type": target_stakeholder,
            "reward_type": reward_type,
            "reward_multiplier": multiplier,
            "bonus_fixed_amount": fixed_bonus,
            "is_active": True
        }
        self.campaigns[camp["campaign_id"]] = camp
        return camp

    def grant_campaign_reward(
        self,
        campaign_id: str,
        recipient_identity_id: str,
        organization_id: str,
        trigger_reason: str,
        base_amount: float = 100.0
    ) -> Dict:
        if campaign_id not in self.campaigns:
            raise KeyError(f"Campaign ID {campaign_id} not found.")

        camp = self.campaigns[campaign_id]
        if not camp["is_active"]:
            raise ValueError(f"Campaign {camp['campaign_name']} is currently inactive.")

        reward_amount = round(base_amount * camp["reward_multiplier"] + camp["bonus_fixed_amount"], 4)
        asset = AssetType.KRT if camp["reward_type"] == "KARIS_TOKENS_KRT" else AssetType.LOYALTY
        w_type = WalletType.KRT_WALLET if asset == AssetType.KRT else WalletType.LOYALTY_WALLET

        recipient_wallet = wallet_engine.get_wallet_by_keys(recipient_identity_id, organization_id, w_type, asset)
        if not recipient_wallet:
            recipient_wallet = wallet_engine.create_wallet(recipient_identity_id, organization_id, w_type, asset, 0.0)

        treasury_pool = wallet_engine.get_wallet_by_keys("TREASURY_IDENTITY", organization_id, WalletType.REWARD_POOL, asset)
        if not treasury_pool:
            treasury_pool = wallet_engine.create_wallet("TREASURY_IDENTITY", organization_id, WalletType.REWARD_POOL, asset, 1_000_000.0)

        tx_id = str(uuid.uuid4())
        ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=asset,
            debit_wallet_id=treasury_pool.wallet_id,
            credit_wallet_id=recipient_wallet.wallet_id,
            amount=reward_amount,
            currency=asset.value,
            organization_id=organization_id,
            trigger_event_id=tx_id,
            description=f"Promotional Campaign Reward ({camp['campaign_name']}) for {trigger_reason}"
        )

        ev = EventPayload(
            event_type="LOYALTY_BONUS_GRANTED",
            event_category=EventCategory.TREASURY,
            actor_identity_id="LOYALTY_SYSTEM",
            organization_id=organization_id,
            correlation_id=tx_id,
            source_module="LOYALTY_INCENTIVE_ENGINE",
            payload={
                "grant_id": str(uuid.uuid4()),
                "campaign_id": campaign_id,
                "recipient_identity_id": recipient_identity_id,
                "reward_type": camp["reward_type"],
                "points_or_tokens_awarded": reward_amount,
                "trigger_reason": trigger_reason
            }
        )
        event_bus.publish(ev)

        return {
            "status": "SUCCESS",
            "campaign_name": camp["campaign_name"],
            "recipient_identity_id": recipient_identity_id,
            "reward_awarded": reward_amount,
            "reward_asset": asset.value
        }

loyalty_engine = LoyaltyIncentiveEngine()
