"""
KARIS OS™ :: Multi-Tenant Integration Test Suite for KARISFX™ Global Financial Ecosystem (`Section 56`).
Verifies KRT Foundation onboarding, 16 Asset Classes trading, 13 AI Services, KRT Staking (up to 60% discount),
Transparent Reward Engine with anti-wash-trading checks, Marketplace 85/15 split settlement, Decentralized Governance,
Social Copy-Trading, Developer API registration, and Zero-Trust AML transaction monitoring.
"""

import pytest
from datetime import datetime, timezone
from src.core.wallet_engine import wallet_engine
from src.core.ledger_engine import ledger_engine
from src.core.event_bus import event_bus
from src.verticals.karisfx.service import karisfx_service
from src.domain.models import WalletType, AssetType

@pytest.fixture(autouse=True)
def setup_karisfx_environment():
    """
    Reset singleton state and initialize clean test wallets and system reserve pools.
    """
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0" * 64
    event_bus.event_store.clear()

    karisfx_service.accounts.clear()
    karisfx_service.orders_trades.clear()
    karisfx_service.staking_positions.clear()
    karisfx_service.rewards_history.clear()
    karisfx_service.marketplace_items.clear()
    karisfx_service.marketplace_purchases.clear()
    karisfx_service.governance_proposals.clear()
    karisfx_service.governance_votes.clear()
    karisfx_service.social_copy_links.clear()
    karisfx_service.developer_apps.clear()
    karisfx_service.compliance_logs.clear()

    # Re-initialize pools
    karisfx_service._init_system_pools()
    yield

def test_karisfx_krt_foundation_and_unified_wallets():
    """
    Verifies that every onboarded user automatically receives their KRT Foundation unified wallet ecosystem.
    """
    acc = karisfx_service.onboard_karisfx_account(
        identity_id="TRADER-KE-001",
        full_name="Alex Kamau",
        phone_number="+254711000111",
        initial_krt_deposit=2500.0,
        initial_usd_deposit=10000.0
    )

    assert acc.identity_id == "TRADER-KE-001"
    assert acc.kyc_status == "VERIFIED_TIER_3"
    assert "TREASURY-ACCOUNT-REF-TRADER-KE-001" in acc.treasury_account_ref
    assert acc.reputation_score == 100

    # Check that all 7 internal wallets exist and have correct balances
    krt_w = wallet_engine.get_wallet(acc.krt_wallet_id)
    usd_w = wallet_engine.get_wallet(acc.usd_wallet_id)
    stable_w = wallet_engine.get_wallet(acc.stablecoin_wallet_id)
    assert krt_w and krt_w.balance == 2500.0
    assert usd_w and usd_w.balance == 10000.0
    assert stable_w and stable_w.balance == 10000.0

    # Check event bus record
    events = [e for e in event_bus.event_store if e.event_type == "KARISFX_ACCOUNT_CREATED"]
    assert len(events) == 1
    assert events[0].payload["account_number"] == acc.account_number

def test_karisfx_multi_asset_trading_and_staking_fee_discounts():
    """
    Tests trading across supported asset classes (Forex, Commodities), verification of KRT staking fee discounts,
    and double-entry ledger settlement per Rule 5 & Rule 9.
    """
    acc = karisfx_service.onboard_karisfx_account("TRADER-KE-002", "Grace Odhiambo", "+254722000222", initial_krt_deposit=10000.0)

    # Trade 1: Standard account (no staking yet -> 0% discount)
    trade_1 = karisfx_service.execute_multi_asset_trade(
        account_id=acc.account_id,
        asset_class="FOREX",
        symbol="KES/USD",
        side="BUY",
        requested_units=1000.0,
        execution_price=1.0,
        leverage=2.0
    )
    assert trade_1.fee_discount_pct == 0.0
    assert trade_1.final_fee_krt == trade_1.base_fee_krt
    assert trade_1.status == "EXECUTED_SETTLED"

    # Now open a KRT Staking position of 5,000 KRT (locks up into Staking pool -> GOLD tier -> 45% discount)
    staking_pos = karisfx_service.open_staking_position(
        account_id=acc.account_id,
        amount_krt=5000.0,
        lockup_duration_days=90
    )
    assert staking_pos.staking_tier == "GOLD"
    assert staking_pos.fee_discount_pct == 45.0
    assert staking_pos.ai_premium_unlocked is True
    assert acc.reputation_score == 400  # +300 bonus for Gold tier

    # Check wallet balance after staking lockup via double entry (`Rule 5 & Rule 9`)
    user_krt_w = wallet_engine.get_wallet(acc.krt_wallet_id)
    assert user_krt_w.balance < 5000.0  # 10,000 initial minus fee minus 5,000 staked plus any trading reward

    # Trade 2: Now with Gold Staking active -> should receive exactly 45% discount on fee!
    trade_2 = karisfx_service.execute_multi_asset_trade(
        account_id=acc.account_id,
        asset_class="COMMODITIES",
        symbol="GOLD-SPOT",
        side="BUY",
        requested_units=10.0,
        execution_price=100.0,
        leverage=1.0
    )
    assert trade_2.fee_discount_pct == 45.0
    expected_discounted_fee = round(trade_2.base_fee_krt * 0.55, 4)
    assert abs(trade_2.final_fee_krt - expected_discounted_fee) < 0.01

    # Verify cryptographic ledger hash chaining intact
    from src.security.audit import audit_engine
    ledger_audit = audit_engine.verify_ledger_chain()
    assert ledger_audit["status"] == "VERIFIED_CLEAN"

