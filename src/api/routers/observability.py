from fastapi import APIRouter, Response
from src.observability.metrics import metrics_engine

router = APIRouter(tags=["Prometheus Observability & Telemetry (Section 40.7)"])

@router.get("/metrics", response_class=Response)
def get_prometheus_metrics():
    """Exposes real-time Prometheus plain-text exposition metrics (`karis_http_requests_total`, `karis_ledger_entries_total`, etc.)."""
    content = metrics_engine.generate_prometheus_metrics()
    return Response(content=content, media_type="text/plain")

@router.get("/api/v1/observability/status")
def get_telemetry_status():
    """Returns JSON telemetry summary across uptime, active wallets, and asset distribution."""
    return metrics_engine.get_json_telemetry_summary()
