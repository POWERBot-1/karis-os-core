# KARIS OS™ Version 1.0.0-PROD-V1 — Phase 4: Interactive Web Portal & Sandbox Walkthrough Guide

**Document Version:** 5.0.0-PROD-V1  
**Target Audience:** C-Suite Leadership (`CEO, CFO, CTO`), Product Managers & Client Integration Teams  
**Enforces:** Section 31 (`Omnichannel Portal Gateway`), Section 27 (`BI Executive Summary`), and All 18 Industry Verticals (`Tabs 1 to 39`)

---

## 1. Executive Portal Overview & Launch Instructions

The **KARIS OS™ Interactive Enterprise Web Portal (`src/web/index.html`)** is a single-page, real-time command center served directly by our FastAPI Gateway (`/portal` or `/`). It unifies all 18 industry verticals across **39 Live Navigation Tabs**, providing instant visual simulation of double-entry ledger checkouts, AI Copilot analyses, and IoT telemetry streams.

```
+---------------------------------------------------------------------------------------------------+
|                        KARIS OS™ INTERACTIVE ENTERPRISE WEB PORTAL (`/portal`)                    |
|                        39 Navigation Tabs • Live Event & Ledger Streams                           |
+---------------------------------------------------------------------------------------------------+
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         ▼                                        ▼                                        ▼
┌────────────────────────────────┐  ┌────────────────────────────────┐  ┌────────────────────────────────┐
│   TAB 1: EXECUTIVE BI DASHBOARD│  │  TAB 2: KARIS FARM TRACEABILITY│  │  TAB 7: LIVE SYSTEM SIMULATORS │
│  • KES/KRT Reserve Backing     │  │  • Smallholder Harvest Batches │  │  • Supermarket POS Checkout    │
│  • 18 Active Verticals Online  │  │  • GAP_CERTIFIED QR Lineage    │  │  • Cloud Kitchen KDS & Rider   │
└────────────────────────────────┘  └────────────────────────────────┘  └────────────────────────────────┘
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         ▼                                        ▼                                        ▼
┌────────────────────────────────┐  ┌────────────────────────────────┐  ┌────────────────────────────────┐
│     TAB 36: POWER BOT X AI     │  │   TAB 37: KARIS ENERGY SOLAR   │  │   TAB 38: PALPLUS HOSTED LINKS │
│  • WhatsApp Status Marketing   │  │  • PAYG Solar Pump Unlocking   │  │  • `link.palpluss.com/6e8de0bc`│
│  • Prediction Copilot (`Rule 10`)│  │  • IoT Telemetry `KRT-JOULE`   │  │  • M-Pesa Express Reconciliation│
└────────────────────────────────┘  └────────────────────────────────┘  └────────────────────────────────┘
                                                  │
                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│               TAB 39: KARIS INNOVATION SUITE (`Pharma-Trace, Prop-Share, Edu-Pay`)               │
│  • Cold-Chain Breach Detection (`10.5°C > 8°C limit`) -> Auto-locks lot from retail dispensing   │
│  • Prop-Share Fractional Real Estate -> Atomic double-entry monthly rental dividend distributions  │
│  • Edu-Pay Tuition Installment Checkouts -> Awards `+150 KRT-EDU` campus cafeteria bonus tokens   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### **To Launch the Portal on Your Machine:**
```bash
cd /home/user/karis-os-core
PYTHONPATH=. uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
Once booted, open your web browser to `http://localhost:8000/portal` (or `/`).

---

## 2. Step-by-Step Walkthrough Guide Across Key Flagship Tabs

### **Step 1: Executive Dashboard & KPIs (`Tab 1`)**
* **What to Show:** Point out the top summary cards:
  * **Active Verticals Online:** `18 Verticals` (`Agriculture, POS, Eatery, Healthcare, Mobility, Logistics, Lending, Power BOT X, Energy, PalPlus, Pharma, Prop-Share, Edu-Pay`).
  * **Treasury Reserve Ratio:** `20.0%+ Backed` (`Rule 5 & Section 12` KES fiat reserve backing).
  * **Rule 9 Audit Status:** `100% Verified Clean` (`prevent_ledger_mutation()` SHA-256 hash chaining intact).

---

### **Step 2: Flagship KARIS FARM™ Traceability (`Tab 2`)**
* **What to Show:** Enter or select a produce QR code (`e.g., KARIS-TRACE-QR-2CD35CAF`).
* **Live Action:** Watch the portal render the complete harvest lineage:
  * **Farmer Origin:** John Kamau (`Machakos County`) | Farm Acreage: `12.5 Acres`.
  * **Produce Specs:** `1,000 KG` of Grade-A Hass Avocados | Verification: `GAP_CERTIFIED`.
  * **Double-Entry Settlement:** Customer Amina Wanjiku purchases 50 KG (`KES 7,500.00`), triggering instant KES debit/credit (`Rule 5`) and awarding a **5% KRT loyalty reward (`+375.00 KRT`)** directly to her wallet (`Rule 7`).

