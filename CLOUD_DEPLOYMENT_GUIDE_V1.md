# KARIS OS™ Version 1.0.0-PROD-V1 — Cloud Deployment & Kubernetes Infrastructure Guide (`Track 1`)

**Document Version:** 1.0.0-PROD-V1  
**Target Architecture:** AWS EKS, Google GKE, Azure AKS & East African Cloud Clusters (`Africa/Nairobi`)  
**Enforces:** Section 40 (`DevOps, Container Orchestration, CI/CD & Observability`)

---

## 1. Executive Deployment Overview

KARIS OS™ is engineered as an **API-First, Cloud-Native, and Event-Driven Operating System Kernel** (`Sections 1–8`) with 15 plug-and-play industry verticals. Every component is containerized using Docker (`Dockerfile`) and orchestrated via Kubernetes (`k8s/deployment.yaml`).

```
+---------------------------------------------------------------------------------------------------+
|                            EXTERNAL PRODUCTION TRAFFIC (`HTTPS / TLS`)                            |
|       api.karis-os.ke (REST API & Webhooks)  •  portal.karis-os.ke (38-Tab Web Portal)            |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
|                        KUBERNETES INGRESS CONTROLLER (`LetsEncrypt SSL`)                          |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
|                           KARIS API GATEWAY DEPLOYMENT (`4 -> 16 Pods`)                           |
|       [Pod 1: Uvicorn API]     [Pod 2: Uvicorn API]     [Pod 3: Uvicorn API]     [Pod 4: Uvicorn API] |
|       Zero-Downtime Rolling Update (`maxSurge: 1, maxUnavailable: 0`)                             |
+---------------------------------------------------------------------------------------------------+
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         ▼                                        ▼                                        ▼
┌────────────────────────────────┐  ┌────────────────────────────────┐  ┌────────────────────────────────┐
│      MANAGED POSTGRESQL 16     │  │       MANAGED REDIS 7          │  │     AUTONOMOUS HPA AUTOSCALER  │
│  (`karis_os_prod` DB Instance) │  │  (Event Pub/Sub & DLQ Cache)   │  │  Scrapes `/metrics` (`ops/sec`)│
│  51 DDL Schemas / 130 Tables   │  │  Low-latency session storage   │  │  Scales Pods during surges     │
└────────────────────────────────┘  └────────────────────────────────┘  └────────────────────────────────┘
```

---

## 2. Option A: Single-Node & Docker Compose Deployment (`Staging / Edge Hubs`)

For edge deployments (such as `Machakos County Agricultural Aggregation Hub` or `Mlolongo Retail Supermarket Center`), you can launch the complete self-contained stack in seconds using Docker Compose:

### **Step 1: Set Environment Variables**
Create a `.env` file in the root directory (`/home/user/karis-os-core/.env`):
```ini
# Platform Metadata
PLATFORM_NAME="KARIS OS™"
PLATFORM_VERSION="1.0.0-PROD-V1"
DEFAULT_CURRENCY="KES"
DEFAULT_COUNTRY="KE"

# Security & API Keys
JWT_SECRET_KEY="SuperSecretProductionJwtKey2026_KarisOS_EastAfrica"
PALPLUS_PAYMENT_LINK_ID="6e8de0bc-1284-4bba-a5de-f886665bf18f"

# Database & Cache Credentials
POSTGRES_DB="karis_os_prod"
POSTGRES_USER="karis_admin"
POSTGRES_PASSWORD="SecureKarisPassword2026!"
DATABASE_URL="postgresql://karis_admin:SecureKarisPassword2026!@karis-postgres:5432/karis_os_prod"
REDIS_URL="redis://karis-redis:6379/0"
```

### **Step 2: Launch with Docker Compose**
```bash
cd /home/user/karis-os-core
docker-compose up --build -d
```

### **Automated Boot Sequence Executed by Docker Compose:**
1. **`karis-postgres`:** Starts PostgreSQL 16 Alpine and waits for `pg_isready` health check.
2. **`karis-redis`:** Starts Redis 7 Alpine and waits for `ping` response.
3. **`karis-migrator`:** Runs `python3 -m src.db.migrator --migrate`. Sequentially executes all **51 DDL migration scripts (`001 -> 051`)**, creating 130 tables with strict double-entry immutability triggers (`prevent_ledger_mutation()`).
4. **`karis-seeder`:** Runs `python3 -m src.db.seed_data --seed`. Populates global identities, multi-tenant organizations, wallets (`Rule 5`), and flagship produce QR codes (`KARIS-TRACE-QR-...`).
5. **`karis-api-gateway`:** Boots Uvicorn with `4 multi-processing workers` listening on port `8000`.

