# KARIS OS™ :: TECHNICAL SRE RUNBOOK VOLUME 18
## KARIS BORDERX™ EAST AFRICAN CUSTOMS & BORDER TRADE CLEARING ENGINE (SECTION 58 / VERTICAL 23)

---

### 1. Architectural Overview & 9 Multi-Currency Trade Wallets
**KARIS BorderX™** (`Vertical 23 / Section 58`) is the digital customs, border trade, and logistics clearing ecosystem across East Africa (`KE, UG, TZ, RW, BI, SS, CD, ET, COMESA, EAC, AfCFTA`). Every onboarded trade entity (`IMPORTER, EXPORTER, CLEARING_AGENT, TRANSPORTER, FREIGHT_COMPANY, SHIPPING_LINE, CUSTOMS_OFFICER`) automatically receives 9 multi-currency trade wallets (`Rule 1 & Rule 6`):
1. `kes_wallet_id`: Kenyan Shilling (KES)
2. `ugx_wallet_id`: Ugandan Shilling (UGX)
3. `tzs_wallet_id`: Tanzanian Shilling (TZS)
4. `rwf_wallet_id`: Rwandan Franc (RWF)
5. `bif_wallet_id`: Burundian Franc (BIF)
6. `ssp_wallet_id`: South Sudanese Pound (SSP)
7. `usd_wallet_id`: United States Dollar (USD)
8. `eur_wallet_id`: Euro (EUR)
9. `krt_wallet_id`: KRT Digital Utility Token (`1 KRT = 1 KES default parity`) plus `CUSTOMS-ACCOUNT-REF`

---

### 2. Customs Declarations across 7 Corridors & AI HS Code Classification
BorderX supports 7 declaration categories: `IMPORTS`, `EXPORTS`, `TRANSIT_CARGO`, `WAREHOUSING`, `BONDED_GOODS`, `TEMPORARY_IMPORTS`, and `DUTY_EXEMPTIONS`.
- **AI HS Code Classifier (`ai_hs_classifier`)**: Automatically maps product descriptions to exact EAC/WCO Harmonized System (`HS Code`). For example, `Solar Inverter Components` -> `HS Code 8517.13.00` with exact permit mapping (`CAK Equipment Homologation Certificate`, `KEBS Quality Inspection`).
- **Rule 10 Advisory**: All AI classifications enforce a human verification gate (`require_role('CLEARING_AGENT')`).

---

### 3. Smart Duty Calculator & KRT Clearing Fee Discounts (`Rule 5 & Rule 9`)
The `SmartDutyCalculator` calculates precise duty and fee breakdowns across 11 parameters: `import_duty, export_duty, vat, excise, railway_levy, idf, rdl, port_charges, clearing_fees, agent_fees, and inspection_fees`.
- **KRT Utility Fee Discount (Up to 50%)**: When traders or agents settle duty and agency clearing fees using KRT (`or hold active KRT staking lockups`), clearing fees and agent fees are discounted by **25% to 50%**.
- **Double-Entry Immutability (`Rule 9`)**: Every settlement debits the trader wallet and credits the Customs Revenue Pool (`POOL-BORDERX-REVENUE`), recording an exact SHA-256 hash anchor.

---

### 4. AI Customs Risk Engine (`Rule 10 Mandatory Officer Inspection`)
To prevent smuggling and tax evasion across COMESA/EAC borders (`Section 58.8`), the AI Customs Risk Engine monitors:
- **Under-Valuation (`cif_value < market_benchmark * 0.6`)**: If declared CIF is under 60% of the regional HS benchmark (`e.g. $3,000 USD vs $10,000 USD`), the engine immediately assigns `customs_risk_score = 85.0`.
- **Hard Block & Rule 10 Gate**: Declarations with `risk_score >= 75` transition to `UNDER_INSPECTION` and hard-block green-channel duty settlement. An automated physical inspection (`BorderXInspectionModel`) is scheduled for a licensed Customs Officer (`require_role('CUSTOMS_OFFICER')`) under **Rule 10**.

---

### 5. Smart Border Queue & Congestion Forecasts (`Section 58.7`)
`smart_border_queue` predicts real-time waiting times and congestion across East African clearing hubs (`Busia, Malaba, Namanga, Gatuna, Rusumo, Nimule`):
- For example, when `BUSIA_EAC` is experiencing heavy commercial truck congestion (`4.5 hours waiting time`), the AI automatically recommends diverting transit cargo to `MALABA_EAC` (`1.2 hours waiting time`), saving 3.3 hours of transit delay!

---

### 6. Trade Finance Facilities under Rule 3 (`Section 58.10`)
BorderX structures 6 cross-border financing facilities: `WORKING_CAPITAL`, `INVOICE_FINANCING`, `LETTERS_OF_CREDIT`, `TRADE_CREDIT`, `PURCHASE_FINANCING`, and `SUPPLIER_FINANCING`.
- **Rule 3 Enforcement**: *No Credit Approval -> No Credit Purchase*. Applications are verified against borrower reputation (`score >= 60`) and CIF collateral value (`max loan up to 80% of CIF value`).
- **Double-Entry Disbursement (`Rule 9`)**: Approved loans are disbursed directly from `POOL-BORDERX-FINANCE` to the borrower's KRT or USD wallet.

---

### 7. Digital Document AI (`Section 58.12`)
BorderX auto-generates 8 cryptographic SHA-256 verified trade certificates: `COMMERCIAL_INVOICE`, `PACKING_LIST`, `CERTIFICATE_OF_ORIGIN`, `BILL_OF_LADING`, `TRANSIT_DECLARATION`, `CUSTOMS_DECLARATION_FORM`, `INSPECTION_CERTIFICATE`, and `DELIVERY_NOTE`. Each document includes a verifiable digital signature (`e.g., BDX-SIG-A8F190B2...`).

---

### 8. Verification Commands
```bash
# Run multi-tenant integration test suite for BorderX
PYTHONPATH=. pytest tests/test_karis_borderx_customs.py -v

# Run full system multi-tenant verification (74/74 passing)
PYTHONPATH=. pytest tests/ -v
```