---

### **Step 3: PalPlus Hosted Payment Links (`Tab 38 - Section 51`)**
* **What to Show:** Highlight our active temporary payment link:
  * **URL:** `https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f` (Link ID: `6e8de0bc-1284-4bba-a5de-f886665bf18f`).
* **Live Action:** Click **`Trigger PalPlus Webhook`** inside the simulator card.
* **System Execution (`Verified Live`):**
  ```text
  💰 [PALPLUS WEBHOOK RECEIVED] Receipt: PALPLUS-RC-99021 | Payer: USER-AMINA-777 | Amount: KES 3,500.00
  ✔ [DOUBLE-ENTRY RECONCILIATION (`Rule 2, 5 & 9`)]
  1. Customer KES Wallet Debited (-KES 3,500.00) / Supplier KES Wallet Credited (+KES 3,500.00)
  2. Rule Engine Minted +175.00 KRT Loyalty Reward directly into Customer KRT Wallet (`Rule 7`)
  3. Event Published: PAYMENT_LINK_CHECKOUT_COMPLETED (`SHA-256 Chained Hash Anchor intact`)
  ```

---

### **Step 4: KARIS ENERGY & SMART SOLAR GRID™ (`Tab 37 - Section 50`)**
* **What to Show:** Explain how smallholder farmers and community clinics purchase Pay-As-You-Go (PAYG) solar home systems, battery storage banks, and irrigation pumps (`SOLAR-PUMP-MACHAKOS-01`).
* **Live Action:** Click **`Stream Telemetry & Mint KRT`**.
* **System Execution (`Verified Live`):**
  ```text
  📡 [SMART METER TELEMETRY ARRIVED] Generation: 6.85 kWh | Battery: 98.44% | Moisture: 48.0%
  ⚡ [COMMUNITY MICROGRID FEED-IN DETECTED] Surplus Solar Power Fed into Grid: 2.50 kWh
  🎉 [AUTOMATED GREEN TOKEN MINTING] UniversalLedgerEngine debits Treasury Reserve Pool and credits Farmer Kamau's KRT Wallet: +25.00 KRT-JOULE (`Rule 7 & Rule 9 double entry`)!
  ```

---

### **Step 5: POWER BOT X Autonomous AI Prediction Economy (`Tab 36 - Section 49`)**
* **What to Show:** Explain that Power BOT X is not a betting site or chatbot—it is a self-improving WhatsApp prediction economy powered by 7 AI Intelligence engines and KRT tokens.
* **Live Action:** Click **`Generate WhatsApp Status Kit`**.
* **System Execution (`Verified Live`):**
  ```text
  ✔ [WHATSAPP STATUS PACKAGE GENERATED]
  Target Channel: WHATSAPP_STATUS | Deep Link: https://wa.me/254700000000?text=JOIN_AGENT-David_...
  Headline: Gor Mahia vs AFC Leopards
  Audio Script: "Sasa buda! Komaa na Power BOT X. Hii mechi ya Gor Mahia na AFC Leopards ni moto. AI yetu imeshachora tactical breakdown yote kwa WhatsApp!"
  ```

---

### **Step 6: KARIS INNOVATION EXPANSION SUITE (`Tab 39 - Section 52`)**
* **What to Show:** Demonstrate zero-code kernel expansion across 3 high-impact industry domains (`Pharma-Trace / Prop-Share / Edu-Pay`).
* **Live Action:** Click **`Trigger Cold-Chain Breach`**, then **`Distribute Rental Dividends`**, then **`Pay Tuition Installment`**.
* **System Execution (`Verified Live`):**
  ```text
  🌡️ [PHARMA-TRACE COLD-CHAIN BREACH] Temperature Reported: 10.5°C (`> 8.0°C limit`) -> Status: COLD_CHAIN_BREACHED_LOCKED (`Rule 1 & Rule 6 verified`)
  🏢 [PROP-SHARE DIVIDENDS] Property: Machakos Commercial Hub | Rental Pool: 100,000 KRT -> Distributed via double-entry accounting (`Rule 5 & Rule 9`)
  🎓 [EDU-PAY TUITION CHECKOUT] Paid: KES 15,000.00 -> Awarded Scholarship/Cafeteria Bonus: +150.00 KRT-EDU (`Rule 7 & Rule 9 verified`)
  ```

---

## 3. Automated Walkthrough Verification Command

To run our automated API Gateway test client across all 6 steps of this exact portal walkthrough right inside your terminal:

```bash
cd /home/user/karis-os-core
PYTHONPATH=. python3 run_phase_4_portal_demo_execution.py
```

Your executive presentation, client walkthrough, and interactive sandbox demonstration are 100% operational and verified!
