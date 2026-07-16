import pytest
from src.integrations.erp_tax_sync import erp_notification_engine
from src.ai.crm_intelligence import crm_ai_engine
from src.verticals.future_industries.service import future_industries_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType

def test_erp_accounting_sync_and_notification_templates():
    org = "ORG-KARIS-RETAIL"
    # 1. ERP Batch Sync
    sync = erp_notification_engine.execute_erp_accounting_batch_sync(org, "SAP_S4HANA_KENYA", "FY-2026-Q3")
    assert sync["sync_status"] == "COMPLETED_VERIFIED"
    assert sync["external_batch_reference"].startswith("BATCH-SAP-2026-")

    # 2. Notification Dispatch
    notif = erp_notification_engine.dispatch_notification(
        "TPL-ORDER-CONFIRMED-SMS", "USER-101", "+254711000003",
        {"customer_name": "Amina", "order_number": "ORD-101", "amount_kes": "4500.00", "qr_code": "KARIS-TRACE-QR-01"}, org
    )
    assert notif["delivery_status"] == "DELIVERED_CONFIRMED"
    assert "Amina" in notif["rendered_message_text"]

def test_ai_crm_intelligence_churn_prediction_and_winback():
    org = "ORG-KARIS-RETAIL"
    user_id = "USER-CRM-101"

    wallet_engine.create_wallet("TREASURY_IDENTITY", org, WalletType.REWARD_POOL, AssetType.KRT, 500000.0)

    # High churn risk evaluation (>90 days inactive) -> Triggers automatic 500 KRT retention grant
    eval_res = crm_ai_engine.evaluate_customer_ltv_and_churn(user_id, 150000.0, 95.0, org, "Amina Wanjiku")
    assert eval_res["predicted_churn_risk_pct"] > 60.0
    assert eval_res["retention_campaign_triggered"] is True

    cust_krt = wallet_engine.get_wallet_by_keys(user_id, org, WalletType.KRT_WALLET, AssetType.KRT)
    assert cust_krt.balance == 500.0 # 500 KRT win-back retention bonus granted!

def test_future_industries_education_tourism_real_estate():
    org = "ORG-KARIS-RETAIL"
    student_id = "USER-STUD-01"
    parent_id = "USER-PARENT-01"
    guest_id = "USER-GUEST-01"
    investor_id = "USER-INV-01"

    wallet_engine.create_wallet("TREASURY_IDENTITY", org, WalletType.REWARD_POOL, AssetType.KRT, 500000.0)
    wallet_engine.create_wallet("TREASURY_IDENTITY", org, WalletType.RESERVE_WALLET, AssetType.INVESTMENT, 10000000.0)

    # 1. Education Hub (`KARIS Edu-Pay`)
    plan = future_industries_engine.register_tuition_plan(student_id, parent_id, "Machakos Academy", "Term 3 2026", 45000.0, org)
    pay_res = future_industries_engine.pay_tuition_installment(plan["plan_id"], 15000.0)
    assert pay_res["krt_scholarship_awarded"] == 1500.0 # 10% KRT-EDU scholarship grant

    # 2. Tourism Hub (`KARIS Safari & Stays`)
    safari = future_industries_engine.book_safari_lodge(guest_id, "Machakos Luxury Eco-Camp", 3, 12000.0, org)
    assert safari["total_booking_price_kes"] == 36000.0
    assert safari["krt_green_carbon_offset_tokens"] == 75.0 # 3 nights * 25 KRT-GREEN

    # 3. Real Estate Hub (`KARIS Prop-Share`)
    syn = future_industries_engine.create_property_syndication("PROP-MLO-01", "Mlolongo Trade Towers", 100000000.0, 10000.0, 13.8, org)
    alloc = future_industries_engine.allocate_fractional_units(syn["syndication_id"], investor_id, 50.0)
    assert alloc["units_purchased"] == 50.0
    assert alloc["total_cost_kes"] == 500000.0
