import uuid
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path
from src.domain.models import AssetType, OrderItemModel, WalletType
from src.core.event_bus import event_bus
from src.core.wallet_engine import wallet_engine
from src.core.ledger_engine import ledger_engine
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

router = APIRouter(tags=["Web Portal & Interactive Live Simulators"])

@router.get("/", response_class=HTMLResponse)
@router.get("/portal", response_class=HTMLResponse)
def get_portal():
    html_path = Path(__file__).resolve().parent.parent.parent / "web" / "index.html"
    return html_path.read_text(encoding="utf-8")

@router.post("/api/v1/simulators/pos")
def simulate_pos_checkout():
    """Simulates live Supermarket POS checkout with mixed KES+KRT M-Pesa payment."""
    org_retail = "ORG-KARIS-RETAIL"
    cust_id = "7f8013a9-310c-4f16-9031-295274a26944"
    farmer_id = "268e1e85-a0b3-445d-827b-98e327af3bee"

    # Ensure wallets exist
    wallet_engine.create_wallet(cust_id, org_retail, WalletType.KES_WALLET, AssetType.KES, 50000.0)
    wallet_engine.create_wallet(cust_id, org_retail, WalletType.KRT_WALLET, AssetType.KRT, 500.0)
    wallet_engine.create_wallet(farmer_id, "ORG-KARIS-FARM", WalletType.KES_WALLET, AssetType.KES, 10000.0)
    wallet_engine.create_wallet("TREASURY_IDENTITY", org_retail, WalletType.RESERVE_WALLET, AssetType.KES, 2000000.0)
    wallet_engine.create_wallet("TREASURY_IDENTITY", org_retail, WalletType.REWARD_POOL, AssetType.KRT, 1000000.0)

    store = retail_pos_service.register_store_and_terminal(org_retail, "Machakos Supermarket", f"POS-SIM-{uuid.uuid4().hex[:4].upper()}")
    session = retail_pos_service.open_pos_session(store["terminal_code"], farmer_id)

    res = retail_pos_service.process_pos_checkout(
        session.session_id, store["store_id"], cust_id, farmer_id,
        items=[OrderItemModel(product_id="PROD-AVO-01", sku="SKU-AVO-SIM", quantity=25.0, unit_price=150.0, total_price=3750.0)],
        payment_method="MIXED_PAYMENT", krt_discount_used=250.0
    )
    return {"status": "SUCCESS", "checkout_result": res}

@router.post("/api/v1/simulators/logistics")
def simulate_kds_and_logistics():
    """Simulates Kitchen KDS, AI Rider Dispatch, and GPS Proof of Delivery escrow payout."""
    org_retail = "ORG-KARIS-RETAIL"
    rider_id = "da11cf88-5121-49b0-9a3b-28f0d8a11a2b"
    cust_id = "7f8013a9-310c-4f16-9031-295274a26944"

    wallet_engine.create_wallet(rider_id, org_retail, WalletType.KES_WALLET, AssetType.KES, 1000.0)
    wallet_engine.create_wallet("OPERATIONS_IDENTITY", org_retail, WalletType.RESERVE_WALLET, AssetType.KES, 100000.0)

    eatery = eatery_service.register_eatery(org_retail, "Machakos Cloud Kitchen")
    order_id = f"ORD-KDS-{uuid.uuid4().hex[:6].upper()}"
    kds_order = eatery_service.submit_to_kds(eatery["eatery_id"], order_id)
    eatery_service.flag_meal_ready(kds_order.kds_id, "CHEF-SIM")

    log_rider = logistics_service.register_rider(rider_id, org_retail, "MOTORCYCLE", f"KMDE-{uuid.uuid4().hex[:4].upper()}")
    dispatch = logistics_service.request_delivery_dispatch(org_retail, order_id, "Machakos Kitchen", "Mlolongo Estate", 6.5)
    logistics_service.assign_rider(dispatch.dispatch_id, log_rider["rider_id"])
    res = logistics_service.confirm_delivery_completed(dispatch.dispatch_id, cust_id, "-1.35,36.93", "OTP-SIM-99")
    return {"status": "SUCCESS", "delivery_result": res}

@router.post("/api/v1/simulators/healthcare")
def simulate_healthcare_visit():
    """Simulates Healthcare Telemedicine consultation and CHV maternal health check."""
    org_health = "ORG-KARIS-HEALTH"
    cust_id = "7f8013a9-310c-4f16-9031-295274a26944"
    doc_id = "6d17b5bc-b136-43ad-87c8-90e28717dc44"

    fac = healthcare_service.register_facility(org_health, "Machakos County Clinic")
    pat = healthcare_service.register_patient(cust_id, "O+")
    apt = healthcare_service.book_appointment(fac["facility_id"], pat["patient_id"], doc_id, "TELEMEDICINE", 1500.0)
    presc = healthcare_service.issue_prescription(apt.appointment_id, "PROD-MED-SIM", 1.0, "Routine tele-checkup")
    chv_res = healthcare_service.record_chv_visit(org_health, "CHV-ID-SIM", pat["patient_id"], "Maternal check clean")
    return {"status": "SUCCESS", "appointment_id": apt.appointment_id, "prescription_status": presc.status, "chv_result": chv_res}

@router.post("/api/v1/simulators/credit")
def simulate_credit_disbursement():
    """Simulates Risk AI credit evaluation and loan disbursement via Universal Ledger."""
    org_farm = "ORG-KARIS-FARM"
    farmer_id = "268e1e85-a0b3-445d-827b-98e327af3bee"

    wallet_engine.create_wallet(farmer_id, org_farm, WalletType.CREDIT_WALLET, AssetType.CREDIT, 0.0)
    wallet_engine.create_wallet("TREASURY_IDENTITY", org_farm, WalletType.CREDIT_WALLET, AssetType.CREDIT, 10_000_000.0)

    app = finance_investment_service.apply_for_credit(farmer_id, org_farm, 85000.0, 120000.0)
    res = finance_investment_service.approve_and_disburse_loan(app["application_id"], "ADMIN-ID")
    return {"status": "SUCCESS", "credit_application": app, "disbursement_result": res}
