import pytest
from src.domain.models import AssetType, IdentityType, OrderItemModel, WalletType
from src.core.event_bus import event_bus
from src.core.wallet_engine import wallet_engine
from src.core.ledger_engine import ledger_engine
from src.core.rule_engine import rule_engine
from src.verticals.karis_farm.service import karis_farm_service
from src.api.main import (
    CreateIdentityRequest,
    CreateOrderRequest,
    ConfirmPaymentRequest,
    RegisterFarmRequest,
    LogHarvestRequest,
    create_identity,
    create_wallet,
    create_order,
    confirm_payment,
    register_farm,
    log_harvest,
    get_traceability
)

def test_karis_os_end_to_end_simulation():
    # 1. Clear state for clean verification
    event_bus.event_store.clear()
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()

    # 2. Register Identities
    farmer = create_identity(CreateIdentityRequest(
        identity_type=IdentityType.INDIVIDUAL,
        global_identifier="ID-KE-28491029",
        full_name="John Kamau",
        phone_number="+254711223344"
    ))
    coop = create_identity(CreateIdentityRequest(
        identity_type=IdentityType.COOPERATIVE,
        global_identifier="COOP-KE-MACHAKOS-01",
        full_name="Machakos Farmers Cooperative",
        phone_number="+254722334455"
    ))
    customer = create_identity(CreateIdentityRequest(
        identity_type=IdentityType.INDIVIDUAL,
        global_identifier="ID-KE-31920192",
        full_name="Amina Wanjiku",
        phone_number="+254733445566"
    ))

    org_id = "ORG-KARIS-FARM-MACHAKOS"

    # 3. Create Wallets
    # Customer Wallets
    cust_kes = wallet_engine.create_wallet(customer.identity_id, org_id, WalletType.KES_WALLET, AssetType.KES, initial_balance=50000.0)
    cust_krt = wallet_engine.create_wallet(customer.identity_id, org_id, WalletType.KRT_WALLET, AssetType.KRT, initial_balance=0.0)

    # Farmer Wallets
    farmer_kes = wallet_engine.create_wallet(farmer.identity_id, org_id, WalletType.KES_WALLET, AssetType.KES, initial_balance=0.0)
    farmer_krt = wallet_engine.create_wallet(farmer.identity_id, org_id, WalletType.KRT_WALLET, AssetType.KRT, initial_balance=0.0)

    # Treasury Wallets
    treasury_kes = wallet_engine.create_wallet("TREASURY_IDENTITY", org_id, WalletType.RESERVE_WALLET, AssetType.KES, initial_balance=1000000.0)
    treasury_krt = wallet_engine.create_wallet("TREASURY_IDENTITY", org_id, WalletType.REWARD_POOL, AssetType.KRT, initial_balance=500000.0)

    # 4. Register Farm under KARIS FARM Vertical
    farm = register_farm(RegisterFarmRequest(
        farmer_identity_id=farmer.identity_id,
        organization_id=org_id,
        farm_name="Kamau Orchards - Machakos",
        region_county="Machakos County",
        total_acreage=12.5,
        cooperative_identity_id=coop.identity_id
    ))
    assert farm["farm_name"] == "Kamau Orchards - Machakos"

    # 5. Log Harvest of Grade-A Hass Avocados
    batch = log_harvest(LogHarvestRequest(
        farm_id=farm["farm_id"],
        crop_type="HASS_AVOCADO",
        quantity_kg=1000.0,
        quality_grade="GRADE_A",
        unit_cost_kes=150.0
    ))
    assert batch.traceability_qr_code.startswith("KARIS-TRACE-QR-")

    # 6. Verify Traceability
    trace = get_traceability(batch.traceability_qr_code)
    assert trace["farm_name"] == "Kamau Orchards - Machakos"
    assert trace["quality_grade"] == "GRADE_A"

    # 7. Customer places order for 50 KG of Avocados
    order = create_order(CreateOrderRequest(
        organization_id=org_id,
        customer_identity_id=customer.identity_id,
        supplier_identity_id=farmer.identity_id,
        items=[
            OrderItemModel(
                product_id=batch.product_id,
                sku="SKU-AVO-GRADE-A",
                quantity=50.0,
                unit_price=150.0,
                total_price=7500.0
            )
        ]
    ))
    assert order.total_kes_amount == 7500.0

    # 8. Customer confirms M-Pesa Payment
    confirm_payment(ConfirmPaymentRequest(
        order_id=order.order_id,
        payer_identity_id=customer.identity_id,
        payment_method="M_PESA",
        external_reference="QG37MACHAKOS01",
        amount_kes=7500.0
    ))

    # 9. Verify Rule Engine & Ledger Settlement
    # Customer KES debited by 7500
    assert cust_kes.balance == 50000.0 - 7500.0
    # Farmer KES credited by 7500 (Rule 5 & Rule 2 enforced)
    assert farmer_kes.balance == 7500.0

    # 10. Verify KRT Reward Minting (5% of 7500 = 375 KRT)
    assert cust_krt.balance == 375.0
    assert treasury_krt.balance == 500000.0 - 375.0

    # 11. Verify Universal Ledger & Event Bus Immutability
    entries = ledger_engine.get_entries()
    assert len(entries) >= 2  # KES settlement + KRT reward
    assert all(entry.audit_hash != "" for entry in entries)

    events = event_bus.get_event_store()
    assert len(events) >= 5
    assert all(ev.cryptographic_hash is not None for ev in events)
