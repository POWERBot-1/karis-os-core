# KARIS OS™ — Unified Enterprise & Digital Economy Platform
## Production Architecture, Executable Codebase & Engineering Runbook (`v1.0.0-PROD-V1`)

**KARIS OS™** is an AI-native, event-driven, modular Enterprise Operating System engineered to unify **Commerce, Agriculture, Retail, Eatery/Food Services, Logistics, Healthcare, Mobility, Lending, and Investment** into one intelligent, multi-tenant platform.

Instead of building fragmented software for separate vertical industries, KARIS OS™ establishes a unified infrastructure (`One Identity, One Multi-Asset Wallet Engine, One Universal Event Bus, One Double-Entry Ledger, and One AI Gateway`) upon which unlimited industry-specific solutions operate.

---

## 🚀 1. Quick Start & Execution Guide

### Option A: Local Python Execution (`Zero Dependencies`)
You can run the full multi-vertical simulations and start the live web dashboard right in your local environment using Python 3.13+:

```bash
# 1. Clone or enter the workspace
cd /home/user/karis-os-core

# 2. Run Database Migrations (001 -> 015 DDL Schemas)
PYTHONPATH=. python3 -m src.db.migrator --migrate

# 3. Seed Production East African Ecosystem & KARIS FARM™
PYTHONPATH=. python3 -m src.db.seed_data --seed

# 4. Execute the E2E Console Simulation across all 7 Verticals & Invariants
PYTHONPATH=. python3 run_enterprise_simulation.py

# 5. Start the Live API Gateway & Interactive Web Portal
PYTHONPATH=. uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
Once Uvicorn is running:
* **Interactive Enterprise Web Portal & Traceability Dashboard:** Open `http://localhost:8000/portal` (or `http://localhost:8000/`)
* **Live OpenAPI / Swagger Documentation:** Open `http://localhost:8000/docs`

### Option B: Docker & Container Orchestration (`Turnkey Stack`)
Deploy the full stack including PostgreSQL 16, Redis Cache, Database Migrations, Seeding Engine, and API Gateway:

```bash
# Start all services via Docker Compose
docker-compose up --build -d

# Check service health and live migration logs
docker-compose logs -f karis-migrator karis-seeder
```

