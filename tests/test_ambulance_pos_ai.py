import pytest
from src.verticals.healthcare.ambulance_ai import ambulance_ai_engine
from src.verticals.retail_pos.pos_ai import pos_ai_engine

def test_emergency_ambulance_ai_dispatching():
    org = "ORG-KARIS-HEALTH"
    # Ensure standby unit exists near Machakos CBD (-1.3564,36.9321)
    ambulance_ai_engine.register_ambulance_unit(org, "AMB-TEST-ALS-99", "KCT-999Z", "ADVANCED_LIFE_SUPPORT_ALS", "-1.3564,36.9321", "PARAMEDIC-TEST")

    # Dispatch nearest ALS unit for highway emergency
    dispatch = ambulance_ai_engine.dispatch_nearest_emergency_unit("-1.3600,36.9350", "ADVANCED_LIFE_SUPPORT_ALS", org)
    assert dispatch["status"] == "AMBULANCE_DISPATCHED"
    assert dispatch["life_support_tier"] == "ADVANCED_LIFE_SUPPORT_ALS"
    assert dispatch["estimated_arrival_minutes"] > 0

def test_pos_ai_queue_congestion_and_shrinkage_audits():
    org = "ORG-KARIS-RETAIL"
    store_id = "STORE-RETAIL-MLOLONGO-01"

    # 1. Normal Queue Flow
    normal_q = pos_ai_engine.monitor_pos_queue(store_id, "POS-MLO-01", 2, 1.5, org)
    assert normal_q["congestion_status"] == "NORMAL_FLOW"

    # 2. Queue Congestion Alert -> Commanding Express Lane
    congested_q = pos_ai_engine.monitor_pos_queue(store_id, "POS-MLO-01", 10, 6.0, org)
    assert congested_q["congestion_status"] == "QUEUE_CONGESTION_DETECTED"
    assert "Express Terminal" in congested_q["ai_recommendation_action"]

    # 3. Inventory Shrinkage Recount Audit
    shrink = pos_ai_engine.audit_inventory_shrinkage(store_id, "PROD-AVO-01", 300.0, 280.0, 150.0, "THEFT_SUSPECTED", org)
    assert shrink["discrepancy_quantity"] == 20.0
    assert shrink["estimated_loss_kes"] == 3000.0
