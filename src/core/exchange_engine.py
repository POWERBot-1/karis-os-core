import uuid
from typing import Dict
from src.config import config
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine

class MultiAssetExchangeEngine:
    """
    KARIS OS™ Multi-Asset Exchange Engine.
    Enforces Section 4 (Digital Economy Layer) & Section 6 (Exchange Engine).
    Handles KES <-> KRT, LOYLTY -> KRT, and Credit redemptions while strictly passing all movements through Universal Ledger Engine (Rule 5).
    """
    def __init__(self):
        # Exchange rates relative to KES (1.0 KES base)
        self.rates: Dict[AssetType, float] = {
            AssetType.KES: 1.0,
            AssetType.KRT: config.KRT_KES_EXCHANGE_RATE,  # 1 KRT = 1 KES default
            AssetType.LOYALTY: 0.10,                     # 10 Loyalty Points = 1 KES equivalent
        }

    def execute_exchange(
        self,
        identity_id: str,
        organization_id: str,
        from_asset: AssetType,
        to_asset: AssetType,
        from_amount: float
    ) -> Dict:
        if from_amount <= 0:
            raise ValueError("Exchange amount must be greater than zero.")
        if from_asset == to_asset:
            raise ValueError("Source and destination asset types must be different.")

        from_rate = self.rates.get(from_asset, 1.0)
        to_rate = self.rates.get(to_asset, 1.0)
        
        # Calculate destination amount based on exchange rate
        kes_value = from_amount * from_rate
        to_amount = round(kes_value / to_rate, 4)

        # Lookup source and target wallets for the user
        from_wallet = wallet_engine.get_wallet_by_keys(
            identity_id=identity_id,
            organization_id=organization_id,
            wallet_type=self._asset_to_wallet_type(from_asset),
            asset_type=from_asset
        )
        to_wallet = wallet_engine.get_wallet_by_keys(
            identity_id=identity_id,
            organization_id=organization_id,
            wallet_type=self._asset_to_wallet_type(to_asset),
            asset_type=to_asset
        )

        # Lookup Treasury exchange pool wallets
        treasury_from_pool = wallet_engine.get_wallet_by_keys(
            identity_id="TREASURY_IDENTITY",
            organization_id=organization_id,
            wallet_type=WalletType.RESERVE_WALLET if from_asset == AssetType.KES else WalletType.REWARD_POOL,
            asset_type=from_asset
        )
        treasury_to_pool = wallet_engine.get_wallet_by_keys(
            identity_id="TREASURY_IDENTITY",
            organization_id=organization_id,
            wallet_type=WalletType.RESERVE_WALLET if to_asset == AssetType.KES else WalletType.REWARD_POOL,
            asset_type=to_asset
        )

        if not from_wallet or not to_wallet or not treasury_from_pool or not treasury_to_pool:
            raise KeyError("One or more required exchange wallets or treasury pools do not exist.")

        if from_wallet.balance < from_amount:
            raise ValueError(f"Insufficient balance in {from_asset.value} wallet for exchange.")

        exchange_tx_id = str(uuid.uuid4())

        # Leg 1: Debit User From-Wallet -> Credit Treasury Pool (via Ledger Engine)
        ledger_engine.record_transaction(
            transaction_id=str(uuid.uuid4()),
            asset_type=from_asset,
            debit_wallet_id=from_wallet.wallet_id,
            credit_wallet_id=treasury_from_pool.wallet_id,
            amount=from_amount,
            currency=from_asset.value,
            organization_id=organization_id,
            trigger_event_id=exchange_tx_id,
            description=f"Exchange Leg 1: User deposited {from_amount} {from_asset.value} into Treasury"
        )

        # Leg 2: Debit Treasury Pool -> Credit User To-Wallet (via Ledger Engine)
        ledger_engine.record_transaction(
            transaction_id=str(uuid.uuid4()),
            asset_type=to_asset,
            debit_wallet_id=treasury_to_pool.wallet_id,
            credit_wallet_id=to_wallet.wallet_id,
            amount=to_amount,
            currency=to_asset.value,
            organization_id=organization_id,
            trigger_event_id=exchange_tx_id,
            description=f"Exchange Leg 2: Treasury disbursed {to_amount} {to_asset.value} to User"
        )

        # Publish Exchange Event
        ev = EventPayload(
            event_type="ASSET_EXCHANGED",
            event_category=EventCategory.CURRENCY,
            actor_identity_id=identity_id,
            organization_id=organization_id,
            correlation_id=exchange_tx_id,
            source_module="EXCHANGE_ENGINE",
            payload={
                "exchange_id": exchange_tx_id,
                "identity_id": identity_id,
                "from_asset": from_asset.value,
                "to_asset": to_asset.value,
                "from_amount": from_amount,
                "to_amount": to_amount,
                "exchange_rate": round(from_rate / to_rate, 6)
            }
        )
        event_bus.publish(ev)

        return {
            "status": "SUCCESS",
            "exchange_id": exchange_tx_id,
            "from_asset": from_asset.value,
            "from_amount": from_amount,
            "to_asset": to_asset.value,
            "to_amount": to_amount,
            "new_from_balance": from_wallet.balance,
            "new_to_balance": to_wallet.balance
        }

    def _asset_to_wallet_type(self, asset: AssetType) -> WalletType:
        if asset == AssetType.KES:
            return WalletType.KES_WALLET
        elif asset == AssetType.KRT:
            return WalletType.KRT_WALLET
        elif asset == AssetType.LOYALTY:
            return WalletType.LOYALTY_WALLET
        elif asset == AssetType.CREDIT:
            return WalletType.CREDIT_WALLET
        return WalletType.INVESTMENT_WALLET

exchange_engine = MultiAssetExchangeEngine()
