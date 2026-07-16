import pytest
from datetime import datetime, timezone, timedelta
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType
from src.verticals.power_bot_x.service import PowerBotXService

@pytest.fixture
def power_bot_env():
    # Isolate state across test runs
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0" * 64
    event_bus.event_store.clear()

    # Initialize Treasury and Escrow wallets
    treasury = wallet_engine.get_or_create_wallet("ORG-TREASURY-MAIN", "ORG-POWER-BOT-X-MAIN", WalletType.RESERVE_WALLET, AssetType.KRT, 1000000.0)
    escrow = wallet_engine.get_or_create_wallet("SYSTEM-ESCROW-POOL", "ORG-POWER-BOT-X-MAIN", WalletType.SETTLEMENT_WALLET, AssetType.KRT, 0.0)
    eatery_merchant = wallet_engine.get_or_create_wallet("ORG-KARIS-EATERY-MAIN", "ORG-KARIS-EATERY-MAIN", WalletType.KRT_WALLET, AssetType.KRT, 0.0)
    
    svc = PowerBotXService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
    svc.treasury_id = treasury.wallet_id
    svc.escrow_id = escrow.wallet_id
    svc.merchant_id = eatery_merchant.wallet_id
    return svc, event_bus, ledger_engine, wallet_engine

def test_power_bot_x_registration_and_whatsapp_experience(power_bot_env):
    svc, eb, le, we = power_bot_env
    
    # 1. Register User via WhatsApp
    profile = svc.register_user("USER-WA-Kamau", "254712345678", "WHATSAPP", referring_agent_id="AGENT-David")
    assert profile.user_id == "USER-WA-Kamau"
    assert profile.total_reputation_points >= 151
    
    # Verify POWER_BOT_USER_REGISTERED event was emitted
    registered_events = [e for e in eb.event_store if e.event_type == "POWER_BOT_USER_REGISTERED"]
    assert len(registered_events) == 1
    assert registered_events[0].payload["discovery_channel"] == "WHATSAPP"

    # 2. Create Fixture & Generate WhatsApp Status Kit
    fixture = svc.create_fixture("Gor Mahia vs AFC Leopards", "FOOTBALL_DERBY", datetime.now(timezone.utc) + timedelta(hours=24))
    package = svc.whatsapp_experience.generate_whatsapp_status_package(fixture, "AGENT-David", "SWAHILI_SHENG")
    
    assert package["target_channel"] == "WHATSAPP_STATUS"
    assert "Gor Mahia vs AFC Leopards" in package["match_card"]["team_a"] + " vs " + package["match_card"]["team_b"]
    assert "Komaa na Power BOT X" in package["voice_note_script"]
    assert "wa.me/254700000000" in package["deep_link"]

    # 3. Simulate incoming WhatsApp bot message
    reply = svc.whatsapp_experience.handle_whatsapp_incoming_message("254712345678", f"JOIN_AGENT-David_{fixture.fixture_id}")
    assert reply["reply_type"] == "WELCOME_JOIN"
    assert "AGENT-DAVID" in reply["message"].upper()

def test_power_bot_x_ai_copilot_and_agent_coaching(power_bot_env):
    svc, eb, le, we = power_bot_env
    fixture = svc.create_fixture("Tusker FC vs Sofapaka", "FOOTBALL_PREMIER", datetime.now(timezone.utc) + timedelta(days=2))
    
    # 1. Test AI Copilot Tactical Form & Uncertainty Analysis (Rule 10)
    analysis = svc.ai_copilot.analyze_fixture_form(fixture)
    assert "uncertainty_index" in analysis["confidence_intervals_and_uncertainty"]
    assert "does NOT promise match outcomes" in analysis["ai_copilot_disclaimer"]
    
    # 2. Test Living AI Content Engine (Personalized campaign package)
    campaign = svc.ai_copilot.generate_agent_campaign("AGENT-Sarah", fixture, "WHATSAPP_STATUS", "ENGLISH")
    assert campaign.agent_user_id == "AGENT-Sarah"
    assert campaign.predicted_conversion_rate > 0.0
    assert "Don't guess—use the Power BOT X AI Copilot!" in campaign.media_payload_json
    
    # 3. Test Agent Coaching Intelligence
    coaching = svc.ai_copilot.coach_underperforming_agent("AGENT-Sarah", current_conversions=2, total_posts=45)
    assert coaching["current_metrics"]["conversion_rate_pct"] == round((2/45)*100, 2)
    assert len(coaching["actionable_recommendations"]) == 3

