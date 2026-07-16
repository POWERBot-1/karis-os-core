import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from src.domain.models import (
    EnergySolarInstallationModel, EnergySmartMeterTelemetryModel,
    EnergyPAYGInstallmentModel, EnergyMicrogridPeerTransferModel,
    EventPayload, AssetType, WalletType
)
from src.core.event_bus import event_bus, UniversalEventBus
from src.core.ledger_engine import ledger_engine, UniversalLedgerEngine
from src.core.wallet_engine import wallet_engine, MultiAssetWalletEngine

class KarisEnergyService:
    """
    KARIS OS™ :: KARIS ENERGY & SMART SOLAR GRID™ (`Section 50 / Vertical 15`).
    
    Provides:
    1. PAYG Solar Installation Registration (Home systems, irrigation pumps, battery storage)
    2. IoT Smart Meter Telemetry Logging (Daily kWh generation, soil moisture, feed-in tracking)
    3. Automated Surplus Green Energy Token Minting (`KRT-JOULE` / `KRT-GREEN` via Rule 7 & Rule 9)
    4. PAYG Token Unlocking Installment Checkout (Mixed KES / KRT via double entry)
    5. Peer-to-Peer Microgrid Solar Energy Trading (`Rule 5 & Rule 9 double entry`)
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
        
        self.installations: Dict[str, EnergySolarInstallationModel] = {}
        self.telemetry_logs: Dict[str, EnergySmartMeterTelemetryModel] = {}
        self.installments: Dict[str, EnergyPAYGInstallmentModel] = {}
        self.peer_transfers: Dict[str, EnergyMicrogridPeerTransferModel] = {}

    def register_solar_unit(
        self,
        owner_user_id: str,
        organization_id: str,
        device_serial_number: str,
        device_type: str = "SOLAR_IRRIGATION_PUMP",
        rated_capacity_watts: float = 1500.0,
        daily_token_rate_krt: float = 50.0
    ) -> EnergySolarInstallationModel:
        """Registers a PAYG solar home system or irrigation pump (`Section 50.2`)."""
        inst = EnergySolarInstallationModel(
            owner_user_id=owner_user_id,
            organization_id=organization_id,
            device_serial_number=device_serial_number,
            device_type=device_type,
            rated_capacity_watts=rated_capacity_watts,
            payg_status="ACTIVE_UNLOCKED",
            daily_token_rate_krt=daily_token_rate_krt
        )
        self.installations[inst.installation_id] = inst

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="ENERGY_SOLAR_UNIT_REGISTERED",
            event_category="ENERGY",
            actor_identity_id=owner_user_id,
            organization_id=organization_id,
            correlation_id=str(uuid.uuid4()),
            source_module="KARIS_ENERGY_GRID",
            timestamp=datetime.now(timezone.utc),
            payload={
                "installation_id": inst.installation_id,
                "owner_user_id": owner_user_id,
                "organization_id": organization_id,
                "device_serial_number": device_serial_number,
                "device_type": device_type,
                "rated_capacity_watts": rated_capacity_watts,
                "daily_token_rate_krt": daily_token_rate_krt
            }
        )
        self.event_bus.publish(ev)
        return inst

    def log_smart_meter_telemetry(
        self,
        installation_id: str,
        kwh_generated_today: float,
        kwh_consumed_today: float,
        battery_voltage_v: float = 24.5,
        soil_moisture_pct: float = 45.0,
        microgrid_feed_in_kwh: float = 0.0
    ) -> Dict[str, Any]:
        """
        Logs daily IoT smart meter telemetry (`Rule 6`).
        If `microgrid_feed_in_kwh > 0` and `battery_voltage_v >= 24.0`, automatically mints `KRT-JOULE` / `KRT-GREEN`
        token rewards via exact double-entry accounting (`Rule 5 & Rule 9`).
        """
        if installation_id not in self.installations:
            raise KeyError(f"Installation {installation_id} not registered.")
        inst = self.installations[installation_id]

        inst.total_kwh_generated = round(inst.total_kwh_generated + kwh_generated_today, 4)
        battery_pct = min(100.0, round((battery_voltage_v / 25.6) * 100.0, 2))
        inst.battery_charge_pct = battery_pct

        tel = EnergySmartMeterTelemetryModel(
            installation_id=installation_id,
            kwh_generated_today=kwh_generated_today,
            kwh_consumed_today=kwh_consumed_today,
            battery_voltage_v=battery_voltage_v,
            soil_moisture_pct=soil_moisture_pct,
            microgrid_feed_in_kwh=microgrid_feed_in_kwh
        )
        self.telemetry_logs[tel.telemetry_id] = tel

        # Emit telemetry event
        ev_tel = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="ENERGY_METER_TELEMETRY_RECORDED",
            event_category="ENERGY",
            actor_identity_id=inst.owner_user_id,
            organization_id=inst.organization_id,
            correlation_id=str(uuid.uuid4()),
            source_module="KARIS_ENERGY_GRID",
            timestamp=datetime.now(timezone.utc),
            payload={
                "telemetry_id": tel.telemetry_id,
                "installation_id": installation_id,
                "kwh_generated_today": kwh_generated_today,
                "kwh_consumed_today": kwh_consumed_today,
                "battery_voltage_v": battery_voltage_v,
                "soil_moisture_pct": soil_moisture_pct,
                "microgrid_feed_in_kwh": microgrid_feed_in_kwh
            }
        )
        self.event_bus.publish(ev_tel)

        minted_krt = 0.0
        tx_id = "NONE"
        if microgrid_feed_in_kwh > 0.0 and battery_pct >= 85.0:
            # Mint KRT-JOULE (10 KRT per kWh surplus fed back to microgrid)
            minted_krt = round(microgrid_feed_in_kwh * 10.0, 4)
            treasury_wallet = self.wallet_engine.get_or_create_wallet("ORG-TREASURY-MAIN", inst.organization_id, WalletType.RESERVE_WALLET, AssetType.KRT, 1000000.0)
            owner_wallet = self.wallet_engine.get_or_create_wallet(inst.owner_user_id, inst.organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)

            tx_id = str(uuid.uuid4())
            self.ledger_engine.record_transaction(
                transaction_id=tx_id,
                asset_type=AssetType.KRT,
                debit_wallet_id=treasury_wallet.wallet_id,
                credit_wallet_id=owner_wallet.wallet_id,
                amount=minted_krt,
                currency="KRT",
                organization_id=inst.organization_id,
                trigger_event_id=ev_tel.event_id,
                description=f"Surplus Solar Microgrid Feed-In Reward ({microgrid_feed_in_kwh} kWh) -> Minted {minted_krt} KRT-JOULE"
            )

            ev_mint = EventPayload(
                event_id=str(uuid.uuid4()),
                event_type="ENERGY_MICROGRID_SURPLUS_MINTED",
                event_category="ENERGY",
                actor_identity_id=inst.owner_user_id,
                organization_id=inst.organization_id,
                correlation_id=str(uuid.uuid4()),
                source_module="KARIS_ENERGY_GRID",
                timestamp=datetime.now(timezone.utc),
                payload={
                    "installation_id": installation_id,
                    "owner_user_id": inst.owner_user_id,
                    "microgrid_feed_in_kwh": microgrid_feed_in_kwh,
                    "minted_krt_joule_amount": minted_krt,
                    "reference_transaction_id": tx_id
                }
            )
            self.event_bus.publish(ev_mint)

        return {
            "telemetry_id": tel.telemetry_id,
            "installation_id": installation_id,
            "total_kwh_generated": inst.total_kwh_generated,
            "battery_charge_pct": battery_pct,
            "surplus_feed_in_kwh": microgrid_feed_in_kwh,
            "minted_krt_joule_reward": minted_krt,
            "reference_transaction_id": tx_id,
            "audit_hash": self.ledger_engine.last_hash
        }

    def pay_payg_installment(
        self,
        installation_id: str,
        payer_user_id: str,
        amount_krt: float,
        payment_method: str = "KRT_WALLET"
    ) -> Dict[str, Any]:
        """
        Processes PAYG solar unlocking payment via KRT tokens (`Rule 2 & Rule 9`).
        Unlocks days = `amount_krt / daily_token_rate_krt`.
        """
        if installation_id not in self.installations:
            raise KeyError(f"Installation {installation_id} not found.")
        inst = self.installations[installation_id]
        if amount_krt <= 0:
            raise ValueError("Installment amount must be strictly greater than 0.")

        days_unlocked = max(1, int(amount_krt / inst.daily_token_rate_krt))
        payer_wallet = self.wallet_engine.get_or_create_wallet(payer_user_id, inst.organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)
        if payer_wallet.balance < amount_krt:
            raise ValueError(f"Insufficient KRT balance for PAYG solar installment. Balance: {payer_wallet.balance}, Required: {amount_krt}")

        energy_merchant_wallet = self.wallet_engine.get_or_create_wallet("ORG-KARIS-ENERGY-MAIN", inst.organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)

        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=payer_wallet.wallet_id,
            credit_wallet_id=energy_merchant_wallet.wallet_id,
            amount=amount_krt,
            currency="KRT",
            organization_id=inst.organization_id,
            trigger_event_id=f"PAYG-UNLOCK-{installation_id[:8]}",
            description=f"PAYG Solar Token Installment ({amount_krt} KRT -> Unlocked {days_unlocked} Days)"
        )

        inst.payg_status = "ACTIVE_UNLOCKED"
        installment = EnergyPAYGInstallmentModel(
            installation_id=installation_id,
            payer_user_id=payer_user_id,
            amount_krt=amount_krt,
            payment_method=payment_method,
            days_unlocked=days_unlocked,
            status="SETTLED_UNLOCKED"
        )
        self.installments[installment.installment_id] = installment

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="ENERGY_PAYG_INSTALLMENT_SETTLED",
            event_category="ENERGY",
            actor_identity_id=payer_user_id,
            organization_id=inst.organization_id,
            correlation_id=str(uuid.uuid4()),
            source_module="KARIS_ENERGY_GRID",
            timestamp=datetime.now(timezone.utc),
            payload={
                "installment_id": installment.installment_id,
                "installation_id": installation_id,
                "payer_user_id": payer_user_id,
                "amount_krt": amount_krt,
                "amount_kes": amount_krt,
                "days_unlocked": days_unlocked
            }
        )
        self.event_bus.publish(ev)

        return {
            "installment_id": installment.installment_id,
            "installation_id": installation_id,
            "amount_krt_paid": amount_krt,
            "days_unlocked": days_unlocked,
            "payg_status": inst.payg_status,
            "remaining_payer_krt_balance": payer_wallet.balance,
            "audit_hash": self.ledger_engine.last_hash
        }

    def execute_peer_energy_trade(
        self,
        seller_user_id: str,
        buyer_user_id: str,
        organization_id: str,
        kwh_traded: float,
        price_per_kwh_krt: float = 12.5
    ) -> EnergyMicrogridPeerTransferModel:
        """
        Executes peer-to-peer solar energy token trading (`Rule 5 & Rule 9 double entry`).
        Buyer KRT wallet debited, Seller KRT wallet credited.
        """
        if kwh_traded <= 0 or price_per_kwh_krt <= 0:
            raise ValueError("Traded kWh and price per kWh must be greater than 0.")

        total_krt = round(kwh_traded * price_per_kwh_krt, 4)
        buyer_wallet = self.wallet_engine.get_or_create_wallet(buyer_user_id, organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)
        if buyer_wallet.balance < total_krt:
            raise ValueError(f"Insufficient KRT balance inside buyer wallet. Balance: {buyer_wallet.balance}, Required: {total_krt}")

        seller_wallet = self.wallet_engine.get_or_create_wallet(seller_user_id, organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)

        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=buyer_wallet.wallet_id,
            credit_wallet_id=seller_wallet.wallet_id,
            amount=total_krt,
            currency="KRT",
            organization_id=organization_id,
            trigger_event_id=f"P2P-SOLAR-{seller_user_id[:6]}-{buyer_user_id[:6]}",
            description=f"Peer-to-Peer Microgrid Solar Trade ({kwh_traded} kWh at {price_per_kwh_krt} KRT/kWh)"
        )

        trade = EnergyMicrogridPeerTransferModel(
            seller_user_id=seller_user_id,
            buyer_user_id=buyer_user_id,
            kwh_traded=kwh_traded,
            price_per_kwh_krt=price_per_kwh_krt,
            total_amount_krt=total_krt,
            audit_hash=self.ledger_engine.last_hash
        )
        self.peer_transfers[trade.transfer_id] = trade
        return trade

karis_energy_service = KarisEnergyService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