def test_karisfx_ai_economy_services_rule_10():
    """
    Verifies the AI Economy Engine querying across the 13 supported AI services and enforcing Rule 10 advisories.
    """
    acc = karisfx_service.onboard_karisfx_account("TRADER-AI-003", "David Mutua", "+254733000333", initial_krt_deposit=3000.0)

    # Query Market Intelligence
    res_market = karisfx_service.ai_economy.query_ai_service(
        service_name="MARKET_INTELLIGENCE",
        query_text="Analyze KES/USD volatility trajectory",
        account_tier="STANDARD",
        krt_wallet_balance=3000.0,
        staked_amount_krt=0.0
    )
    assert res_market["service_executed"] == "MARKET_INTELLIGENCE"
    assert res_market["premium_tier_active"] is True  # Because balance >= 2500 KRT
    assert "Rule 10" in res_market["rule_10_advisory"]
    assert res_market["market_sentiment"] == "BULLISH_CONSOLIDATION"

    # Query Portfolio Optimization
    res_port = karisfx_service.ai_economy.query_ai_service(
        service_name="PORTFOLIO_OPTIMIZATION",
        query_text="Optimize multi-asset mix",
        account_tier="STANDARD",
        krt_wallet_balance=3000.0,
        staked_amount_krt=0.0
    )
    assert res_port["optimized_sharpe_estimate"] == 2.15

def test_karisfx_reward_engine_anti_abuse_controls():
    """
    Verifies that the Reward Engine detects and blocks wash-trading manipulation attempts while rewarding clean activity.
    """
    acc = karisfx_service.onboard_karisfx_account("TRADER-REWARD-004", "Sarah Njoroge", "+254744000444")

    # Attempt a scalp/wash trade claim (holding duration only 15 seconds < 60 seconds minimum)
    blocked_rew = karisfx_service.claim_platform_reward(
        account_id=acc.account_id,
        activity_type="TRADING_ACTIVITY",
        custom_amount_krt=15.0,
        trade_holding_seconds=15.0
    )
    assert blocked_rew.anti_abuse_status == "BLOCKED_WASH_TRADING_VELOCITY_CHECK"
    assert blocked_rew.reward_amount_krt == 0.0

    # Now make a legitimate claim with valid holding duration (3600 seconds)
    clean_rew = karisfx_service.claim_platform_reward(
        account_id=acc.account_id,
        activity_type="TRADING_ACTIVITY",
        custom_amount_krt=15.0,
        trade_holding_seconds=3600.0
    )
    assert clean_rew.anti_abuse_status == "VERIFIED_CLEAN"
    assert clean_rew.reward_amount_krt == 15.0

    # Verify KRT rewards wallet received the payout exactly
    rewards_w = wallet_engine.get_wallet(acc.rewards_wallet_id)
    # Initial balance 100.0 + 15.0 = 115.0
    assert rewards_w.balance == 115.0