def test_power_bot_x_deposit_predict_and_settle_lifecycle(power_bot_env):
    svc, eb, le, we = power_bot_env
    fixture = svc.create_fixture("Shabana vs Kakamega Homeboyz", "FOOTBALL_COUNTY", datetime.now(timezone.utc) + timedelta(hours=6))
    
    # 1. Process M-Pesa KES Deposit -> Mint KRT (`Rule 5` & `Rule 9`)
    dep_res = svc.process_mpesa_deposit_and_mint_krt("USER-Amina", 1000.0, "QWX8992110", svc.treasury_id)
    assert dep_res["converted_krt_amount"] == 1000.0
    assert dep_res["new_krt_balance"] == 1000.0
    assert le.last_hash != "0" * 64  # Cryptographic audit hash generated
    
    # Verify events
    assert any(e.event_type == "POWER_BOT_DEPOSIT_COMPLETED" for e in eb.event_store)
    assert any(e.event_type == "POWER_BOT_KRT_MINTED" for e in eb.event_store)

    # 2. Submit Prediction (`Escrow KRT Stake via Rule 9 double entry`)
    pred = svc.submit_prediction("USER-Amina", fixture.fixture_id, "SHABANA_WIN", 400.0, svc.escrow_id)
    assert pred.stake_krt == 400.0
    assert pred.status == "PENDING_SETTLEMENT"
    
    user_krt_wallet = we.get_wallet_by_keys("USER-Amina", "ORG-POWER-BOT-X-MAIN", WalletType.KRT_WALLET, AssetType.KRT)
    assert user_krt_wallet.balance == 600.0  # 1000 - 400 escrowed
    
    # 3. Settle Match & Payout Winners (`Rule 9` double entry & Reputation boost)
    settle_res = svc.settle_match_and_payout(fixture.fixture_id, "SHABANA_WIN", svc.escrow_id)
    assert settle_res["winning_predictions_count"] == 1
    assert settle_res["total_payout_krt"] == round(400.0 * 1.85, 4)
    
    # Verify user wallet credited with winnings
    assert user_krt_wallet.balance == round(600.0 + (400.0 * 1.85), 4)
    assert pred.status == "WON"
    
    # Verify non-financial reputation boost
    profile = svc.reputation_profiles.get("USER-Amina")
    if profile:
        assert profile.fair_participation_score >= 125

def test_power_bot_x_digital_twin_and_merchant_redemption(power_bot_env):
    svc, eb, le, we = power_bot_env
    
    # 1. Digital Twin Real-Time Snapshot & Policy Simulation (`Rule 10`)
    snapshot = svc.digital_twin.generate_real_time_snapshot(krt_circulation=500000.0, active_predictions=120)
    assert snapshot.treasury_health_score > 80.0
    
    sim = svc.digital_twin.simulate_policy_change(snapshot, proposed_agent_commission_pct=12.0, proposed_staking_bonus_pct=4.0)
    assert sim["solvency_assessment"] == "SOLVENT AND SUSTAINABLE"
    assert "Requires explicit RBAC approval" in sim["rule_10_gate"]

    # 2. Digital Economy Marketplace Gateway (Immediate Meal & Produce Redemption)
    # Fund User wallet with 500 KRT
    import uuid
    user_wallet = we.get_or_create_wallet("USER-Winner", "ORG-POWER-BOT-X-MAIN", WalletType.KRT_WALLET, AssetType.KRT)
    le.record_transaction(
        transaction_id=str(uuid.uuid4()),
        asset_type=AssetType.KRT,
        debit_wallet_id=svc.treasury_id,
        credit_wallet_id=user_wallet.wallet_id,
        amount=500.0,
        currency="KRT",
        organization_id="ORG-POWER-BOT-X-MAIN",
        trigger_event_id="FUND-WINNER",
        description="Test Fund"
    )
    
    spend_res = svc.redeem_krt_at_karis_merchant("USER-Winner", "ORG-KARIS-EATERY-MAIN", svc.merchant_id, 350.0, "KARIS_EATERY", "MEAL-ORDER-777")
    assert spend_res["status"] == "MERCHANT_REDEMPTION_SUCCESS"
    assert spend_res["remaining_user_krt_balance"] == 150.0
    
    merchant_wallet = we.get_wallet(svc.merchant_id)
    assert merchant_wallet.balance == 350.0
    
    # Verify POWER_BOT_MERCHANT_PAID event
    merchant_events = [e for e in eb.event_store if e.event_type == "POWER_BOT_MERCHANT_PAID"]
    assert len(merchant_events) == 1
    assert merchant_events[0].payload["vertical_target"] == "KARIS_EATERY"
