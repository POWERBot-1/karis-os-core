import pytest
from src.observability.metrics import metrics_engine
from src.observability.disaster_recovery import dr_engine
from src.core.event_replay import event_replay_engine
from src.core.event_bus import event_bus
from src.domain.models import EventCategory, EventPayload

def test_prometheus_observability_metrics():
    metrics_engine.record_http_request("/api/v1/orders", "POST", 201, 0.045)
    metrics_engine.record_http_request("/api/v1/wallets", "GET", 200, 0.012)
    
    prom_text = metrics_engine.generate_prometheus_metrics()
    assert "karis_platform_uptime_seconds" in prom_text
    assert "karis_ledger_entries_total" in prom_text
    assert 'karis_http_requests_total{endpoint="/api/v1/orders",method="POST",status="201"} 1' in prom_text

    status_summary = metrics_engine.get_json_telemetry_summary()
    assert status_summary["telemetry_engine_status"] == "ONLINE_ACTIVE_SCRAPING"

def test_disaster_recovery_pitr_snapshots_and_checksum_verification():
    org = "ORG-KARIS-RETAIL"
    snap = dr_engine.create_point_in_time_snapshot(org, "POINT_IN_TIME_PITR", "ADMIN-01")
    assert snap["status"] == "VERIFIED_CLEAN"
    assert snap["sha256_checksum"] != ""

    verify_res = dr_engine.verify_snapshot_checksum(snap["snapshot_id"])
    assert verify_res["status"] == "VERIFIED_CLEAN"
    assert verify_res["sha256_checksum"] == snap["sha256_checksum"]

def test_event_sourcing_replay_and_state_reconstruction():
    # Publish simulated delta events
    event_bus.publish(EventPayload(
        event_type="LEDGER_ENTRY_RECORDED",
        event_category=EventCategory.TREASURY,
        actor_identity_id="SYSTEM",
        organization_id="ORG-TEST",
        correlation_id="TX-101",
        source_module="LEDGER_ENGINE",
        payload={"debit_wallet_id": "W-CUST-1", "credit_wallet_id": "W-MERCH-1", "amount": 5000.0}
    ))
    event_bus.publish(EventPayload(
        event_type="TOKEN_MINTED",
        event_category=EventCategory.CURRENCY,
        actor_identity_id="TREASURY",
        organization_id="ORG-TEST",
        correlation_id="TX-102",
        source_module="TREASURY_ENGINE",
        payload={"target_wallet_id": "W-CUST-1-KRT", "amount": 250.0}
    ))

    replay_res = event_replay_engine.reconstruct_system_state_from_events(organization_id="ORG-TEST")
    assert replay_res["status"] == "SUCCESS"
    assert replay_res["events_replayed_count"] >= 2
    assert "W-CUST-1" in replay_res["reconstructed_balances_sample"]
    assert replay_res["reconstructed_balances_sample"]["W-CUST-1"] == -5000.0
    assert replay_res["reconstructed_balances_sample"]["W-CUST-1-KRT"] == 250.0
