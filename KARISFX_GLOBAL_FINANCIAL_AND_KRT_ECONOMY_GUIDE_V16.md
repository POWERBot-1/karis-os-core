# KARIS OS™ :: TECHNICAL SRE RUNBOOK VOLUME 16
## KARISFX™ GLOBAL FINANCIAL ECOSYSTEM & KRT ECONOMY LAYER (SECTION 56 / VERTICAL 21)

---

### 1. Architectural Overview & KRT Foundation
**KARISFX™** (`Vertical 21 / Section 56`) is the flagship multi-asset trading platform of KARIS OS™, built directly on the **KRT (Karis Token) Economy Layer**. Every single onboarded account automatically receives a unified multi-asset wallet ecosystem (`Rule 1 & Rule 6`), including:
1. **KRT Foundation Wallet (`KRT_WALLET`)**: Primary utility and fee settlement anchor.
2. **Fiat Wallets (`KES_WALLET`, `USD_WALLET`, `EUR_WALLET`, `GBP_WALLET`)**: Local & international fiat holdings.
3. **Stablecoin Wallet (`STABLECOIN_WALLET`)**: USDT/USDC cross-border liquidity.
4. **Rewards Wallet (`REWARDS_WALLET` / `AssetType.KRT_REWARDS`)**: Dedicated holding wallet for earned activity bonuses.
5. **Treasury Reference (`TREASURY-ACCOUNT-REF-{identity_id}`)**: Direct accounting link to platform reserves.

---

### 2. Multi-Asset Trading Platform across 16 Asset Classes
KARISFX supports 16 global financial asset classes: `Forex`, `Stocks`, `ETFs`, `Commodities`, `Precious Metals`, `Energy Markets`, `Indices`, `Bonds`, `Futures`, `Options`, `Money Markets`, `Mutual Funds`, `Tokenized Assets`, `AI Portfolios`, `Social Trading`, and `Copy Trading`.
- **Trading Fee Discounts (Up to 60%)**: When users pay trading fees in KRT or hold active KRT staking lockups (`SILVER / GOLD / PLATINUM`), fees are discounted by **15% to 60%**.
- **Double-Entry Ledger Immutability (`Rule 5 & Rule 9`)**: Every fee deduction or settlement is strictly executed via `UniversalLedgerEngine.record_transaction()`, chaining exact SHA-256 cryptographic hashes (`previous_hash + payload + timestamp`).

---

### 3. KRT Staking Modules (`Section 56.5`)
Staking KRT into lockup pools (`30, 90, 180, 365 days`) unlocks high-yield APY (`12% - 25%`) alongside VIP platform benefits:
| Staking Tier | Min Staked KRT | Lockup Days | APY Yield | Fee Discount | AI Premium Unlocked | Reputation Boost |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BRONZE** | 500.0 KRT | 30 Days | 12.0% | 15.0% | No | +50 Points |
| **SILVER** | 2,000.0 KRT | 90 Days | 15.0% | 30.0% | **Yes** | +150 Points |
| **GOLD** | 5,000.0 KRT | 180 Days | 20.0% | 45.0% | **Yes** | +300 Points |
| **PLATINUM** | 15,000.0 KRT | 365 Days | 25.0% | 60.0% | **Yes** | +500 Points |

---

### 4. AI Economy Engine & Rule 10 Governance Gate
The **KARIS AI Economy Engine** delivers 13 core financial intelligence services: `MARKET_INTELLIGENCE`, `PORTFOLIO_OPTIMIZATION`, `STRATEGY_BUILDER`, `RISK_ANALYSIS`, `TRADE_JOURNAL`, `AI_MENTOR`, `AI_CHAT`, `VOICE_ASSISTANT`, `NEWS_INTELLIGENCE`, `PATTERN_RECOGNITION`, `AUTOMATED_WATCHLISTS`, `PORTFOLIO_HEALTH`, and `EARNINGS_ANALYSIS`.
- **Rule 10 Mandatory Advisory**: All AI outputs explicitly enforce a Rule 10 guardrail: *"AI assists with market patterns and risk analysis. Exact trade execution requiring capital deployment or margin leverage strictly mandates human/trader approval per Rule 10."*

---

### 5. Reward Engine Anti-Abuse Controls (`Section 56.6`)
The Transparent Reward Engine tracks 10 platform activities (`Trading, Learning, Strategies, Referrals, Competitions, Bug Reports, etc.`). To prevent wash-trading or automated scalp exploitation (`Rule 1 & Rule 6`):
- **Velocity & Scalp Check**: If a trade holding duration is strictly less than 60 seconds (`trade_holding_seconds < 60`), the engine immediately blocks the reward (`status: BLOCKED_WASH_TRADING_VELOCITY_CHECK`).
- **Daily Caps**: Enforces strict daily KRT limits (e.g. `300 KRT/day` for trading, `3,500 KRT/day` for bug reports).

---

### 6. Strategy Marketplace & Decentralized Governance (`Section 56.7 & 56.8`)
- **Marketplace Split Settlement**: Users purchase published trading strategies, bots, and indicators using KRT. The double-entry ledger automatically splits settlement exactly: **85% to Creator KRT Wallet** and **15% to Platform Treasury (`ORG-TREASURY-MAIN`)**.
- **Decentralized Governance Voting**: KRT tokenholders submit proposals and cast weighted votes (`FOR`, `AGAINST`, `ABSTAIN`) where voting power equals `staked_amount + (wallet_balance * 0.5)`. High-impact system changes require AI impact summaries under `Rule 10`.

---

### 7. Zero-Trust Compliance & AML Screening (`Section 56.12`)
- **Continuous AML Monitoring**: All transactions are evaluated against exact jurisdictional rules (`KE-EAC`). Any transaction volume exceeding **$10,000 USD equivalent** (`or 1,300,000 KES`) automatically triggers a **CBK/FIU AML Alert (`cbk_fiu_flagged: True`)**, mandates KYC Tier 3 audit review, and emits `KARISFX_AML_ALERT_TRIGGERED`.

---

### 8. Verification Commands
```bash
# Run integration tests for KARISFX
PYTHONPATH=. pytest tests/test_karisfx_krt_economy.py -v

# Verify via Python API Client SDK
PYTHONPATH=. python3 -c "from sdk.karis_os_client import KarisOsClient; print('SDK Ready')"
```
