import pytest
from src.verticals.financial_services.insurance_engine import parametric_insurance_iot_engine
from src.security.policy_control import operational_policy_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType

def test_parametric_crop_insurance_and_iot_sensor_telemetry():
    org = "ORG-KARIS-FARM"
    farmer_id = "268e1e85-a0b3-445d-827b-98e327af3bee"
    farm_id = "FARM-ID-MACHAKOS-01"

    # Ensure treasury and farmer KES wallets exist
    wallet_engine.create_wallet(farmer_id, org, WalletType.KES_WALLET, AssetType.KES, 0.0)
    wallet_engine.create_wallet("TREASURY_IDENTITY", org, WalletType.RESERVE_WALLET, AssetType.KES, 10_000_000.0)

    # 1. Issue Policy
    pol = parametric_insurance_iot_engine.issue_parametric_policy(farmer_id, farm_id, org, "CROP_DROUGHT_INDEX", 15.0, 5000.0, 50000.0)
    assert pol["policy_status"] == "ACTIVE_INSURED"

    # 2. Log Drought Telemetry (<20% moisture) -> Auto irrigation & claim settlement
    tel = parametric_insurance_iot_engine.log_iot_sensor_telemetry("IOT-MACHAKOS-SN-01", farm_id, 14.5, 26.0, 31.0, 0.0, org)
    assert "Drought detected" in tel["automated_action_triggered"]
    assert "VALVE-MLO-12 opened" in tel["automated_action_triggered"]

    # Verify claim was auto-approved and settled via Universal Ledger (Rule 2 & Rule 5)
    farmer_kes = wallet_engine.get_wallet_by_keys(farmer_id, org, WalletType.KES_WALLET, AssetType.KES)
    assert farmer_kes.balance == 50000.0
    assert pol["policy_status"] == "CLAIM_PAID_OUT"

def test_operational_governance_policy_and_api_keys():
    org = "ORG-KARIS-RETAIL"
    user_id = "ADMIN-USER-01"

    # 1. Governance Policy
    pol = operational_policy_engine.create_governance_policy(org, "POL-TEST-01", "Test Reserve Policy", "TREASURY_LIQUIDITY_RESERVE", '{"min_pct": 20}')
    assert pol["policy_code"] == "POL-TEST-01"

    # 2. API Key Lifecycle
    key = operational_policy_engine.issue_api_key(user_id, org, "POS Terminal Key", ["ORDERS:WRITE"])
    assert key["key_prefix"].startswith("KARIS_LIVE_")
    assert key["status"] == "ACTIVE"
    assert "raw_api_secret_once" in key

    rev = operational_policy_engine.revoke_api_key(key["key_id"], user_id)
    assert rev["status"] == "SUCCESS"
    assert operational_policy_engine.api_keys[key["key_id"]]["status"] == "REVOKED"

    # 3. Dynamic Tax Rules
    tax = operational_policy_engine.create_tax_rule(org, "KE", "TAX-KE-VAT-16", "Standard VAT", 16.0)
    assert tax["tax_rate_pct"] == 16.0
