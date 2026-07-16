import pytest
from src.core.offline_sync import offline_sync_engine
from src.verticals.marketplace.service import marketplace_split_engine
from src.security.regulatory_reporting import regulatory_compliance_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType

def test_mobile_app_and_pos_offline_synchronization():
    org = "ORG-KARIS-RETAIL"
    cashier = "268e1e85-a0b3-445d-827b-98e327af3bee"
    customer = "USER-OFFLINE-101"

    wallet_engine.create_wallet(customer, org, WalletType.KES_WALLET, AssetType.KES, 20000.0)

    offline_txs = [
        {"type": "POS_CHECKOUT", "amount_kes": 4500.0, "customer_id": customer, "seller_id": cashier},
        {"type": "POS_CHECKOUT", "amount_kes": 1500.0, "customer_id": customer, "seller_id": cashier}
    ]

    sync_res = offline_sync_engine.synchronize_offline_batch("POS-MLO-01", offline_txs, cashier, org)
    assert sync_res["sync_status"] == "SYNCHRONIZED_SUCCESS"
    assert sync_res["synced_transactions_count"] == 2
    assert sync_res["total_kes_volume_synchronized"] == 6000.0

    cust_kes = wallet_engine.get_wallet_by_keys(customer, org, WalletType.KES_WALLET, AssetType.KES)
    assert cust_kes.balance == 14000.0 # 20000 - 6000

def test_multi_vendor_marketplace_aggregation_and_split_settlement():
    org = "ORG-KARIS-RETAIL"
    cust_id = "USER-MKT-CUST-01"
    vendor_a = "268e1e85-a0b3-445d-827b-98e327af3bee"
    vendor_b = "8b6ff564-ce30-489e-8a02-75004ccd5516"

    wallet_engine.create_wallet(cust_id, org, WalletType.KES_WALLET, AssetType.KES, 15000.0)

    items = [
        {"vendor_id": vendor_a, "amount_kes": 5000.0, "commission_pct": 15.0},
        {"vendor_id": vendor_b, "amount_kes": 3000.0, "commission_pct": 15.0}
    ]

    split_res = marketplace_split_engine.execute_multi_vendor_split_settlement(cust_id, items, "QG37TEST123", org)
    assert split_res["status"] == "SUCCESS"
    assert len(split_res["allocations"]) == 2
    assert split_res["cart_order"]["total_cart_amount_kes"] == 8000.0
    assert split_res["cart_order"]["total_platform_commission_kes"] == 1200.0 # 15% of 8000

    cust_kes = wallet_engine.get_wallet_by_keys(cust_id, org, WalletType.KES_WALLET, AssetType.KES)
    assert cust_kes.balance == 7000.0 # 15000 - 8000

def test_automated_regulatory_compliance_and_multi_jurisdictional_reporting():
    org = "ORG-KARIS-RETAIL"
    report = regulatory_compliance_engine.generate_jurisdictional_regulatory_report("KE", "CENTRAL_BANK_AML_FIU_SUMMARY", org)
    assert report["jurisdiction_code"] == "KE"
    assert report["compliance_status"] == "100PCT_VERIFIED_COMPLIANT"
    assert report["total_records_audited"] >= 0
