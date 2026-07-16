import pytest
from src.security.hardware_hsm import hardware_hsm_engine
from src.verticals.loyalty.network_tier_engine import loyalty_network_engine
from src.observability.ha_failover import ha_failover_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType

def test_mobile_nfc_biometric_smart_terminal_hsm_encryption_and_checkout():
    org = "ORG-KARIS-RETAIL"
    user_id = "USER-HSM-101"
    seller_id = "USER-HSM-SELLER-202"

    wallet_engine.create_wallet(user_id, org, WalletType.KES_WALLET, AssetType.KES, 15000.0)

    # 1. Issue Biometric NFC Cryptogram
    token = hardware_hsm_engine.generate_nfc_biometric_payment_token(
        user_id, "W-CUST-1", 4500.0, "POS-MLO-01", "FACE_ID_VERIFIED", org
    )
    assert token["nfc_cryptogram"].startswith("NFC-TOKEN-2026-")
    assert token["status"] == "ISSUED_PENDING_SCAN"

    # 2. POS Terminal Scan & Double-Entry Settlement
    settle = hardware_hsm_engine.verify_and_settle_nfc_token(token["nfc_cryptogram"], seller_id, "POS-MLO-01")
    assert settle["status"] == "SUCCESS"
    assert settle["settled_amount_kes"] == 4500.0

    cust_kes = wallet_engine.get_wallet_by_keys(user_id, org, WalletType.KES_WALLET, AssetType.KES)
    assert cust_kes.balance == 10500.0 # 15000 - 4500

def test_customer_loyalty_tier_auto_upgrades_and_cross_merchant_clearing():
    org_farm = "ORG-KARIS-FARM"
    org_eatery = "ORG-KARIS-EATERY"
    user_id = "USER-LOYALTY-VIP-01"

    # 1. Spend Evaluation -> Auto upgrade to PLATINUM_VIP
    tier = loyalty_network_engine.evaluate_and_upgrade_customer_tier(user_id, total_lifetime_spend_kes=125000.0, krt_balance=450.0, organization_id=org_farm)
    assert tier["current_tier"] == "PLATINUM_VIP"
    assert tier["rebate_delivery_fee_pct"] == 15.0

    # 2. Cross-Merchant Network Redemption (Spend KRT earned at FARM inside Eatery)
    wallet_engine.create_wallet(user_id, org_farm, WalletType.KRT_WALLET, AssetType.KRT, 500.0)
    wallet_engine.create_wallet("TREASURY_IDENTITY", org_eatery, WalletType.REWARD_POOL, AssetType.KRT, 1000000.0)

    red = loyalty_network_engine.execute_cross_merchant_network_redemption(user_id, org_farm, org_eatery, 150.0)
    assert red["clearing_status"] == "CLEARED_SETTLED"
    assert red["kes_equivalent_value"] == 150.0

def test_active_active_ha_geographic_failover_routing():
    failover = ha_failover_engine.evaluate_cluster_health_and_execute_failover(
        "CLUSTER-NAIROBI-MAIN", "CLUSTER-MACHAKOS-EDGE", "Simulated node heartbeat timeout"
    )
    assert failover["failed_node_code"] == "CLUSTER-NAIROBI-MAIN"
    assert failover["promoted_node_code"] == "CLUSTER-MACHAKOS-EDGE"
    assert failover["ledger_continuity_status"] == "100PCT_LEDGER_CONTINUITY_VERIFIED"
