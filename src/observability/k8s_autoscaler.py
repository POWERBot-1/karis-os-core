import uuid
from datetime import datetime, timezone
from typing import Dict
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus

class KubernetesHpaAutoscalingEngine:
    """
    KARIS OS™ Multi-Cloud Kubernetes Autonomous Container Orchestration Engine (Section 40.3 & 40.4).
    Monitors microservice deployments (`karis-api-gateway`, `karis-event-worker`, `karis-ledger-engine`),
    evaluates real-time CPU utilization and request velocity (`ops/sec`), and dynamically scales pod replicas via HPA.
    """
    def __init__(self):
        self.hpa_logs: Dict[str, Dict] = {}
        self.deployments: Dict[str, int] = {
            "karis-api-gateway": 4,
            "karis-event-worker": 2,
            "karis-ledger-engine": 4,
            "karis-ai-gateway": 2
        }

    def evaluate_traffic_load_and_scale_pods(
        self,
        request_velocity_ops_per_sec: float = 2380.0,
        cpu_utilization_pct: float = 88.5,
        target_service: str = "karis-api-gateway",
        cluster_node_code: str = "CLUSTER-NAIROBI-MAIN",
        organization_id: str = "SYSTEM_CORE_ORG"
    ) -> Dict:
        prev_replicas = self.deployments.get(target_service, 4)

        if request_velocity_ops_per_sec > 2000.0 or cpu_utilization_pct > 80.0:
            new_replicas = min(prev_replicas * 4, 32)
            action = "PODS_SCALED_OUT_TRAFFIC_SURGE"
            reason = f"ALERT: High traffic surge ({request_velocity_ops_per_sec:.1f} ops/sec, {cpu_utilization_pct}% CPU). Scaled out from {prev_replicas} to {new_replicas} pod replicas across multi-cloud cluster!"
        elif request_velocity_ops_per_sec < 200.0 and cpu_utilization_pct < 30.0 and prev_replicas > 4:
            new_replicas = max(prev_replicas // 2, 4)
            action = "PODS_SCALED_IN_LOW_LOAD"
            reason = f"Low traffic detected ({request_velocity_ops_per_sec:.1f} ops/sec). Scaled in pods from {prev_replicas} to {new_replicas}."
        else:
            new_replicas = prev_replicas
            action = "OPTIMAL_REPLICAS_MAINTAINED"
            reason = f"Traffic load ({request_velocity_ops_per_sec:.1f} ops/sec, {cpu_utilization_pct}% CPU) within normal HPA operating parameters ({prev_replicas} pods)."

        self.deployments[target_service] = new_replicas
        log_id = f"HPA-LOG-{uuid.uuid4().hex[:8].upper()}"

        record = {
            "hpa_log_id": log_id,
            "cluster_node_code": cluster_node_code,
            "target_microservice_deployment": target_service,
            "previous_replicas": prev_replicas,
            "new_replicas": new_replicas,
            "cpu_utilization_pct": cpu_utilization_pct,
            "request_velocity_ops_per_sec": request_velocity_ops_per_sec,
            "scaling_action": action,
            "scaling_reason": reason,
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }
        self.hpa_logs[log_id] = record

        if action != "OPTIMAL_REPLICAS_MAINTAINED":
            ev = EventPayload(
                event_type="K8S_CONTAINER_REPLICAS_SCALED",
                event_category=EventCategory.GOVERNANCE,
                actor_identity_id="SYSTEM_K8S_HPA",
                organization_id=organization_id,
                correlation_id=log_id,
                source_module="KUBERNETES_HPA_AUTOSCALING_ENGINE",
                payload={
                    "hpa_log_id": log_id,
                    "cluster_node_code": cluster_node_code,
                    "target_microservice_deployment": target_service,
                    "previous_replicas": prev_replicas,
                    "new_replicas": new_replicas,
                    "cpu_utilization_pct": cpu_utilization_pct,
                    "request_velocity_ops_per_sec": request_velocity_ops_per_sec,
                    "scaling_action": action
                }
            )
            event_bus.publish(ev)

        return record

k8s_hpa_engine = KubernetesHpaAutoscalingEngine()
