import pytest
from src.integrations.mobile_passkey_push import mobile_passkey_push_engine
from src.observability.ledger_reconciliation import ledger_reconciliation_engine
from src.observability.k8s_autoscaler import k8s_hpa_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType

def test_mobile_passkeys_push_notifications_and_gamified_bonuses():
    org = "ORG-KARIS-RETAIL"
    user_id = "USER-PASSKEY-101"

    wallet_engine.create_wallet(user_id, org, WalletType.KRT_WALLET, AssetType.KRT, 100.0)
    wallet_engine.create_wallet("TREASURY_IDENTITY", org, WalletType.REWARD_POOL, AssetType.KRT, 500000.0)

    # 1. Register Push Device
    dev = mobile_passkey_push_engine.register_push_device(user_id, "FCM-TOKEN-101", "ANDROID_FCM", "Samsung Galaxy S24 Ultra", "CUSTOMER")
    assert dev["push_device_token"] == "FCM-TOKEN-101"

    # 2. Verify Passkey Challenge (Triggering 10th milestone 250 KRT bonus)
    pk_res = mobile_passkey_push_engine.execute_mobile_passkey_challenge_and_bonus(user_id, org, "IOS_APPLE_SECURE_ENCLAVE", "PASSKEY-CRED-01")
    assert pk_res["status"] == "SUCCESS"
    assert pk_res["krt_bonus_awarded"] == 250.0

    cust_krt = wallet_engine.get_wallet_by_keys(user_id, org, WalletType.KRT_WALLET, AssetType.KRT)
    assert cust_krt.balance == 350.0 # 100 + 250

    # 3. Dispatch Push Notification
    push_disp = mobile_passkey_push_engine.dispatch_push_notification(user_id, "Security Bonus Awarded", "You earned 250 KRT for verifying FIDO2 passkey!")
    assert push_disp["delivery_status"] == "DELIVERED_CONFIRMED_APNS_FCM"

def test_universal_ledger_reconciliation_sweeps():
    org = "ORG-KARIS-RETAIL"
    sweep = ledger_reconciliation_engine.execute_automated_ledger_reconciliation_sweep(org)
    assert sweep["reconciliation_status"] == "100PCT_MATHEMATICALLY_RECONCILED"
    assert sweep["total_wallets_audited"] >= 0

def test_kubernetes_hpa_autoscaling_and_pod_orchestration():
    # Evaluate traffic surge (2,380 ops/sec, 88.5% CPU) -> Scale out pods 4 -> 16
    scale_out = k8s_hpa_engine.evaluate_traffic_load_and_scale_pods(2380.0, 88.5, "karis-api-gateway", "CLUSTER-NAIROBI-MAIN")
    assert scale_out["scaling_action"] == "PODS_SCALED_OUT_TRAFFIC_SURGE"
    assert scale_out["previous_replicas"] == 4
    assert scale_out["new_replicas"] == 16

    # Evaluate low load -> Scale in pods 16 -> 8
    scale_in = k8s_hpa_engine.evaluate_traffic_load_and_scale_pods(150.0, 20.0, "karis-api-gateway", "CLUSTER-NAIROBI-MAIN")
    assert scale_in["scaling_action"] == "PODS_SCALED_IN_LOW_LOAD"
    assert scale_in["new_replicas"] == 8
