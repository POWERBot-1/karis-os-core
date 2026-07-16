import threading
import time
import uuid
from typing import Dict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus
from src.observability.metrics import metrics_engine

class RateLimitBucket:
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_rate = refill_rate_per_sec
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(float(self.capacity), self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

class EnterpriseSecurityMiddleware(BaseHTTPMiddleware):
    """
    KARIS OS™ Enterprise Security & API Gateway Middleware (Section 36.1, 38.2 & 46).
    Enforces Correlation ID injection (`X-Correlation-ID`), Rate Limiting (Token Bucket),
    CORS / Security Headers, and Prometheus latency tracking.
    """
    def __init__(self, app):
        super().__init__(app)
        self.buckets: Dict[str, RateLimitBucket] = {}
        self._lock = threading.Lock()

    def _get_bucket(self, client_ip: str, endpoint: str) -> RateLimitBucket:
        with self._lock:
            key = f"{client_ip}:{endpoint}"
            if key not in self.buckets:
                # Stricter rate limits for authentication/OTP endpoints
                if "/auth/" in endpoint or "/otp/" in endpoint:
                    self.buckets[key] = RateLimitBucket(capacity=20, refill_rate_per_sec=0.2)
                else:
                    self.buckets[key] = RateLimitBucket(capacity=200, refill_rate_per_sec=5.0)
            return self.buckets[key]

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "127.0.0.1"
        endpoint = request.url.path

        # 1. Correlation ID Injection (Rule 1 & Rule 8 Traceability)
        correlation_id = request.headers.get("X-Correlation-ID", f"REQ-{uuid.uuid4().hex[:8].upper()}")
        request.state.correlation_id = correlation_id

        # 2. Rate Limiting Check (Skip metrics/static/docs)
        if not endpoint.startswith("/metrics") and not endpoint.startswith("/docs") and not endpoint.startswith("/portal"):
            bucket = self._get_bucket(client_ip, endpoint)
            if not bucket.consume(1):
                # Emit Rate Limit Exceeded event
                ev = EventPayload(
                    event_type="API_GATEWAY_RATE_LIMIT_EXCEEDED",
                    event_category=EventCategory.GOVERNANCE,
                    actor_identity_id="SYSTEM_GATEWAY_MIDDLEWARE",
                    organization_id="SYSTEM_CORE_ORG",
                    correlation_id=correlation_id,
                    source_module="API_GATEWAY_SECURITY_MIDDLEWARE",
                    payload={
                        "client_ip": client_ip,
                        "endpoint_requested": endpoint,
                        "rate_limit_bucket": f"{client_ip}:{endpoint}",
                        "requests_seen_in_window": bucket.capacity
                    }
                )
                event_bus.publish(ev)
                return JSONResponse(
                    status_code=429,
                    content={"error": "Too Many Requests", "message": "API Gateway rate limit exceeded. Please slow down request velocity under Section 36.1 security controls.", "correlation_id": correlation_id},
                    headers={"Retry-After": "5", "X-Correlation-ID": correlation_id}
                )

        # 3. Execute Request
        response = await call_next(request)
        duration = time.time() - start_time

        # 4. Record Prometheus Telemetry
        metrics_engine.record_http_request(endpoint, request.method, response.status_code, duration)

        # 5. Attach Enterprise Security & Traceability Headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Platform-Version"] = "KARIS-OS-1.0.0-PROD-V1"
        return response
