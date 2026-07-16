# KARIS OS™ Version 1.0.0-PROD-V1 — Phase 3: SRE Chaos Resilience & Disaster Recovery PITR Guide

**Document Version:** 4.0.0-PROD-V1  
**Target Audience:** Site Reliability Engineers (`SRE`), Cloud Architects & Database Administrators  
**Enforces:** Section 37.5 (`PITR Snapshots & Replay`), Section 40.8 (`High Availability Clusters`), and Section 44 (`Chaos Resilience Drills`)

---

## 1. Executive SRE & Resilience Architecture

To maintain 100% continuous uptime and immutable double-entry ledger verification (`Rule 9`) across Kenya and East Africa (`Africa/Nairobi`), KARIS OS™ integrates an active-active high availability mesh (`HaActiveActiveGeographicFailoverEngine`) alongside continuous point-in-time cryptographic snapshots (`DisasterRecoveryEngine`).

```
+---------------------------------------------------------------------------------------------------+
|                           ACTIVE-ACTIVE REGIONAL CLUSTER MESH (`Section 45.3`)                    |
|   [Nairobi Core Hub (`CLUSTER-NAIROBI-MAIN`)]   <==>   [Machakos Edge Hub (`CLUSTER-MACHAKOS`)]   |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
|                        HA GEOGRAPHIC FAILOVER ORCHESTRATOR (`Section 40.8`)                       |
|   Monitored Heartbeat status: `ONLINE_HEALTHY`. Upon primary node timeout or error rate surge:    |
|   -> Promotes standby node (`100% traffic rerouting`) with `100PCT_LEDGER_CONTINUITY_VERIFIED`   |
+---------------------------------------------------------------------------------------------------+
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         ▼                                        ▼                                        ▼
┌────────────────────────────────┐  ┌────────────────────────────────┐  ┌────────────────────────────────┐
│   POINT-IN-TIME RECOVERY PITR  │  │  DEAD-LETTER QUEUE SELF-HEALING│  │  EVENT SOURCING REPLAY ENGINE  │
│  `/backups/PITR-SNAP-*.json`   │  │  Exponential backoff recovery  │  │  Deterministic state rebuilding│
│  Exact SHA-256 File Checksum   │  │  `DLQ_EVENT_RECOVERED`         │  │  `reconstruct_system_state()`  │
└────────────────────────────────┘  └────────────────────────────────┘  └────────────────────────────────┘
```

---

## 2. Active-Active Geographic Failover Runbook (`Section 45.3`)

### **A. Pre-Configured Regional Nodes (`_seed_default_nodes`):**
1. **`CLUSTER-NAIROBI-MAIN`:** Nairobi Core Data Center (`AWS EKS Africa`, Baseline 2,400 active connections).
2. **`CLUSTER-MACHAKOS-EDGE`:** Machakos Agri & Retail Edge Hub (`Private Kubernetes Cluster`, Baseline 850 active connections).
3. **`CLUSTER-MOMBASA-DR`:** Mombasa Coastal Disaster Recovery (`Google GKE`, Baseline 150 active connections).

### **B. Executing Geographic Failover in Code / Terminal:**
When a regional network split or primary data center hardware failure occurs, execute:
```bash
cd /home/user/karis-os-core
PYTHONPATH=. python3 -c '
from src.observability.ha_failover import ha_failover_engine
rec = ha_failover_engine.evaluate_cluster_health_and_execute_failover(
    failed_node_code="CLUSTER-NAIROBI-MAIN",
    promoted_node_code="CLUSTER-MACHAKOS-EDGE",
    trigger_reason="Primary data center heartbeat timeout during high-throughput drill"
)
print("✔ FAILOVER ID:", rec["failover_id"])
print("✔ REROUTED TRAFFIC:", rec["traffic_rerouted_pct"], "%")
print("✔ LEDGER CONTINUITY:", rec["ledger_continuity_status"])
'
```

### **Outcome (`Zero Human Database Intervention`):**
* Primary node marked `OFFLINE_FAILED`.
* Standby node `CLUSTER-MACHAKOS-EDGE` inherits all active connections.
* Double-entry ledger verification anchor (`last_hash`) preserved intact across the promoted node (`Rule 9`).

---

## 3. Point-in-Time Recovery (`PITR`) & Cryptographic Checksum Runbook (`Section 37.5`)

### **A. Creating a Verified PITR Snapshot:**
Our `DisasterRecoveryEngine` dumps every multi-asset wallet balance, double-entry ledger transfer, and domain event into an exact JSON snapshot file inside `/home/user/karis-os-core/backups/PITR-SNAP-*.json` and seals it with a SHA-256 checksum:

```bash
cd /home/user/karis-os-core
PYTHONPATH=. python3 -c '
from src.observability.disaster_recovery import dr_engine
snap = dr_engine.create_point_in_time_snapshot()
print("✔ SNAPSHOT CREATED:", snap["snapshot_id"])
print("✔ FILE PATH:", snap["snapshot_file_path"])
print("✔ SHA-256 CHECKSUM:", snap["sha256_checksum"])
'
```

### **B. Verifying Checksum Integrity Against Tampering:**
To verify that a backup snapshot on disk has not been corrupted or altered prior to restoration:
```bash
PYTHONPATH=. python3 -c '
from src.observability.disaster_recovery import dr_engine
chk = dr_engine.verify_snapshot_checksum("PITR-SNAP-1CAF8B2E") # Use target ID
print("✔ CHECKSUM STATUS:", chk["status"], "| MESSAGE:", chk["message"])
'
```

---

## 4. Deterministic Event Sourcing Replay Runbook (`Section 9.4`)

Because KARIS OS™ enforces **Rule 1 (`No Event -> No State Change`)**, every historical state modification is preserved as an immutable domain event (`event_store`). If in-memory balances are wiped out or if a new analytical read-model needs state reconstruction from scratch, our `EventSourcingReplayEngine` recomputes exact multi-asset wallet balances from pure event history:

```bash
cd /home/user/karis-os-core
PYTHONPATH=. python3 -c '
from src.core.event_replay import event_replay_engine
rep = event_replay_engine.reconstruct_system_state_from_events()
print("✔ REPLAY COMPLETED:", rep["replay_id"])
print("✔ REPLAYED EVENTS:", rep["events_replayed_count"])
print("✔ RECONSTRUCTED WALLETS:", rep["reconstructed_wallets_count"])
'
```

---

## 5. Automated Master Verification Command

To run all 3 SRE resilience drills (`Geographic Failover`, `PITR Snapshot Creation/Verification`, and `Event Sourcing Replay`) right inside your terminal:

```bash
cd /home/user/karis-os-core
PYTHONPATH=. python3 run_phase_3_dr_chaos_execution.py
```

Your cloud infrastructure and database clusters now possess verifiable, SHA-256 sealed disaster recovery and geographic failover capability across East Africa.
