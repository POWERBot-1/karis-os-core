import threading
import time
from typing import Dict
from src.core.ledger_engine import ledger_engine
from src.core.event_bus import event_bus
from src.core.wallet_engine import wallet_engine
from src.core.dlq_healing import dlq_engine

class PrometheusObservabilityEngine:
    """
    KARIS OS™ Prometheus Telemetry & Observability Engine (Section 40.7 & 47.3).
    Tracks API latency, double-entry ledger velocity across asset classes, event counts, and system health.
    Exposes metrics in Prometheus plain-text exposition format (`/metrics`).
    """
    def __init__(self):
        self.http_requests_total: Dict[str, int] = {}
        self.http_request_durations: Dict[str, list[float]] = {}
        self.start_time = time.time()
        self._lock = threading.Lock()

    def record_http_request(self, endpoint: str, method: str, status_code: int, duration_sec: float):
        with self._lock:
            key = f'{endpoint}_{method}_{status_code}'
            self.http_requests_total[key] = self.http_requests_total.get(key, 0) + 1
            if endpoint not in self.http_request_durations:
                self.http_request_durations[endpoint] = []
            self.http_request_durations[endpoint].append(duration_sec)
            if len(self.http_request_durations[endpoint]) > 500:
                self.http_request_durations[endpoint].pop(0)

    def generate_prometheus_metrics(self) -> str:
        with self._lock:
            lines = [
                "# HELP karis_platform_uptime_seconds Total seconds since KARIS OS booted",
                "# TYPE karis_platform_uptime_seconds gauge",
                f"karis_platform_uptime_seconds {round(time.time() - self.start_time, 2)}",
                "",
                "# HELP karis_ledger_entries_total Total double-entry movements recorded in Universal Ledger",
                "# TYPE karis_ledger_entries_total counter",
                f"karis_ledger_entries_total {len(ledger_engine.get_entries())}",
                "",
                "# HELP karis_event_store_total Total immutable domain events published across all verticals",
                "# TYPE karis_event_store_total counter",
                f"karis_event_store_total {len(event_bus.get_event_store())}",
                "",
                "# HELP karis_active_wallets_total Total isolated multi-asset wallets tracked",
                "# TYPE karis_active_wallets_total gauge",
                f"karis_active_wallets_total {len(wallet_engine.wallets)}",
                "",
                "# HELP karis_dlq_pending_total Total failed event dispatches currently in Dead-Letter Queue",
                "# TYPE karis_dlq_pending_total gauge",
                f"karis_dlq_pending_total {dlq_engine.get_dlq_status_summary()['pending_dead_letters']}",
                ""
            ]

            lines.append("# HELP karis_http_requests_total Total HTTP requests processed by API Gateway")
            lines.append("# TYPE karis_http_requests_total counter")
            for k, count in self.http_requests_total.items():
                ep, method, status = k.split("_", 2)
                lines.append(f'karis_http_requests_total{{endpoint="{ep}",method="{method}",status="{status}"}} {count}')

            lines.append("")
            return "\n".join(lines)

    def get_json_telemetry_summary(self) -> Dict:
        entries = ledger_engine.get_entries()
        events = event_bus.get_event_store()
        asset_dist = {}
        for en in entries:
            asset_dist[en.currency] = asset_dist.get(en.currency, 0.0) + en.amount

        return {
            "telemetry_engine_status": "ONLINE_ACTIVE_SCRAPING",
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "total_ledger_entries": len(entries),
            "total_domain_events": len(events),
            "total_active_wallets": len(wallet_engine.wallets),
            "ledger_volume_by_asset": asset_dist,
            "prometheus_scrape_url": "/metrics"
        }

metrics_engine = PrometheusObservabilityEngine()