### Option C: Cloud Kubernetes Deployment (`AWS EKS / GCP GKE / Azure AKS`)
Apply production Kubernetes manifests located inside `/k8s/`:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl get pods -n karis-os-prod
```

---

## 🏛️ 2. Comprehensive System Architecture & Directory Structure

```text
karis-os-core/
├── db/migrations/                         # 15 Chronological PostgreSQL DDL Migration Scripts
│   ├── 001_initial_identities_rbac.sql    # Identities, Organizations & RBAC Matrix (Section 7)
│   ├── 002_universal_ledger_wallets.sql   # Double-Entry Universal Ledger & Wallets (Rules 5, 8, 9)
│   ├── 003_event_bus_store.sql            # Immutable Event Store & Dispatch Status (Rules 1, 6)
│   ├── 004_commerce_and_inventory.sql     # Products, SKU Batches & Orders (Sections 14-17)
│   ├── 005_karis_farm_vertical.sql        # Farms, Crop Plans, Harvests & Traceability (Section 28)
│   ├── 006_rule_and_workflow_engine.sql   # Declarative Business Rules & Workflows (Rule 7)
│   ├── 007_treasury_and_lending.sql       # Treasury Reserves & Credit Scoring (Rule 3)
│   ├── 008_logistics_and_delivery.sql     # Delivery Zones, Riders & Escrow Payouts (Section 21 & Rule 4)
│   ├── 009_crm_and_call_center.sql        # Unified Customer Profiles & Tickets (Sections 23-24)
│   ├── 010_pos_and_retail.sql             # Retail Stores, POS Terminals & Dynamic Pricing (Sections 20, 30)
│   ├── 011_eatery_and_kds.sql             # Digital Menus & Kitchen Display System KDS (Section 29)
│   ├── 012_healthcare_and_emr.sql         # Clinics, Patients, EMR Notes & CHV Checks (Section 32)
│   ├── 013_mobility_and_rides.sql         # Drivers, Vehicles, Trip Lifecycle & Surge Pricing (Section 33)
│   ├── 014_investor_and_capital.sql       # Investment Pools, KYC Allocations & Return Distribution (Section 25)
│   ├── 015_analytics_and_audit.sql        # AI Risk Alerts & Audit Checkpoints (Sections 27, 38)
│   ├── 016_sales_force_automation.sql     # Field Agents, Outreach Visits & Referral Tracking (Section 22)
│   ├── 017_loyalty_incentives.sql         # Promotional Campaigns, Point Grants & KRT Multipliers (Section 26)
│   ├── 018_open_banking_cbdc_esg.sql      # Section 48: Wholesale CBDC, PSD2 Consents, EAC & ESG Carbon Credits
│   ├── 019_governance_compliance_aml.sql  # Section 38.8 & 47: Multi-Tier KYC, AML Structuring SAR & KRA eTIMS Tax
│   ├── 020_predictive_intelligence_forecasts.sql # Section 27.4: Demand Velocity Stockout Forecasts & Dynamic Pricing
│   ├── 021_disaster_recovery_snapshots.sql # Section 44.4 & 47.2: Disaster Recovery Point-in-Time Checkpoint Snapshots
│   ├── 022_emergency_ambulance_ai.sql     # Section 32.8 & 33.5: Emergency ALS/BLS Ambulance Fleet & Geodesic Dispatch
│   ├── 023_pos_ai_queue_shrinkage.sql     # Section 20.3 & 30.5: POS Queue Congestion Logs & Retail Shrinkage Audits
│   ├── 024_erp_tax_sync.sql               # Section 36.5 & 43.2: SAP S/4HANA Accounting Sync & Notification Templates
│   ├── 025_crm_intelligence.sql           # Section 23.4: AI CRM Churn Prediction, LTV & Win-Back Retention Grants
│   ├── 026_future_industries.sql          # Section 35.3: Education Edu-Pay, Tourism Safari & Real Estate Prop-Share
│   ├── 027_fraud_detection_ai.sql         # Section 38.6 & 27.1: AI Fraud Geodesic Impossible Travel & Velocity Checks
│   ├── 028_call_center_sla.sql            # Section 24.4: Call Center SLA Benchmarks & Supervisor Escalations
│   ├── 029_crop_insurance_iot.sql         # Section 34.4 & 28.5: Parametric Crop Insurance & IoT Agri-Sensor Telemetry
│   ├── 030_policy_control_api_keys.sql    # Section 43 & 47: Governance Policies, API Key Lifecycle & Dynamic Tax Rules
│   ├── 031_privacy_consent_gdpr.sql       # Section 38.7: Granular Consents, Data Export & GDPR/DPA Anonymization
│   ├── 032_chaos_resilience_drills.sql    # Section 44.2 & 40.7: Chaos Engineering & Fault Injection Resilience Suite
│   ├── 033_multi_warehouse_serial_tracking.sql # Section 15 & 21.5: Multi-Warehouse Barcodes & Weather-Aware Dispatch
│   ├── 034_sdk_generation_logs.sql        # Section 46.2: Python & TypeScript Client SDK Generation Logs
│   ├── 035_bi_executive_snapshots.sql     # Section 27.2 & 27.3: Unified BI Executive & Leadership Aggregation
│   ├── 036_cicd_quality_gates.sql         # Section 40.5 & 40.6: CI/CD Automated Deployment Quality Gates & Thresholds
│   ├── 037_offline_sync_queues.sql        # Section 41.5 & 20.2: POS & Mobile Offline Caching & Reconnect Sync
│   ├── 038_marketplace_split_commissions.sql # Section 14.3 & 17.2: Multi-Vendor Marketplace Split-Commission Allocations
│   ├── 039_regulatory_compliance_reports.sql # Section 35.4 & 38.8: Automated CBK AML/FIU & KRA Tax Compliance Filings
│   ├── 040_hardware_hsm_keys.sql          # Section 41.4 & 38.4: HSM Master Keys & NFC Biometric Payment Tokens
│   ├── 041_loyalty_tiers_network.sql      # Section 23.2 & 18: Loyalty Tier Upgrades & Cross-Merchant Redemptions
│   ├── 042_ha_geographic_failover.sql     # Section 40.8 & 45.3: Active-Active Cluster Nodes & Geographic Failover
│   ├── 043_mobile_passkey_push.sql        # Section 41.2, 41.3 & 26.5: Mobile FIDO2 Passkeys & APNS/FCM Push Tokens
│   ├── 044_ledger_reconciliation_sweeps.sql # Section 37.4 & 10.4: Double-Entry Ledger Reconciliation & Reversing Sweeps
│   ├── 045_k8s_container_orchestration.sql # Section 40.3 & 40.4: Kubernetes HPA Container Autoscaling Pod Replicas
│   ├── 046_escrow_dispute_clearing.sql    # Section 31.1 & 11.2: Multi-Party Escrow Holdings & Dispute Resolution Splits
│   ├── 047_supply_chain_bottlenecks.sql   # Section 27.4 & 13.4: AI Highway Transit Bottlenecks & Dynamic Route Bypass
│   └── 048_tax_holidays_tariffs.sql       # Section 43.1 & 43.2: Declarative Tax Holidays & Statutory Exemptions
│
├── schemas/events/                        # 64 Complete Draft-07 JSON Schema Event Contracts
│   ├── COMMERCE_ORDER_CREATED.json
│   ├── PAYMENT_CONFIRMED.json
│   ├── LEDGER_ENTRY_RECORDED.json
│   ├── TOKEN_MINTED.json
│   ├── DELIVERY_COMPLETED.json
│   ├── AGRICULTURE_HARVEST_COMPLETED.json
│   ├── LOGISTICS_RIDER_ASSIGNED.json
│   ├── POS_CHECKOUT_COMPLETED.json
│   ├── EATERY_ORDER_RECEIVED.json
│   ├── EATERY_MEAL_READY.json
│   ├── HEALTHCARE_APPOINTMENT_BOOKED.json
│   ├── HEALTHCARE_PRESCRIPTION_CREATED.json
│   ├── MOBILITY_RIDE_REQUESTED.json
│   ├── MOBILITY_TRIP_COMPLETED.json
│   ├── INVESTOR_CAPITAL_DEPOSITED.json
│   └── TREASURY_RETURN_DISTRIBUTED.json
│
├── src/
│   ├── security/                          # Security, MFA/OTP, Governance & Cryptographic Audit (Sections 36, 38, 47)
│   │   ├── auth.py | rbac.py | audit.py | governance_compliance.py # PBKDF2, JWT, multi-tenant blocking, KYC/AML
│   │   ├── gateway_middleware.py          # Rate Limiting (`429`), Correlation ID Injection (`X-Correlation-ID`) & CORS
│   │   ├── fraud_ai.py                    # Section 38.6: Geodesic Impossible Travel (`Machakos->Mombasa`) & Brute Force
│   │   ├── policy_control.py              # Section 43 & 47: Operational Governance Policies, API Keys & Dynamic Tax
│   │   ├── privacy_engine.py              # Section 38.7: GDPR & Kenya DPA Right-to-be-Forgotten PII Anonymization
│   │   ├── regulatory_reporting.py        # Section 35.4 & 38.8: Multi-Jurisdictional CBK AML/FIU & KRA Tax Filings
│   │   └── hardware_hsm.py                # Section 41.4 & 38.4: Mobile NFC Biometric Smart Terminal HSM Encryption Keys
│   │
│   ├── observability/                     # Telemetry, BI, CI/CD, DR & HA Failover (Sections 27, 40, 44, 47)
│   │   ├── metrics.py | disaster_recovery.py # Prometheus exposition (`/metrics`) & point-in-time cryptographic `PITR`
│   │   ├── chaos_engine.py                # Section 44.2 & 40.7: Chaos Engineering & Fault Injection Resilience Drills
│   │   ├── bi_aggregation.py              # Section 27.2 & 27.3: Unified BI Executive & Leadership Aggregations
│   │   ├── cicd_quality_gate.py           # Section 40.5 & 40.6: Automated Deployment Quality Gate & Release Verification
│   │   ├── ha_failover.py                 # Section 40.8 & 45.3: Active-Active High Availability & Geographic Failover
│   │   ├── ledger_reconciliation.py       # Section 37.4 & 10.4: Double-Entry Ledger Reconciliation & Reversing Sweeps
│   │   └── k8s_autoscaler.py              # Section 40.3 & 40.4: Multi-Cloud Kubernetes HPA Container Autoscaling
│   │
│   ├── ai/                                # Multi-Agent Suite & Vector RAG Retrieval (Sections 13, 39)
│   │   ├── rag_engine.py                  # Embedded Vector Knowledge Store & Cosine Similarity Matching
│   │   ├── agents.py                      # Executive AI, Agriculture RAG, and Support Urgency Classifier
│   │   ├── predictive_intelligence.py     # SKU Demand Stockout Forecasts & Dynamic Clearance Pricing (Rule 10)
│   │   └── crm_intelligence.py            # AI CRM Churn Prediction, LTV Evaluation & Automated Retention (`500 KRT`)
│   │
│   ├── config.py                          # Platform Configuration & KRT Reward Ratios (5% default)
│   ├── domain/models.py                   # Pydantic Domain Models across all 7 Verticals & Engines
│   ├── db/
│   │   ├── database.py                    # SQLAlchemy Async/Sync Session management
│   │   ├── migrator.py                    # Automated DDL migration runner & integrity checker
│   │   └── seed_data.py                   # Production East African ecosystem seeder
│   │
│   ├── core/                              # Shared Platform Engines (Strict Rule Enforcement)
│   │   ├── event_bus.py                   # Universal Event Bus with SHA-256 Cryptographic Audit Hashing
│   │   ├── ledger_engine.py               # Universal Double-Entry Ledger Engine (Rule 5, 8, 9)
│   │   ├── wallet_engine.py               # Multi-Asset Wallet Engine isolating KES, KRT, Loyalty, Credit, Investment
│   │   ├── rule_engine.py                 # Declarative Rule Engine executing automated settlements & token grants
│   │   ├── treasury_engine.py             # Treasury & Liquidity Management Engine (Section 12 & 18)
│   │   ├── exchange_engine.py             # Multi-Asset Exchange Engine (KES <-> KRT, Loyalty redemptions)
│   │   ├── ai_gateway.py                  # AI Orchestration & Multi-Agent Gateway (Rule 10)
│   │   ├── workflow_engine.py             # Declarative Workflow State Machine Engine (Section 11.2 & Rule 10)
│   │   ├── dlq_healing.py                 # Section 36.6: Distributed Dead-Letter Queue (DLQ) & Self-Healing
│   │   ├── event_replay.py                # Section 37.5: Replayable Event Sourcing State Reconstruction Engine
│   │   ├── offline_sync.py                # Section 41.5 & 20.2: Mobile App & POS Offline Synchronization Engine
│   │   ├── omnichannel_portal.py          # Section 31.2 & 31.3: Unified Single-Account Super App & Merchant Gateway
│   │   └── vertical_registry.py           # Dynamic Vertical Registration Framework (Section 35)
│   │
│   ├── verticals/                         # All 13 Production Vertical, Future Industry & Innovation Services
│   │   ├── karis_farm/service.py          # Vertical 1: Agriculture & KARIS FARM™ Traceability (Section 28)
│   │   ├── marketplace/service.py         # Section 14.3 & 17.2: Multi-Vendor Marketplace Aggregation & Split-Commissions
│   │   ├── retail_pos/
│   │   │   ├── service.py                 # Vertical 2: Omnichannel POS & Supermarket Retail (Sections 20, 30)
│   │   │   └── pos_ai.py                  # Section 20.3 & 30.5: POS Queue Congestion & Retail Shrinkage Audits
│   │   ├── eatery/service.py              # Vertical 3: Eatery & Kitchen Display System KDS (Section 29)
│   │   ├── logistics/
│   │   │   ├── service.py                 # Vertical 4: Delivery & Logistics Escrow Payouts (Section 21 & Rule 4)
│   │   │   └── route_weather_ai.py        # Section 15 & 21.5: Multi-Warehouse Serial Tracking & AI Weather Dispatch
│   │   ├── healthcare/
│   │   │   ├── service.py                 # Vertical 5: Healthcare, EMR Notes & CHV Workflows (Section 32)
│   │   │   └── ambulance_ai.py            # Section 32.8 & 33.5: Emergency ALS/BLS Ambulance Geodesic Dispatch
│   │   ├── mobility/service.py            # Vertical 6: Mobility & Ride-Hailing Trips (Section 33)
│   │   ├── finance_invest/service.py      # Vertical 7: Investor Capital Pools & AI Lending (Sections 19, 25 & Rule 3)
│   │   ├── crm_call_center/sla_engine.py  # Section 24.4: Call Center SLA Benchmarks & Supervisor Escalations
│   │   ├── financial_services/service.py  # Section 34: Live M-Pesa C2B Webhook Verification & Amortization
│   │   ├── sales_force/service.py         # Section 22: Field Representatives, Visits & Referral Commissions
│   │   ├── loyalty/
│   │   │   ├── service.py                 # Section 26: Promotional Campaigns, Reward Grants & Multipliers
│   │   │   └── network_tier_engine.py     # Section 23.2 & 18: Loyalty Tier Upgrades & Cross-Merchant Network Clearing
│   │   ├── open_banking_cbdc/service.py   # Section 48: CBDC-KES, PSD2 Consents, EAC Cross-Border & ESG
│   │   └── future_industries/service.py   # Section 35.3: Education Edu-Pay, Tourism Safari & Prop-Share Real Estate
│   │
│   ├── integrations/
│   │   ├── erp_tax_sync.py                # Section 36.5 & 43.2: SAP S/4HANA Accounting Batch Sync & Notification Templates
│   │   ├── sdk_generator.py               # Section 46.2: Automated Enterprise API SDK Client & Scaffolding Generator
│   │   ├── mobile_passkey_push.py         # Section 41.2 & 26.5: Mobile FIDO2 Passkey Challenge & APNS/FCM Push Tokens
│   │   └── whatsapp_bot.py                # Section 36.5 & 24: WhatsApp Cloud API Interactive Conversational Bot
│   │
│   ├── web/                               # Interactive Enterprise Web Portal & Dashboard
│   │   └── index.html                     # 35 Live Tabs across Traceability, AI Chat, Ledger, DR, Passkey, Recon & K8s UI
│   │
│   └── api/                               # Enterprise API Gateway & Modular Routers (`/api/v1/...`)
│       ├── main.py                        # Master FastAPI Gateway Server
│       └── routers/                       # 46 Modular controllers across all verticals, AI, auth, telemetry, and DR
│
├── tests/                                 # 100% Passing Automated Verification Suites (16 Suites / 46 Tests)
│
├── tests/                                 # Automated Pytest Suite verifying 100% of invariants
├── Dockerfile                             # Multi-Stage Production Container Build
├── docker-compose.yml                     # Turnkey Local/Cloud Orchestration Stack
├── k8s/deployment.yaml                    # Cloud Kubernetes Deployment Manifests
└── run_enterprise_simulation.py           # Standalone Master 7-Vertical Simulation Script
```

---

## ⚖️ 3. How We Enforce the Ten Absolute Platform Rules

| Rule | Rule Description | Executable Enforcement Implementation |
| :---: | :--- | :--- |
| **Rule 1** | **No Event → No State Change** | All database state modifications occur solely when subscribers (`DeclarativeRuleEngine`, `UniversalLedgerEngine`) react to validated events published on `UniversalEventBus`. |
| **Rule 2** | **No Payment → No Settlement** | Merchant settlement (`CREDIT_SUPPLIER_WALLET`) is hard-blocked until a `PAYMENT_CONFIRMED` event arrives (`src/core/rule_engine.py`). |
| **Rule 3** | **No Credit Approval → No Credit Purchase** | Credit purchases and wallet disbursements verify `credit_applications.status = 'CREDIT_APPROVED'` (`src/verticals/finance_invest/service.py`). |
| **Rule 4** | **No Delivery Confirmation → No Rider Payment** | Rider payouts are escrowed inside `operations_kes` and released strictly when `DELIVERY_COMPLETED` is verified (`src/verticals/logistics/service.py`). |
| **Rule 5** | **No Wallet Directly Edits Another Wallet** | `MultiAssetWalletEngine.execute_ledger_movement()` rejects any direct balance modification unless commanded by `UniversalLedgerEngine` with cryptographic authorization tokens. |
| **Rule 6** | **Everything Generates an Event** | Every identity registration, POS checkout, harvest log, or token minting publishes a JSON Schema-validated payload to the store (`event_store`). |
| **Rule 7** | **Everything is Configurable** | Declarative rules are managed via REST (`/api/v1/admin/rules`) and persisted inside `business_rules` without requiring code rebuilds. |
| **Rule 8** | **Every Event is Timestamped** | All domain events and ledger entries capture exact UTC timestamps (`TIMESTAMP WITH TIME ZONE`). |
| **Rule 9** | **Every Transaction is Immutable** | PostgreSQL triggers (`prevent_ledger_mutation()`) block SQL `UPDATE` or `DELETE` commands. Every double-entry movement chains the previous entry's SHA-256 audit hash. |
| **Rule 10** | **AI Assists; Humans Approve Decisions** | AI models (`Executive AI`, `Risk AI`, `Logistics AI`) calculate credit risk and surge pricing, while high-impact approvals mandate human RBAC verification. |

---

## 🌽 4. Flagship Vertical: KARIS FARM™ Traceability Lineage

When John Kamau logs a `1,000 KG` harvest of `Grade-A Hass Avocados` in Machakos County (`Batch BATCH-FARM-HAS-1BF01C`), the platform generates Traceability QR Code `KARIS-TRACE-QR-12C8D4F2`.

When consumers or supermarket partners scan this QR code on `http://localhost:8000/portal` or call `GET /api/v1/farm/traceability/KARIS-TRACE-QR-12C8D4F2`, the API returns the exact cryptographically chained lineage:
* **Farm Origin & GPS:** `Kamau Orchards - Machakos County` (`-1.3564, 36.9321`).
* **Producer & Cooperative Custody:** Farmer John Kamau aggregated by `Machakos Farmers Cooperative`.
* **Harvest Inspection:** `1,000 KG Grade-A Hass Avocados` certified under `GAP_CERTIFIED`.
* **Retail & Settlement:** Listed at `KARIS Supermarket Mlolongo` with automated double-entry M-Pesa settlement and 5% KRT loyalty token minting (`Rule 2 & 6`).

---
*KARIS OS™ Unified Enterprise & Digital Economy Platform — Built for Scale, Auditability & Infinite Vertical Expansion.*
