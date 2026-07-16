import threading
from typing import Dict, Optional
from src.domain.models import AssetType, WalletModel, WalletType

class MultiAssetWalletEngine:
    """
    KARIS OS™ Multi-Asset Wallet Engine.
    Enforces Rule 5: No Wallet directly edits another Wallet.
    All balance movements MUST be commanded by the Universal Ledger Engine after double-entry validation.
    """
    def __init__(self):
        # Key: wallet_id, Value: WalletModel
        self.wallets: Dict[str, WalletModel] = {}
        # Key: (identity_id, organization_id, wallet_type, asset_type), Value: wallet_id
        self.lookup_index: Dict[tuple, str] = {}
        self._lock = threading.Lock()

    def create_wallet(
        self,
        identity_id: str,
        organization_id: str,
        wallet_type: WalletType,
        asset_type: AssetType,
        initial_balance: float = 0.0
    ) -> WalletModel:
        with self._lock:
            key = (identity_id, organization_id, wallet_type, asset_type)
            if key in self.lookup_index:
                return self.wallets[self.lookup_index[key]]

            wallet = WalletModel(
                identity_id=identity_id,
                organization_id=organization_id,
                wallet_type=wallet_type,
                asset_type=asset_type,
                balance=initial_balance
            )
            self.wallets[wallet.wallet_id] = wallet
            self.lookup_index[key] = wallet.wallet_id
            return wallet

    def get_or_create_wallet(
        self,
        identity_id: str,
        organization_id: str,
        wallet_type: WalletType,
        asset_type: AssetType,
        initial_balance: float = 0.0
    ) -> WalletModel:
        return self.create_wallet(
            identity_id=identity_id,
            organization_id=organization_id,
            wallet_type=wallet_type,
            asset_type=asset_type,
            initial_balance=initial_balance
        )

    def get_wallet(self, wallet_id: str) -> Optional[WalletModel]:
        with self._lock:
            return self.wallets.get(wallet_id)

    def get_wallet_by_keys(
        self,
        identity_id: str,
        organization_id: str,
        wallet_type: WalletType,
        asset_type: AssetType
    ) -> Optional[WalletModel]:
        with self._lock:
            key = (identity_id, organization_id, wallet_type, asset_type)
            if key in self.lookup_index:
                return self.wallets[self.lookup_index[key]]
            return None

    def execute_ledger_movement(
        self,
        debit_wallet_id: str,
        credit_wallet_id: str,
        amount: float,
        caller_token: str
    ) -> tuple[WalletModel, WalletModel]:
        """
        Executes balance adjustments commanded strictly by the Universal Ledger Engine.
        Enforces Rule 5: Rejects unauthorized direct modifications.
        """
        if caller_token != "UNIVERSAL_LEDGER_ENGINE_AUTHORIZATION":
            raise PermissionError(
                "KARIS OS™ Rule 5 Violation: Wallets cannot be edited directly. "
                "Every transfer must occur through: Ledger -> Wallet Engine -> Settlement Engine."
            )

        if debit_wallet_id == credit_wallet_id:
            raise ValueError("KARIS OS™ Rule Violation: Debit and Credit wallet IDs must be distinct.")

        with self._lock:
            debit_wallet = self.wallets.get(debit_wallet_id)
            credit_wallet = self.wallets.get(credit_wallet_id)

            if not debit_wallet or not credit_wallet:
                raise KeyError("Specified Debit or Credit wallet does not exist in the Wallet Engine.")

            if debit_wallet.asset_type != credit_wallet.asset_type:
                raise ValueError(
                    f"Asset type mismatch: cannot transfer directly from {debit_wallet.asset_type} "
                    f"to {credit_wallet.asset_type} without going through the Exchange Engine."
                )

            if debit_wallet.balance < amount:
                raise ValueError(
                    f"Insufficient balance in debit wallet {debit_wallet_id}: "
                    f"Balance {debit_wallet.balance}, Requested Debit {amount}"
                )

            debit_wallet.balance -= amount
            credit_wallet.balance += amount
            return debit_wallet, credit_wallet

# Global Singleton for system simulation
wallet_engine = MultiAssetWalletEngine()
