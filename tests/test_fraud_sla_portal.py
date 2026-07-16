import pytest
from src.security.fraud_ai import fraud_ai_engine
from src.verticals.crm_call_center.sla_engine import call_center_sla_engine
from src.core.omnichannel_portal import omnichannel_portal_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType

def test_ai_fraud_detection_and_impossible_travel_velocity():
    org = "ORG-KARIS-RETAIL"
    user_id = "USER-FRAUD-101"

    w = wallet_engine.create_wallet(user_id, org, WalletType.KES_WALLET, AssetType.KES, 100000.0)

    # 1. Normal transaction in Machakos
    normal = fraud_ai_engine.evaluate_transaction_fraud_risk(
        user_id, w.wallet_id, 5000.0, "DEV-IP-01", "-1.3564,36.9321", "M_PESA", org
    )
    assert normal["action_taken"] == "CLEARED_PROCEED"
    assert w.status == "ACTIVE"

    # 2. Impossible Travel to Mombasa 3 mins later
    anom = fraud_ai_engine.evaluate_transaction_fraud_risk(
        user_id, w.wallet_id, 15000.0, "DEV-IP-02", "-4.0435,39.6682", "M_PESA", org
    )
    assert anom["flagged_anomaly_type"] == "GEOGRAPHIC_VELOCITY_ABUSE_IMPOSSIBLE_TRAVEL"
    assert anom["fraud_risk_score"] > 80.0
    assert w.status == "FROZEN" # Rule 5 & Rule 10 protection active!

def test_call_center_sla_tracking_and_escalation_sweep():
    org = "ORG-KARIS-RETAIL"
    # Track ticket with 0 due minutes to force instant breach during sweep
    rec = call_center_sla_engine.track_ticket_sla("TKT-SLA-101", "URGENT", 0, -1, org)
    assert rec["sla_status"] == "ACTIVE_WITHIN_SLA"

    escalated = call_center_sla_engine.execute_sla_escalation_sweep()
    assert len(escalated) >= 1
    assert any(e["ticket_id"] == "TKT-SLA-101" for e in escalated)
    assert escalated[0]["escalated_to_supervisor_id"] == "SUPERVISOR-ID-99"

def test_omnichannel_super_app_and_merchant_portal_gateways():
    org = "ORG-KARIS-RETAIL"
    user_id = "7f8013a9-310c-4f16-9031-295274a26944"

    # 1. Customer Super App Profile
    app_prof = omnichannel_portal_engine.get_unified_customer_super_app_profile(user_id, org)
    assert app_prof["portal_type"] == "CUSTOMER_SUPER_APP"
    assert app_prof["active_verticals_count"] == 12
    assert "wallets_portfolio" in app_prof
    assert "active_engagements" in app_prof

    # 2. Merchant Portal Dashboard
    merch_dash = omnichannel_portal_engine.get_unified_merchant_portal_dashboard(org)
    assert merch_dash["portal_type"] == "MERCHANT_OMNICHANNEL_PORTAL"
    assert merch_dash["settlement_engine_connection"] == "VERIFIED_DOUBLE_ENTRY"
