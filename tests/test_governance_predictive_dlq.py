import pytest
from src.security.governance_compliance import governance_engine
from src.ai.predictive_intelligence import predictive_engine
from src.core.dlq_healing import dlq_engine
from src.core.event_bus import event_bus

def test_governance_kyc_aml_and_kra_etims_tax_invoices():
    org = "ORG-KARIS-RETAIL"
    user_id = "USER-GOV-101"
    seller_id = "USER-GOV-202"

    # 1. Multi-tier KYC Verification
    kyc = governance_engine.complete_kyc_verification(user_id, org, "ID-28491029", "A001234567Z", "TIER_3_ADVANCED")
    assert kyc["verification_tier"] == "TIER_3_ADVANCED"
    assert kyc["aml_sanction_check_status"] == "CLEARED"

    # 2. AML Structuring Velocity Check (Smurfing check)
    aml_normal = governance_engine.check_aml_transaction_velocity(user_id, org, 15000.0, "M_PESA")
    assert aml_normal["status"] == "CLEARED"

    aml_suspicious = governance_engine.check_aml_transaction_velocity(user_id, org, 249000.0, "M_PESA")
    assert aml_suspicious["status"] == "FLAGGED_SAR"
    assert aml_suspicious["sar_issued"] is True
    assert aml_suspicious["sar_details"]["triggering_rule_code"] == "AML-STRUCTURING-VELOCITY-01"

    # 3. KRA eTIMS Digital Tax Invoice
    inv = governance_engine.issue_kra_etims_tax_invoice(org, "ORD-ETIMS-99", user_id, seller_id, "P051234567Z", 10000.0)
    assert inv["vat_amount_kes"] == 1600.0  # 16% of 10,000
    assert inv["total_invoice_amount_kes"] == 11600.0
    assert inv["etims_control_number"].startswith("KRA-ETIMS-2026-")

def test_predictive_intelligence_demand_forecast_and_pricing():
    org = "ORG-KARIS-RETAIL"
    prod_id = "PROD-AVO-01"

    # 1. Demand Forecast
    fcast = predictive_engine.generate_demand_forecast(org, prod_id, "STORE-01", daily_sales_velocity=50.0, current_shelf_quantity=250.0)
    assert fcast["predicted_demand_units"] == 1500.0 # 50 * 30 days
    assert fcast["recommended_reorder_units"] == 700.0 # 50 * 14 days buffer
    assert fcast["confidence_score_pct"] > 90.0

    # 2. Dynamic Pricing Recommendation (Rule 10)
    rec = predictive_engine.recommend_dynamic_pricing(org, prod_id, 200.0, "SHELF_EXPIRY_APPROACHING")
    assert rec["recommended_unit_price_kes"] == 150.0 # 25% clearance markdown
    assert rec["approval_status"] == "PENDING_HUMAN_APPROVAL"

def test_distributed_dlq_and_self_healing_recovery():
    event_bus.event_store.clear()
    org = "ORG-KARIS-RETAIL"

    # 1. Record failed event dispatch
    failed = dlq_engine.record_failed_dispatch("EV-FAIL-101", "RULE_ENGINE_SUBSCRIBER", "Connection timeout to PostgreSQL slave", org)
    assert failed["status"] == "DEAD_LETTER_QUEUED"
    assert failed["retry_count"] == 0

    # 2. Trigger Self-Healing Sweep
    recovered = dlq_engine.retry_dead_letter_events()
    assert len(recovered) >= 1
    assert recovered[0]["status"] == "PROCESSED_RECOVERED"
    assert recovered[0]["retry_count"] == 1

    # Verify DLQ_EVENT_RECOVERED was published to Event Bus
    events = event_bus.get_event_store()
    assert any(ev.event_type == "DLQ_EVENT_RECOVERED" for ev in events)
