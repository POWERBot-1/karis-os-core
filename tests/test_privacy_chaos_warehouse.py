import pytest
from src.security.privacy_engine import privacy_gdpr_engine
from src.observability.chaos_engine import chaos_engine
from src.verticals.logistics.route_weather_ai import warehouse_weather_engine
from src.verticals.healthcare.service import healthcare_service
from src.security.audit import audit_engine

def test_enterprise_privacy_gdpr_export_and_anonymization():
    org = "ORG-KARIS-RETAIL"
    user_id = "USER-PRIVACY-101"

    # 1. Update Granular Consent
    consent = privacy_gdpr_engine.update_privacy_consent(user_id, org, "MARKETING_COMMUNICATIONS", False)
    assert consent["is_granted"] is False

    # 2. Data Export across 12 Verticals
    healthcare_service.register_patient(user_id, "O+")
    export = privacy_gdpr_engine.export_customer_personal_data(user_id, org)
    assert export["export_format"] == "JSON_STRUCTURED"
    assert export["export_status"] == "COMPLETED"

    # 3. GDPR / Kenya DPA Right-to-be-Forgotten Anonymization (Rule 9 Preserved)
    anon = privacy_gdpr_engine.execute_right_to_be_forgotten_anonymization(user_id, "KENYA_DPA_DELETION_REQUEST", "ADMIN-01", org)
    assert anon["anonymized_alias_code"].startswith("ANONYMIZED-USER-")
    assert anon["ledger_integrity_status"] == "LEDGER_HASHES_PRESERVED_INTACT"

    # Verify patient profile was scrubbed while audit anchor stays clean
    pat = next((p for p in healthcare_service.patients.values() if p["identity_id"] == user_id), None)
    if pat:
        assert pat["blood_group"] == "SCRUBBED"

    audit_res = audit_engine.verify_ledger_chain()
    assert audit_res["status"] == "VERIFIED_CLEAN"

def test_chaos_engineering_and_fault_injection_resilience():
    org = "ORG-KARIS-RETAIL"
    drill = chaos_engine.run_automated_chaos_resilience_drill(
        "SIMULATED_DATABASE_SLAVE_DISCONNECT", "UNIVERSAL_LEDGER_ENGINE", 15, org
    )
    assert drill["drill_status"] == "COMPLETED_HEALED_VIA_DLQ"
    assert drill["dlq_events_recovered_count"] >= 1
    assert drill["ledger_integrity_post_drill"] == "VERIFIED_CLEAN"

def test_multi_warehouse_serial_tracking_and_weather_aware_dispatch():
    org = "ORG-KARIS-FARM"
    # 1. Serial Crate Tracking
    serial = warehouse_weather_engine.register_warehouse_serial_crate(
        "PROD-AVO-01", "BATCH-01", "WH-MACHAKOS-MAIN", org, "USER-FARMER-01"
    )
    assert serial["serial_barcode"].startswith("SN-AVO-CRATE-2026-")
    assert serial["item_status"] == "AVAILABLE_IN_WAREHOUSE"

    # 2. Weather-Aware Route Proximity Dispatching (Heavy storm check)
    weather_disp = warehouse_weather_engine.optimize_weather_aware_logistics_dispatch(
        "ORD-WEATHER-99", "Machakos Depot", "Mlolongo Hub", 10.0, "HEAVY_RAINFALL_STORM", "ORG-KARIS-RETAIL"
    )
    assert weather_disp["selected_vehicle_type"] == "REFRIGERATED_TRUCK"
    assert weather_disp["weather_surge_multiplier"] == 1.35
    assert "Heavy storm rainfall detected" in weather_disp["ai_weather_rationale"]