def test_karisfx_marketplace_split_settlement():
    """
    Verifies strategy publication and KRT purchase with exact 85/15 split double-entry settlement.
    """
    creator = karisfx_service.onboard_karisfx_account("CREATOR-005", "Brian Ochieng", "+254755000555")
    buyer = karisfx_service.onboard_karisfx_account("BUYER-006", "Linda Wanjiku", "+254766000666", initial_krt_deposit=1000.0)

    item = karisfx_service.publish_marketplace_item(
        creator_account_id=creator.account_id,
        item_type="TRADING_STRATEGY",
        title="East African FX Breakout Alpha v2",
        description="High Sharpe strategy for KES & EUR sessions",
        price_krt=200.0,
        historical_win_rate_pct=72.5,
        sharpe_ratio=2.1
    )
    assert item.status == "PUBLISHED"

    creator_krt_w_before = wallet_engine.get_wallet(creator.krt_wallet_id).balance
    treasury_w_before = karisfx_service.treasury_wallet.balance

    # Purchase the item
    purchase = karisfx_service.purchase_marketplace_item(buyer.account_id, item.item_id)
    assert purchase.price_paid_krt == 200.0
    assert purchase.creator_payout_krt == 170.0  # exactly 85%
    assert purchase.treasury_fee_krt == 30.0     # exactly 15%

    creator_krt_w_after = wallet_engine.get_wallet(creator.krt_wallet_id).balance
    treasury_w_after = karisfx_service.treasury_wallet.balance

    assert abs((creator_krt_w_after - creator_krt_w_before) - 170.0) < 0.001
    assert abs((treasury_w_after - treasury_w_before) - 30.0) < 0.001

def test_karisfx_governance_social_copy_dev_and_aml_compliance():
    """
    Verifies Decentralized Governance voting with Rule 10 AI summary, Social Copy-Trading links,
    Developer App API registration, and continuous AML FIU transaction monitoring.
    """
    voter = karisfx_service.onboard_karisfx_account("VOTER-007", "Peter Kipchumba", "+254777000777", initial_krt_deposit=4000.0)

    # 1. Governance Proposal & Voting
    prop = karisfx_service.create_governance_proposal(
        creator_account_id=voter.account_id,
        category="REWARD_PARAMETERS",
        title="Increase Bug Report KRT Base Reward by 25%",
        description="Encourage higher security bug discovery across developer ecosystem"
    )
    assert "Rule 10 AI Governance Advisory" in prop.ai_impact_summary

    vote = karisfx_service.cast_governance_vote(
        voter_account_id=voter.account_id,
        proposal_id=prop.proposal_id,
        vote_choice="FOR"
    )
    assert vote.voting_power_krt > 0.0
    assert prop.votes_for_krt == vote.voting_power_krt

    # 2. Social Copy-Trading Link
    master = karisfx_service.onboard_karisfx_account("MASTER-008", "Master Trader Ken", "+254788000888")
    link = karisfx_service.link_copy_trade(
        follower_account_id=voter.account_id,
        master_trader_account_id=master.account_id,
        allocation_krt=1000.0,
        copy_ratio=1.5
    )
    assert link.allocation_krt == 1000.0
    assert link.status == "ACTIVE"

    # 3. Developer App Registration
    dev_app = karisfx_service.register_developer_app(
        developer_account_id=voter.account_id,
        app_name="AI Forex Risk Sentinel Bot",
        app_type="TRADING_BOT",
        monetization_fee_krt_per_call=2.5
    )
    assert len(dev_app.api_key_hash) == 64
    assert dev_app.monetization_fee_krt_per_call == 2.5

    # 4. Compliance AML Transaction Monitoring
    # Normal transaction ($500 USD) -> not flagged
    log_clean = karisfx_service.audit_compliance_and_aml(voter.account_id, "WITHDRAWAL_USD", 500.0)
    assert log_clean.cbk_fiu_flagged is False

    # Large transaction ($15,000 USD) -> flagged per CBK/FIU rules
    log_flagged = karisfx_service.audit_compliance_and_aml(voter.account_id, "DEPOSIT_WIRE_USD", 15000.0)
    assert log_flagged.cbk_fiu_flagged is True
    assert log_flagged.aml_risk_score == 85.0
    assert "exceeds CBK/FIU $10,000 reporting threshold" in log_flagged.audit_notes

    # Verify AML alert event published
    aml_events = [e for e in event_bus.event_store if e.event_type == "KARISFX_AML_ALERT_TRIGGERED"]
    assert len(aml_events) >= 1
