import pytest
from datetime import datetime, timezone
import uuid
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType
from src.verticals.karis_energy.service import KarisEnergyService

@pytest.fixture
def energy_grid_env():
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0" * 64
    event_bus.event_store.clear()

    # Initialize Treasury and Energy Merchant wallets
    treasury = wallet_engine.get_or_create_wallet("ORG-TREASURY-MAIN", "ORG-KARIS-FARM-MAIN", WalletType.RESERVE_WALLET, AssetType.KRT, 1000000.0)
    energy_merchant = wallet_engine.get_or_create_wallet("ORG-KARIS-ENERGY-MAIN", "ORG-KARIS-FARM-MAIN", WalletType.KRT_WALLET, AssetType.KRT, 0.0)

    svc = KarisEnergyService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
    svc.treasury_id = treasury.wallet_id
    svc.merchant_id = energy_merchant.wallet_id
    return svc, event_bus, ledger_engine, wallet_engine

def test_karis_energy_solar_registration_and_telemetry_surplus_minting(energy_grid_env):
    svc, eb, le, we = energy_grid_env

    # 1. Register PAYG Solar Irrigation Pump
    inst = svc.register_solar_unit("USER-FARMER-KAMAU", "ORG-KARIS-FARM-MAIN", "SN-SOLAR-PUMP-2026-9901", "SOLAR_IRRIGATION_PUMP", 1500.0, 50.0)
    assert inst.device_serial_number == "SN-SOLAR-PUMP-2026-9901"
    assert inst.daily_token_rate_krt == 50.0

    # Verify ENERGY_SOLAR_UNIT_REGISTERED event
    reg_events = [e for e in eb.event_store if e.event_type == "ENERGY_SOLAR_UNIT_REGISTERED"]
    assert len(reg_events) == 1

    # 2. Log Telemetry with microgrid feed-in (2.40 kWh surplus -> auto-mints +24.0 KRT-JOULE)
    tel_res = svc.log_smart_meter_telemetry(inst.installation_id, 6.85, 4.45, 25.2, 48.0, 2.40)
    assert tel_res["minted_krt_joule_reward"] == round(2.40 * 10.0, 4)
    assert tel_res["audit_hash"] != "0" * 64

    # Verify Farmer KRT balance credited (+24.0 KRT) via double-entry
    farmer_wallet = we.get_wallet_by_keys("USER-FARMER-KAMAU", "ORG-KARIS-FARM-MAIN", WalletType.KRT_WALLET, AssetType.KRT)
    assert farmer_wallet is not None
    assert farmer_wallet.balance == 24.0

    # Verify events
    assert any(e.event_type == "ENERGY_METER_TELEMETRY_RECORDED" for e in eb.event_store)
    assert any(e.event_type == "ENERGY_MICROGRID_SURPLUS_MINTED" for e in eb.event_store)

def test_karis_energy_payg_installment_and_peer_microgrid_trade(energy_grid_env):
    svc, eb, le, we = energy_grid_env
    inst = svc.register_solar_unit("USER-FARMER-KAMAU", "ORG-KARIS-FARM-MAIN", "SN-SOLAR-HOME-2026-8802", "SOLAR_HOME_SYSTEM", 800.0, 30.0)

    # Fund Farmer wallet with 300 KRT
    farmer_wallet = we.get_or_create_wallet("USER-FARMER-KAMAU", "ORG-KARIS-FARM-MAIN", WalletType.KRT_WALLET, AssetType.KRT, 300.0)

    # 1. Pay PAYG Solar Installment (150 KRT / 30 KRT/day = 5 Days Unlocked)
    payg_res = svc.pay_payg_installment(inst.installation_id, "USER-FARMER-KAMAU", 150.0, "KRT_WALLET")
    assert payg_res["days_unlocked"] == 5
    assert payg_res["remaining_payer_krt_balance"] == 150.0  # 300 - 150

    # Verify ENERGY_PAYG_INSTALLMENT_SETTLED event
    payg_events = [e for e in eb.event_store if e.event_type == "ENERGY_PAYG_INSTALLMENT_SETTLED"]
    assert len(payg_events) == 1

    # 2. Execute Peer-to-Peer Microgrid Solar Trade (Farmer sells 10 kWh to Clinic at 12 KRT/kWh = 120 KRT)
    clinic_wallet = we.get_or_create_wallet("USER-CLINIC-MACHAKOS", "ORG-KARIS-FARM-MAIN", WalletType.KRT_WALLET, AssetType.KRT, 200.0)

    trade = svc.execute_peer_energy_trade("USER-FARMER-KAMAU", "USER-CLINIC-MACHAKOS", "ORG-KARIS-FARM-MAIN", 10.0, 12.0)
    assert trade.total_amount_krt == 120.0
    assert clinic_wallet.balance == 80.0  # 200 - 120
    assert farmer_wallet.balance == 270.0 # 150 + 120
