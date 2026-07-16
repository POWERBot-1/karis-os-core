import pytest
from datetime import datetime, timezone
import uuid
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType
from src.verticals.karis_expansion_suite.service import KarisExpansionSuiteService

@pytest.fixture
def expsuite_env():
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0" * 64
    event_bus.event_store.clear()

    # Initialize Treasury reserve
    treasury = wallet_engine.get_or_create_wallet("ORG-TREASURY-MAIN", "ORG-KARIS-PROP", WalletType.RESERVE_WALLET, AssetType.KRT, 1000000.0)
    svc = KarisExpansionSuiteService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
    return svc, event_bus, ledger_engine, wallet_engine

def test_karis_pharma_trace_cold_chain_breach_detection(expsuite_env):
    svc, eb, le, we = expsuite_env

    # 1. Log Pharma Cold-Chain Batch (`2°C to 8°C max limit`)
    batch = svc.log_pharma_batch("PROD-INSULIN-01", "ORG-HEALTH-CLINIC", 2.0, 8.0)
    assert batch.storage_max_celsius == 8.0
    assert batch.status == "SAFE_COLD_CHAIN"

    # 2. Log Telemetry Breach (`10.5°C > 8.0°C`)
    tel_res = svc.log_pharma_temperature_telemetry(batch.batch_id, 10.5)
    assert tel_res["cold_chain_breached"] is True
    assert tel_res["status"] == "COLD_CHAIN_BREACHED_LOCKED"
    assert batch.status == "COLD_CHAIN_BREACHED_LOCKED"

    # Verify EXPSUITE_PHARMA_COLD_CHAIN_BREACHED event published
    breach_events = [e for e in eb.event_store if e.event_type == "EXPSUITE_PHARMA_COLD_CHAIN_BREACHED"]
    assert len(breach_events) == 1
    assert breach_events[0].payload["temperature_celsius"] == 10.5

def test_karis_prop_share_and_edu_pay_double_entry_settlement(expsuite_env):
    svc, eb, le, we = expsuite_env

    # 1. Prop-Share Syndication & Dividend Distribution (`Rule 5 & Rule 9`)
    synd = svc.create_syndication("ORG-KARIS-PROP", "Machakos Commercial Hub", "Machakos County", 1000, 10000.0)
    alloc = svc.allocate_shares(synd.syndication_id, "USER-INV-KAMAU", 100)  # 10% ownership
    assert alloc.shares_owned == 100

    div_res = svc.distribute_monthly_rental_dividends(synd.syndication_id, 100000.0)
    assert div_res["investor_payouts_count"] == 1
    assert div_res["payouts"][0]["dividend_krt"] == 10000.0  # 10% of 100k
    assert alloc.total_dividends_earned_kes == 10000.0

    inv_wallet = we.get_wallet_by_keys("USER-INV-KAMAU", "ORG-KARIS-PROP", WalletType.KRT_WALLET, AssetType.KRT)
    assert inv_wallet.balance == 10000.0

    # 2. Edu-Pay Tuition Plan & Installment Payment (`Rule 7 & Rule 9`)
    plan = svc.create_tuition_plan("USER-STUDENT-01", "ORG-COLLEGE-MACHAKOS", "Term 3 2026", 45000.0)
    inst_res = svc.pay_tuition_installment(plan.plan_id, "USER-PARENT-01", 15000.0)
    assert inst_res["paid_amount_kes"] == 15000.0
    assert inst_res["remaining_tuition_kes"] == 30000.0
    assert inst_res["bonus_krt_awarded"] == 150.0

    student_krt = we.get_wallet_by_keys("USER-STUDENT-01", "ORG-COLLEGE-MACHAKOS", WalletType.KRT_WALLET, AssetType.KRT)
    assert student_krt.balance == 150.0
