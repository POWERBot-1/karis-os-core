import pytest
from datetime import datetime, timezone
import uuid
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType
from src.verticals.karis_loop.service import KarisLoopService

@pytest.fixture
def karis_loop_env():
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0" * 64
    event_bus.event_store.clear()

    # Initialize baseline reserves and user wallets
    treasury = wallet_engine.get_or_create_wallet("ORG-TREASURY-MAIN", "ORG-KARIS-RETAIL", WalletType.RESERVE_WALLET, AssetType.KRT, 1000000.0)
    user_amina_krt = wallet_engine.get_or_create_wallet("USER-AMINA-777", "ORG-KARIS-RETAIL", WalletType.KRT_WALLET, AssetType.KRT, 500.0)
    creator_david_krt = wallet_engine.get_or_create_wallet("CREATOR-DAVID-01", "ORG-KARIS-RETAIL", WalletType.KRT_WALLET, AssetType.KRT, 0.0)
    merchant_krt = wallet_engine.get_or_create_wallet("ORG-KARIS-RETAIL", "ORG-KARIS-RETAIL", WalletType.KRT_WALLET, AssetType.KRT, 0.0)

    svc = KarisLoopService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
    return svc, event_bus, ledger_engine, wallet_engine

def test_karis_loop_profiles_communities_and_shoppable_posts(karis_loop_env):
    svc, eb, le, we = karis_loop_env

    # 1. Register profile
    prof = svc.register_profile("CREATOR-DAVID-01", "ORG-KARIS-RETAIL", "creator_david", "David Kamau", "CREATOR_USER")
    assert prof.handle_username == "creator_david"
    assert "CREATOR-DAVID-01" in svc.graph_engine.social_graph

    # 2. Create community
    comm = svc.create_community("Machakos County Farmers Guild", "REGIONAL_AGRI_GUILD", "Machakos County", "CREATOR-DAVID-01", "ORG-KARIS-RETAIL")
    assert comm.name == "Machakos County Farmers Guild"

    # 3. Create shoppable short-form video post (`Rule 6 & Rule 10 check`)
    post = svc.create_post("CREATOR-DAVID-01", comm.community_id, "SHORT_VIDEO", "Check out these Grade-A Export Avocados!", '{"video_url": "/avos.mp4"}', "PROD-AVO-01", 350.0)
    assert post.shoppable_price_kes == 350.0
    assert post.ai_moderation_status == "APPROVED_CLEAN"
    assert "PROD-AVO-01" in svc.graph_engine.commerce_graph.get(post.post_id, [])

    # Verify events
    assert any(e.event_type == "LOOP_PROFILE_REGISTERED" for e in eb.event_store)
    assert any(e.event_type == "LOOP_COMMUNITY_CREATED" for e in eb.event_store)
    assert any(e.event_type == "LOOP_CONTENT_POSTED" for e in eb.event_store)

def test_karis_loop_tipping_shoppable_checkout_and_ai_moderation(karis_loop_env):
    svc, eb, le, we = karis_loop_env
    comm = svc.create_community("Agri Creators", "GUILD", "Machakos", "CREATOR-DAVID-01", "ORG-KARIS-RETAIL")
    post = svc.create_post("CREATOR-DAVID-01", comm.community_id, "SHORT_VIDEO", "Great harvest update!", '{"video_url": "/test.mp4"}', "PROD-AVO-01", 350.0)

    # 1. Execute Double-Entry KRT Tip (`Rule 5 & Rule 9`)
    tip_res = svc.tip_creator("USER-AMINA-777", "CREATOR-DAVID-01", post.post_id, 50.0)
    assert tip_res["status"] == "TIP_SETTLED_SUCCESS"
    assert tip_res["remaining_tipper_krt_balance"] == 450.0  # 500 - 50
    assert tip_res["creator_new_krt_balance"] == 50.0
    assert tip_res["audit_hash"] != "0" * 64

    # 2. Complete Shoppable Checkout Directly From Post (`One Wallet Economy`)
    chk_res = svc.checkout_shoppable_product("USER-AMINA-777", post.post_id, "PROD-AVO-01", "ORG-KARIS-RETAIL", 350.0, "KRT_WALLET")
    assert chk_res["status"] == "SHOPPABLE_CHECKOUT_SUCCESS"
    assert chk_res["loyalty_krt_reward_earned"] == round(350.0 * 0.05, 4)  # 17.5 KRT
    assert chk_res["remaining_buyer_balance"] == round(450.0 - 350.0 + 17.5, 4)  # 117.5 KRT

    # 3. Test AI Moderation Guardrail (`Rule 10`) on toxic post
    toxic_post = svc.create_post("USER-TOXIC-01", comm.community_id, "TEXT", "This product is a complete scam and fake!", "{}", None, 0.0)
    assert toxic_post.ai_moderation_status == "FLAGGED_PENDING_HUMAN_REVIEW"

    # Verify events
    assert any(e.event_type == "LOOP_CREATOR_TIPPED" for e in eb.event_store)
    assert any(e.event_type == "LOOP_SHOPPABLE_CHECKOUT_COMPLETED" for e in eb.event_store)
