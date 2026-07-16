import pytest
from datetime import datetime, timezone
import uuid
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.core.rule_engine import rule_engine
from src.domain.models import AssetType, WalletType
from src.integrations.payment_links import PaymentLinkCheckoutEngine

@pytest.fixture
def palplus_env():
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0" * 64
    event_bus.event_store.clear()

    # Initialize Treasury, Reward Pool, Supplier and Customer wallets
    treasury = wallet_engine.get_or_create_wallet("TREASURY_IDENTITY", "ORG-KARIS-RETAIL", WalletType.RESERVE_WALLET, AssetType.KRT, 1000000.0)
    reward_pool = wallet_engine.get_or_create_wallet("TREASURY_IDENTITY", "ORG-KARIS-RETAIL", WalletType.REWARD_POOL, AssetType.KRT, 500000.0)
    supplier_kes = wallet_engine.get_or_create_wallet("268e1e85-a0b3-445d-827b-98e327af3bee", "ORG-KARIS-RETAIL", WalletType.KES_WALLET, AssetType.KES, 0.0)
    customer_kes = wallet_engine.get_or_create_wallet("USER-AMINA-777", "ORG-KARIS-RETAIL", WalletType.KES_WALLET, AssetType.KES, 10000.0)
    customer_krt = wallet_engine.get_or_create_wallet("USER-AMINA-777", "ORG-KARIS-RETAIL", WalletType.KRT_WALLET, AssetType.KRT, 50.0)

    engine = PaymentLinkCheckoutEngine()
    return engine, event_bus, ledger_engine, wallet_engine

def test_palplus_payment_link_package_and_webhook_reconciliation(palplus_env):
    engine, eb, le, we = palplus_env

    # 1. Verify exact existing temporary link registration
    link = engine.get_or_register_payment_link()
    assert link.payment_link_id == "6e8de0bc-1284-4bba-a5de-f886665bf18f"
    assert link.external_link_url == "https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f"

    # 2. Generate Checkout Package for Order
    pkg = engine.generate_checkout_package("ORDER-9901", 3500.0, "USER-AMINA-777")
    assert pkg["payment_link_url"] == "https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f"
    assert "ORDER-9901" in pkg["qr_code_payload"]

    # 3. Process incoming PalPlus Webhook (Customer paid KES 3,500 via M-Pesa Express on PalPlus link)
    res = engine.process_palplus_webhook(
        payment_link_id="6e8de0bc-1284-4bba-a5de-f886665bf18f",
        payer_identity_id="USER-AMINA-777",
        amount_kes=3500.0,
        external_receipt_number="PALPLUS-RC-77112",
        organization_id="ORG-KARIS-RETAIL",
        target_order_id="ORDER-9901"
    )

    assert res["status"] == "SUCCESS"
    assert res["reconciled_amount_kes"] == 3500.0
    assert res["loyalty_krt_earned"] == round(3500.0 * 0.05, 4)  # 175 KRT
    assert res["audit_hash"] != "0" * 64

    # Verify Customer KES debited via double-entry accounting
    cust_kes = we.get_wallet_by_keys("USER-AMINA-777", "ORG-KARIS-RETAIL", WalletType.KES_WALLET, AssetType.KES)
    assert cust_kes.balance == 6500.0  # 10000 - 3500

    # Verify Customer KRT credited (+175 KRT)
    cust_krt = we.get_wallet_by_keys("USER-AMINA-777", "ORG-KARIS-RETAIL", WalletType.KRT_WALLET, AssetType.KRT)
    assert cust_krt.balance == 225.0   # 50 + 175

    # Verify events
    assert any(e.event_type == "PAYMENT_LINK_CHECKOUT_COMPLETED" for e in eb.event_store)
    assert any(e.event_type == "PAYMENT_CONFIRMED" for e in eb.event_store)