To check logs or verify health:
```bash
docker-compose ps
docker-compose logs -f karis-api-gateway
curl http://localhost:8000/docs
```

---

## 3. Option B: Enterprise Kubernetes Deployment (`Production EKS / GKE / AKS`)

For high-availability regional production (`Africa/Nairobi`), deploy KARIS OS™ using our production Kubernetes manifest (`k8s/deployment.yaml`).

### **Step 1: Create Namespace & Secrets**
Ensure your Kubernetes cluster has `kubectl` connected, then create the production namespace and secrets:
```bash
kubectl create namespace karis-os-prod

# Create Database, Redis & API Secrets
kubectl create secret generic karis-os-secrets \
  --namespace=karis-os-prod \
  --from-literal=DATABASE_URL="postgresql://karis_admin:SecureKarisPassword2026!@rds-endpoint.aws.internal:5432/karis_os_prod" \
  --from-literal=REDIS_URL="redis://elasticache.aws.internal:6379/0" \
  --from-literal=JWT_SECRET="SuperSecretProductionJwtKey2026_KarisOS_EastAfrica" \
  --from-literal=PALPLUS_API_KEY="palplus_live_key_9901"
```

### **Step 2: Apply Kubernetes Configuration & Deployment Manifest**
```bash
cd /home/user/karis-os-core
kubectl apply -f k8s/deployment.yaml
```

### **Step 3: Run Database Migrator Job inside Kubernetes**
To run the schema migrations and seeder across your managed cloud PostgreSQL database before cutting over traffic:
```bash
kubectl run karis-migrator-job \
  --namespace=karis-os-prod \
  --image=karis-os-core:1.0.0-PROD-V1 \
  --env="DATABASE_URL=postgresql://karis_admin:SecureKarisPassword2026!@rds-endpoint.aws.internal:5432/karis_os_prod" \
  --command -- python3 -m src.db.migrator --migrate

# Check migrator completion
kubectl logs -f job/karis-migrator-job --namespace=karis-os-prod
```

---

## 4. Enabling Autonomous Pod Autoscaling (`Section 40.3 & 40.4`)

KARIS OS™ features an intelligent **Kubernetes Horizontal Pod Autoscaler (`HPA`) Engine** (`src/observability/k8s_autoscaler.py`) that monitors request velocity (`ops/sec`) and CPU utilization (`/metrics`).

When checkouts across Supermarket POS terminals, prediction entries on Power BOT X, or solar PAYG token payments spike above threshold (`> 80% CPU` or `> 1,500 ops/sec`), the autoscaler dynamically scales replica pods:
```text
[POD AUTOSCALING EVENT]
• Baseline Replicas: 4 Pods
• Traffic Velocity Detected: 2,213.2 operations / second
• HPA Decision: SCALE OUT -> Increasing to 16 Pod Replicas
• Audit Log: PODS_SCALED_OUT_TRAFFIC_SURGE (`Rule 6 Event Published`)
```

To verify the live autoscaler status in your Kubernetes cluster:
```bash
kubectl get hpa --namespace=karis-os-prod
kubectl get pods --namespace=karis-os-prod -o wide
```

---

## 5. Live Production Health Checklist

Before signing off on production cutover, run our automated verification curl commands:

1. **Verify API Gateway & Swagger Documentation:**
   ```bash
   curl -I https://api.karis-os.ke/docs
   # Expected: HTTP/2 200 OK
   ```
2. **Verify Prometheus Telemetry Scraper Endpoint (`Section 40.7`):**
   ```bash
   curl -s https://api.karis-os.ke/api/v1/observability/metrics | grep karis_http_requests_total
   ```
3. **Verify Active PalPlus Payment Link Endpoint (`Section 51`):**
   ```bash
   curl -s https://api.karis-os.ke/api/v1/payment-links/active-temporary | grep "6e8de0bc-1284-4bba-a5de-f886665bf18f"
   ```

You are now 100% live and operational on cloud Kubernetes!
