# KARIS OS™ Version 1.0.0-PROD-V1 — Cloud Infrastructure Credentials & Emergency Recovery Vault

**Document Version:** 15.0.0-PROD-V1 (`Cloud SRE Track`)  
**Target Audience:** Site Reliability Engineers (`SRE`), Cloud SRE Supervisors & Emergency Incident Commanders  
**Enforces:** Section 45 (`Multi-Region High Availability Clusters`) and Section 44 (`Disaster Recovery & Replay`)

---

## 1. Multi-Region Cloud Account Topology (`Africa/Nairobi Primary & Coastal Edge Mesh`)

KARIS OS™ runs across a distributed active-active regional cloud topology (`src/observability/ha_failover.py`). Below is the secure account matrix and recovery contact protocols:

| Region Node Code | Cloud Provider & Region | Cluster Identifier & Kubernetes Context | Emergency SRE Role & Vault Ref |
| :--- | :--- | :--- | :--- |
| `CLUSTER-NAIROBI-MAIN` | **AWS EKS (`af-south-1` Cape Town / Nairobi Edge)** | `arn:aws:eks:af-south-1:998877665544:cluster/karis-os-nairobi-core` | `vault:secret/data/karis-os/cloud#aws_eks_nairobi_admin` |
| `CLUSTER-MACHAKOS-EDGE` | **Private Kubernetes Edge Cluster (`Machakos Hub`)** | `k8s-context: karis-edge-machakos-01@192.168.100.10:6443` | `vault:secret/data/karis-os/cloud#private_k8s_machakos_admin` |
| `CLUSTER-MOMBASA-DR` | **Google GKE (`europe-west1` / Mombasa Coastal Edge)** | `gke_karis-os-prod_europe-west1_karis-dr-mombasa` | `vault:secret/data/karis-os/cloud#gke_mombasa_dr_admin` |

---

## 2. Emergency Root & Break-Glass Recovery Protocol (`Rule 10 & Section 38`)

If a catastrophic IAM lock-out, cloud account compromise, or primary data center partition occurs (`e.g., Nairobi Main offline during a 2,400 ops/sec traffic surge`), execute our strict **Emergency Break-Glass Protocol**:

### **A. Multi-Factor Break-Glass Root Authorization:**
1. **Hardware Root Security Key (`YubiKey 5 NFC / FIDO2`):** Held physically by `PLATFORM_ADMINISTRATOR` (`CFO / CISO`) inside a fireproof safe (`Vault Box Ref: SAF-NBO-01`).
2. **M-Pesa Biometric OTP Authorization:** Requires dual-authorization PIN generation via Safaricom M-Pesa corporate break-glass OTP (`Paybill 888880 Emergency Admin Channel`).

### **B. Instant Cluster Failover Execution (`Terminal Runbook`):**
To execute an immediate break-glass failover from `CLUSTER-NAIROBI-MAIN` to `CLUSTER-MACHAKOS-EDGE` from any backup command post:

```bash
# 1. Authenticate to HashiCorp Vault using emergency YubiKey FIDO2 token
export VAULT_TOKEN=$(op item get "Emergency_Karis_Vault_Token" --fields label=password)

# 2. Extract Machakos Edge K8s Kubeconfig into safe temporary context
op item get "Machakos_K8s_Kubeconfig" --fields label=notes > /tmp/emergency_kubeconfig.yaml
export KUBECONFIG=/tmp/emergency_kubeconfig.yaml

# 3. Trigger immediate geographic failover via HaFailoverEngine script
cd /home/user/karis-os-core
PYTHONPATH=. python3 -c '
from src.observability.ha_failover import ha_failover_engine
rec = ha_failover_engine.evaluate_cluster_health_and_execute_failover(
    failed_node_code="CLUSTER-NAIROBI-MAIN",
    promoted_node_code="CLUSTER-MACHAKOS-EDGE",
    trigger_reason="Emergency Break-Glass Root Failover execution under Section 45.3"
)
print("✔ EMERGENCY FAILOVER EXECUTED TO:", rec["promoted_node_code"])
print("✔ LEDGER CONTINUITY VERIFIED:", rec["ledger_continuity_status"])
'
```

---

## 3. Point-in-Time Recovery (`PITR`) Cold-Vault Restoration Protocol

If the active cloud database (`karis_os_prod`) experiences physical corruption or tampering (`Rule 9` breach), execute cold-vault restoration:

```bash
# 1. Pull latest SHA-256 sealed PITR snapshot from secure S3 / Cold Vault
aws s3 cp s3://karis-os-cold-vault-africa-nairobi/encrypted/PITR-SNAP-LATEST.json.enc /tmp/snapshot.json.enc --sse aws:kms

# 2. Decrypt snapshot using SRE Master GPG / OpenSSL Key
openssl enc -d -aes-256-gcm -in /tmp/snapshot.json.enc -out /home/user/karis-os-core/backups/PITR-SNAP-LATEST.json -pass pass:${PITR_MASTER_DECRYPTION_KEY}

# 3. Verify SHA-256 checksum and execute Event Sourcing Replay (`Section 9.4`)
PYTHONPATH=. python3 -c '
from src.observability.disaster_recovery import dr_engine
from src.core.event_replay import event_replay_engine
# Verify hash clean
print(dr_engine.verify_snapshot_checksum("PITR-SNAP-LATEST")["status"])
# Reconstruct exact multi-asset wallet state bit-for-bit
rep = event_replay_engine.reconstruct_system_state_from_events()
print("✔ DETERMINISTIC STATE REBUILT:", rep["status"], "| Replayed Events:", rep["events_replayed_count"])
'
```

All emergency recovery procedures and break-glass authorization keys are documented and active under strict double-entry protection.
