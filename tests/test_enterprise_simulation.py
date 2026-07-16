import pytest
from src.domain.models import AssetType, IdentityType, OrderItemModel, WalletType
from src.core.event_bus import event_bus
from src.core.wallet_engine import wallet_engine
from src.core.ledger_engine import ledger_engine
from src.core.rule_engine import rule_engine
from src.core.treasury_engine import treasury_engine
from src.core.exchange_engine import exchange_engine
from src.core.ai_gateway import ai_gateway

from src.verticals.karis_farm.service import karis_farm_service
from src.verticals.retail_pos.service import retail_pos_service
from src.verticals.eatery.service import eatery_service
from src.verticals.logistics.service import logistics_service
from src.verticals.healthcare.service import healthcare_service
from src.verticals.mobility.service import mobility_service
from src.verticals.finance_invest.service import finance_investment_service

from src.api.main import (
    CreateIdentityRequest,
    CreateOrderRequest,
    ConfirmPaymentRequest,
    create_identity,
    create_order,
    confirm_payment,
)

def test_full_enterprise_multi_vertical_simulation():
    # 1. Clear core architecture state
    event_bus.event_store.clear()
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()

    # 2. Register Multi-Tenant Identities
    farmer = create_identity(CreateIdentityRequest(
        identity_type=IdentityType.INDIVIDUAL,
        global_identifier="ID-KE-FARMER-01",
        full_name="John Kamau (Farmer)",
        phone_number="+254711000001"
    ))
    coop = create_identity(CreateIdentityRequest(
        identity_type=IdentityType.COOPERATIVE,
        global_identifier="ID-KE-COOP-01",
        full_name="Machakos Cooperative",
        phone_number="+254711000002"
    ))
    customer = create_identity(CreateIdentityRequest(
        identity_type=IdentityType.INDIVIDUAL,
        global_identifier="ID-KE-CUST-01",
        full_name="Amina Wanjiku (Customer)",
        phone_number="+254711000003"
    ))
    rider = create_identity(CreateIdentityRequest(
        identity_type=IdentityType.INDIVIDUAL,
        global_identifier="ID-KE-RIDER-01",
        full_name="David Ochieng (Rider & Driver)",
        phone_number="+254711000004"
    ))
    doctor = create_identity(CreateIdentityRequest(
        identity_type=IdentityType.INDIVIDUAL,
        global_identifier="ID-KE-DOC-01",
        full_name="Dr. Omondi (Healthcare Specialist)",
        phone_number="+254711000005"
    ))

    org_farm = "ORG-KARIS-FARM"
    org_retail = "ORG-KARIS-RETAIL"
    org_health = "ORG-KARIS-HEALTH"

    # 3. Setup Wallets & Treasury Backing
    cust_kes = wallet_engine.create_wallet(customer.identity_id, org_retail, WalletType.KES_WALLET, AssetType.KES, 50000.0)
    cust_krt = wallet_engine.create_wallet(customer.identity_id, org_retail, WalletType.KRT_WALLET, AssetType.KRT, 500.0)
    farmer_kes = wallet_engine.create_wallet(farmer.identity_id, org_farm, WalletType.KES_WALLET, AssetType.KES, 0.0)
    rider_kes = wallet_engine.create_wallet(rider.identity_id, org_retail, WalletType.KES_WALLET, AssetType.KES, 0.0)
    
    # Treasury Pool wallets across orgs
    treasury_reserve = wallet_engine.create_wallet("TREASURY_IDENTITY", org_retail, WalletType.RESERVE_WALLET, AssetType.KES, 2000000.0)
    treasury_krt = wallet_engine.create_wallet("TREASURY_IDENTITY", org_retail, WalletType.REWARD_POOL, AssetType.KRT, 1000000.0)
    operations_kes = wallet_engine.create_wallet("OPERATIONS_IDENTITY", org_retail, WalletType.RESERVE_WALLET, AssetType.KES, 100000.0)

    # 4. Vertical 1: KARIS FARM™
    farm = karis_farm_service.register_farm(farmer.identity_id, org_farm, "Kamau Orchards", "Machakos County", 15.0)
    batch = karis_farm_service.log_harvest(farm["farm_id"], "HASS_AVOCADO", 1000.0, "GRADE_A", 150.0)
    assert batch.traceability_qr_code.startswith("KARIS-TRACE-QR-")

    # 5. Vertical 2: Retail POS & Mixed Payment (Exchange Engine)
    store = retail_pos_service.register_store_and_terminal(org_retail, "Machakos Supermarket", "POS-MLO-01")
    session = retail_pos_service.open_pos_session("POS-MLO-01", farmer.identity_id)
    
    # Customer buys groceries using mixed payment: KES + 200 KRT discount
    checkout_res = retail_pos_service.process_pos_checkout(
        session.session_id, store["store_id"], customer.identity_id, farmer.identity_id,
        items=[OrderItemModel(product_id=batch.product_id, sku="SKU-AVO-01", quantity=20.0, unit_price=150.0, total_price=3000.0)],
        payment_method="MIXED_PAYMENT", krt_discount_used=200.0
    )
    assert checkout_res["fiat_paid_kes"] == 2800.0
    assert cust_krt.balance == 500.0 - 200.0 + round(2800.0 * 0.05, 4) # Deducted 200, earned 5% (140 KRT)

    # 6. Vertical 3 & 4: Eatery KDS & Logistics Dispatch (Rule 4)
    eatery = eatery_service.register_eatery(org_retail, "Machakos Cloud Kitchen")
    kds_order = eatery_service.submit_to_kds(eatery["eatery_id"], "ORD-EATERY-101")
    eatery_service.flag_meal_ready(kds_order.kds_id, "CHEF-ID")

    log_rider = logistics_service.register_rider(rider.identity_id, org_retail, "MOTORCYCLE", "KMDE-123A")
    dispatch = logistics_service.request_delivery_dispatch(org_retail, "ORD-EATERY-101", "Machakos Kitchen", "Mlolongo Estate", 5.0)
    logistics_service.assign_rider(dispatch.dispatch_id, log_rider["rider_id"])
    
    # Confirm delivery -> Triggering Rider Escrow Release via Rule 4
    logistics_service.confirm_delivery_completed(dispatch.dispatch_id, customer.identity_id, "-1.35,36.93", "OTP-9921")
    assert rider_kes.balance > 0.0 # Payout released from operations escrow!

    # 7. Vertical 5: Healthcare EMR & Telemedicine
    fac = healthcare_service.register_facility(org_health, "Machakos County Clinic")
    pat = healthcare_service.register_patient(customer.identity_id, "B+")
    apt = healthcare_service.book_appointment(fac["facility_id"], pat["patient_id"], doctor.identity_id, "TELEMEDICINE", 1500.0)
    presc = healthcare_service.issue_prescription(apt.appointment_id, "PROD-MED-01", 2.0, "Checkup clean")
    assert presc.status == "ISSUED"

    # 8. Vertical 6: Mobility & Ride-Hailing
    mob_driver = mobility_service.register_driver(rider.identity_id, org_retail, "LIC-9901", "Bajaj TukTuk", "KTUK-001")
    trip = mobility_service.request_ride(org_retail, customer.identity_id, "Mlolongo Market", "Machakos CBD", 12.0)
    mobility_service.accept_ride(trip.trip_id, mob_driver["driver_id"])
    mobility_service.complete_trip(trip.trip_id)
    assert trip.trip_status == "TRIP_COMPLETED"

    # 9. Vertical 7: Investor Capital Pool & AI Credit Lending (Rule 3 & Rule 10)
    pool = finance_investment_service.create_investment_pool("POOL-AGRI-01", "Agriculture Fund", "AGRICULTURE_GROWTH_FUND", 5000000.0, 14.5)
    finance_investment_service.deposit_capital(pool.pool_id, coop.identity_id, org_farm, 500000.0)

    # Farmer applies for credit
    app = finance_investment_service.apply_for_credit(farmer.identity_id, org_farm, 100000.0, 150000.0)
    assert app["ai_risk_score"] <= 50.0 # Risk AI evaluates application
    
    # Ensure credit wallet exists before disbursement
    wallet_engine.create_wallet(farmer.identity_id, org_farm, WalletType.CREDIT_WALLET, AssetType.CREDIT, 0.0)
    wallet_engine.create_wallet("TREASURY_IDENTITY", org_farm, WalletType.RESERVE_WALLET, AssetType.KES, 1000000.0)
    
    finance_investment_service.approve_and_disburse_loan(app["application_id"], "ADMIN-ID")
    farmer_credit = wallet_engine.get_wallet_by_keys(farmer.identity_id, org_farm, WalletType.CREDIT_WALLET, AssetType.CREDIT)
    assert farmer_credit.balance == 100000.0

    # 10. Verify Universal Ledger & Event Store Integrity (Rule 8 & 9)
    entries = ledger_engine.get_entries()
    assert len(entries) >= 5
    assert all(entry.audit_hash != "" for entry in entries)

    events = event_bus.get_event_store()
    assert len(events) >= 15
    assert all(ev.cryptographic_hash is not None for ev in events)
