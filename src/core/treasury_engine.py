import uuid
from typing import Dict
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine

class TreasuryEngine:
    """
    KARIS OS™ Treasury Engine.
    Enforces Section 12 (Treasury Engine) & Section 18 (KRT Economy Controls).
    Governs platform liquidity, KRT token supply caps, reserve ratios, and reward pool rebalancing.
    """
    def __init__(self):
        self.krt_max_supply: float = 10_000_000.0  # 10 Million KRT token cap
        self.krt_circulating_supply: float = 500_000.0
        self.target_reserve_ratio_pct: float = 20.0 # 20% fiat backing reserve ratio

    def get_treasury_health(self, organization_id: str) -> Dict:
        reserve_kes = wallet_engine.get_wallet_by_keys("TREASURY_IDENTITY", organization_id, WalletType.RESERVE_WALLET, AssetType.KES)
        reward_krt = wallet_engine.get_wallet_by_keys("TREASURY_IDENTITY", organization_id, WalletType.REWARD_POOL, AssetType.KRT)
        
        kes_bal = reserve_kes.balance if reserve_kes else 0.0
        krt_bal = reward_krt.balance if reward_krt else 0.0

        reserve_ratio = round((kes_bal / max(self.krt_circulating_supply, 1.0)) * 100, 2)
        status = "HEALTHY" if reserve_ratio >= self.target_reserve_ratio_pct else "REBALANCING_REQUIRED"

        return {
            "organization_id": organization_id,
            "treasury_reserve_kes": kes_bal,
            "reward_pool_krt": krt_bal,
            "circulating_krt_supply": self.krt_circulating_supply,
            "max_krt_supply_cap": self.krt_max_supply,
            "current_reserve_ratio_pct": reserve_ratio,
            "target_reserve_ratio_pct": self.target_reserve_ratio_pct,
            "treasury_status": status
        }

    def rebalance_pools(self, organization_id: str, amount_kes: float) -> Dict:
        """Transfers liquidity from Reserve Wallet to Operations/Reward Pools."""
        reserve_kes = wallet_engine.get_wallet_by_keys("TREASURY_IDENTITY", organization_id, WalletType.RESERVE_WALLET, AssetType.KES)
        operations_kes = wallet_engine.get_wallet_by_keys("OPERATIONS_IDENTITY", organization_id, WalletType.RESERVE_WALLET, AssetType.KES)

        if not reserve_kes or not operations_kes:
            raise KeyError("Treasury or Operations reserve wallets do not exist.")

        tx_id = str(uuid.uuid4())
        ledger_engine.record_transaction(
            transaction_id=str(uuid.uuid4()),
            asset_type=AssetType.KES,
            debit_wallet_id=reserve_kes.wallet_id,
            credit_wallet_id=operations_kes.wallet_id,
            amount=amount_kes,
            currency="KES",
            organization_id=organization_id,
            trigger_event_id=tx_id,
            description=f"Treasury Liquidity Rebalance of KES {amount_kes:,.2f}"
        )

        ev = EventPayload(
            event_type="TREASURY_REBALANCED",
            event_category=EventCategory.TREASURY,
            actor_identity_id="TREASURY_ENGINE",
            organization_id=organization_id,
            correlation_id=tx_id,
            source_module="TREASURY_ENGINE",
            payload={
                "amount_rebalanced_kes": amount_kes,
                "new_reserve_kes": reserve_kes.balance,
                "new_operations_kes": operations_kes.balance
            }
        )
        event_bus.publish(ev)
        return {"status": "SUCCESS", "message": "Treasury successfully rebalanced."}

treasury_engine = TreasuryEngine()
