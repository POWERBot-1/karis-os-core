"""
KARIS OS™ :: Multi-Tenant Integration Test Suite for COSMOX™ Universal AI Marketplace (`Section 57`).
Verifies Universal Wallet onboarding (`fiat, krt, rewards, escrow, merchant, driver`), AI Dynamic Pricing & Shopping,
Marketplace Checkout with Escrow hold (`Rule 2`), Logistics Route AI strictly enforcing Rule 4 Escrow Release,
Referral Network payouts, Developer Digital Service checkouts (85/15 split), Tokenomics Deflationary Burn (`burn_krt`),
and Multi-Signature Treasury gating (`Rule 10`).
"""

import pytest
from datetime import datetime, timezone
from src.core.wallet_engine import wallet_engine
from src.core.ledger_engine import ledger_engine
from src.core.event_bus import event_bus
from src.verticals.cosmox.service import cosmox_service
from src.domain.models import WalletType, AssetType

@pytest.fixture(autouse=True)
def setup_cosmox_environment():
    """
    Reset singleton state and initialize clean test wallets and system reserve pools.
    """
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0" * 64
    event_bus.event_store.clear()

    cosmox_service.accounts.clear()
    cosmox_service.products.clear()
    cosmox_service.orders.clear()
    cosmox_service.deliveries.clear()
    cosmox_service.referrals.clear()
    cosmox_service.staking_positions.clear()
    cosmox_service.digital_services.clear()
    cosmox_service.vesting_schedules.clear()
    cosmox_service.proposals.clear()
    cosmox_service.votes.clear()
    cosmox_service.multisig_requests.clear()

    cosmox_service._init_system_pools()
    yield

def test_cosmox_universal_wallet_onboarding_and_ai_dynamic_pricing():
    """
    Verifies that onboarded accounts automatically receive their 6 Universal Wallets and AI dynamic pricing functions correctly.
    """
    seller = cosmox_service.onboard_cosmox_account("SELLER-CMX-001", account_type="MERCHANT")
    buyer = cosmox_service.onboard_cosmox_account("BUYER-CMX-002", account_type="BUYER", initial_krt=5000.0)

    assert seller.kyc_status == "VERIFIED_TIER_3"
    assert buyer.kyc_status == "VERIFIED_TIER_3"

    # Verify all 6 Universal Wallets exist for the buyer
    fiat_w = wallet_engine.get_wallet(buyer.fiat_wallet_id)
    krt_w = wallet_engine.get_wallet(buyer.krt_wallet_id)
    rewards_w = wallet_engine.get_wallet(buyer.rewards_wallet_id)
    escrow_w = wallet_engine.get_wallet(buyer.escrow_wallet_id)
    merchant_w = wallet_engine.get_wallet(buyer.merchant_wallet_id)
    driver_w = wallet_engine.get_wallet(buyer.driver_wallet_id)

    assert fiat_w and fiat_w.balance == 50000.0
    assert krt_w and krt_w.balance == 5000.0
    assert rewards_w and rewards_w.balance == 100.0
    assert escrow_w and escrow_w.balance == 0.0

    # Create product with AI dynamic pricing
    prod = cosmox_service.create_product(
        seller_account_id=seller.account_id,
        product_name="Solar Home Inverter Kit 3KVA",
        category="PHYSICAL_GOODS",
        base_price_krt=1000.0,
        inventory_count=10,  # low stock -> triggers AI scarcity premium (+8%)
        ai_dynamic_pricing_enabled=True
    )
    assert prod.current_price_krt == 1080.0
    assert prod.status == "ACTIVE"

def test_cosmox_order_checkout_escrow_and_strict_rule_4_delivery_release():
    """
    Verifies marketplace checkout locking KRT in Escrow (`Rule 2 & Rule 5 & Rule 9`), driver dispatch,
    and strict Rule 4 escrow release upon confirmed delivery along with deflationary burn and cashback.
    """
    seller = cosmox_service.onboard_cosmox_account("SELLER-CMX-003", account_type="MERCHANT")
    buyer = cosmox_service.onboard_cosmox_account("BUYER-CMX-004", account_type="BUYER", initial_krt=3000.0)
    driver = cosmox_service.onboard_cosmox_account("DRIVER-CMX-005", account_type="DRIVER")

    prod = cosmox_service.create_product(
        seller_account_id=seller.account_id,
        product_name="Machakos Coffee Beans (25kg Bag)",
        category="AGRICULTURE",
        base_price_krt=200.0,
        inventory_count=100,
        ai_dynamic_pricing_enabled=False
    )

    # 1. Buyer checks out 5 bags -> 1,000 KRT locked in Escrow
    order = cosmox_service.checkout_marketplace_order(buyer.account_id, prod.product_id, quantity=5)
    assert order.total_price_krt == 1000.0
    assert order.seller_payout_krt == 880.0       # 88%
    assert order.platform_commission_krt == 120.0 # 12%
    assert order.cashback_reward_krt == 15.0      # 1.5%
    assert order.escrow_status == "ESCROWED_PENDING_DELIVERY"
    assert prod.inventory_count == 95

    buyer_krt_w = wallet_engine.get_wallet(buyer.krt_wallet_id)
    assert buyer_krt_w.balance == 2000.0  # 3000 - 1000

    # 2. Dispatch Driver -> locks +25 KRT bonus in Main Escrow Pool under Rule 4
    deliv = cosmox_service.dispatch_logistics_delivery(
        order_id=order.order_id,
        driver_account_id=driver.account_id,
        origin="Nairobi Coffee Warehouse",
        destination="Mlolongo Supermarket",
        distance_km=25.0
    )
    assert deliv.driver_payout_fiat == 1250.0  # 25 km * 50 KES
    assert deliv.driver_bonus_krt == 25.0
    assert deliv.status == "ASSIGNED_IN_TRANSIT"

    # Verify driver KRT wallet before delivery confirmation
    driver_krt_w_before = wallet_engine.get_wallet(driver.krt_wallet_id).balance
    seller_merchant_w_before = wallet_engine.get_wallet(seller.merchant_wallet_id).balance
    treasury_w_before = cosmox_service.treasury_wallet.balance
    burn_w_before = cosmox_service.burn_wallet.balance

    # 3. Confirm Delivery -> strictly triggers escrow release (`Rule 4 & Rule 9`)
    settled_order, settled_deliv = cosmox_service.confirm_delivery_and_settle_escrow(deliv.delivery_id)
    assert settled_order.escrow_status == "RELEASED_SETTLED"
    assert settled_deliv.status == "DELIVERY_CONFIRMED"

    driver_krt_w_after = wallet_engine.get_wallet(driver.krt_wallet_id).balance
    seller_merchant_w_after = wallet_engine.get_wallet(seller.merchant_wallet_id).balance
    treasury_w_after = cosmox_service.treasury_wallet.balance
    burn_w_after = cosmox_service.burn_wallet.balance

    # Check exactly +880 KRT to seller merchant wallet
    assert abs((seller_merchant_w_after - seller_merchant_w_before) - 880.0) < 0.001

    # Check exactly +25 KRT to driver KRT wallet under Rule 4
    assert abs((driver_krt_w_after - driver_krt_w_before) - 25.0) < 0.001

    # Check platform commission (120 KRT) minus 2% deflationary burn (2.4 KRT)
    expected_burn = round(120.0 * 0.02, 4)  # 2.4 KRT
    assert abs((burn_w_after - burn_w_before) - expected_burn) < 0.001

    # Check buyer cashback (+15 KRT_REWARDS to buyer rewards wallet)
    buyer_rewards_w = wallet_engine.get_wallet(buyer.rewards_wallet_id)
    assert buyer_rewards_w.balance == 115.0  # initial 100 + 15

    # Verify ledger integrity
    from src.security.audit import audit_engine
    ledger_audit = audit_engine.verify_ledger_chain()
    assert ledger_audit["status"] == "VERIFIED_CLEAN"

def test_cosmox_referral_network_and_digital_service_checkout():
    """
    Verifies referral network verification across tiers (`INDIVIDUAL, MERCHANT`) and developer digital service checkouts.
    """
    referrer = cosmox_service.onboard_cosmox_account("REF-CMX-006")
    referred_buyer = cosmox_service.onboard_cosmox_account("REF-CMX-007")
    referred_merchant = cosmox_service.onboard_cosmox_account("REF-CMX-008", account_type="MERCHANT")

    # 1. Qualify Individual referral (+100 KRT_REWARDS)
    ref_1 = cosmox_service.qualify_and_payout_referral(referrer.account_id, referred_buyer.account_id, "INDIVIDUAL")
    assert ref_1.reward_krt == 100.0
    assert ref_1.status == "REWARDED_CLEAN"

    # 2. Qualify Merchant referral (+500 KRT_REWARDS)
    ref_2 = cosmox_service.qualify_and_payout_referral(referrer.account_id, referred_merchant.account_id, "MERCHANT")
    assert ref_2.reward_krt == 500.0
    assert ref_2.status == "REWARDED_CLEAN"

    referrer_rewards_w = wallet_engine.get_wallet(referrer.rewards_wallet_id)
    # Initial 100 + 100 + 500 = 700
    assert referrer_rewards_w.balance == 700.0

    # 3. Developer Digital Service Checkout (85/15 split)
    developer = cosmox_service.onboard_cosmox_account("DEV-CMX-009", account_type="DEVELOPER")
    ds = cosmox_service.publish_digital_service(
        developer_account_id=developer.account_id,
        title="COSMOX AI Demand Forecaster Engine v1",
        service_type="AI_TOOL",
        api_endpoint_url="https://api.cosmox.ai/v1/forecast",
        price_krt_per_access=100.0
    )

    buyer = cosmox_service.onboard_cosmox_account("BUYER-CMX-010", initial_krt=500.0)
    dev_krt_before = wallet_engine.get_wallet(developer.krt_wallet_id).balance

    checkout_res = cosmox_service.purchase_digital_service(buyer.account_id, ds.service_id)
    assert checkout_res["status"] == "SUCCESS_SETTLED"
    assert checkout_res["developer_payout_krt"] == 85.0
    assert checkout_res["treasury_fee_krt"] == 15.0

    dev_krt_after = wallet_engine.get_wallet(developer.krt_wallet_id).balance
    assert abs((dev_krt_after - dev_krt_before) - 85.0) < 0.001

def test_cosmox_ai_engine_translation_and_multisig_treasury_rule_10():
    """
    Verifies AI recommendations, multi-lingual translations (`SW, SHENG, EN, FR, AR`), and multi-sig treasury gating (`Rule 10`).
    """
    # 1. AI Recommendation & Translation
    buyer = cosmox_service.onboard_cosmox_account("BUYER-CMX-011")
    recs = cosmox_service.ai_engine.recommend_products(buyer.account_id, ["PHYSICAL_GOODS"], 150)
    assert len(recs["recommended_items"]) == 3
    assert "Rule 10" in recs["rule_10_advisory"]

    trans_sw = cosmox_service.ai_engine.translate_content("Inquiry about delayed order", "SW")
    assert "Swahili Translation" in trans_sw["translated_text"]

    trans_sheng = cosmox_service.ai_engine.translate_content("Inquiry about delayed order", "SHENG")
    assert "Sheng Translation" in trans_sheng["translated_text"]

    # 2. Multi-Sig Treasury Request requiring 2+ RBAC approvals (`Rule 10`)
    admin_1 = cosmox_service.onboard_cosmox_account("ADMIN-CMX-012")
    admin_2 = cosmox_service.onboard_cosmox_account("ADMIN-CMX-013")
    beneficiary = cosmox_service.onboard_cosmox_account("BENEFICIARY-CMX-014", initial_krt=0.0)

    ms_req = cosmox_service.request_multisig_treasury_disbursement(
        requester_account_id=beneficiary.account_id,
        amount_krt=250000.0,
        purpose="Ecosystem Liquidity Bootstrapping Grant for Machakos Hub"
    )
    assert ms_req.status == "PENDING_MULTISIG"
    assert ms_req.required_approvals == 2
    assert ms_req.ai_risk_score == 65.0  # flagged as high value

    # First approval -> should remain pending
    ms_req_1 = cosmox_service.approve_multisig_treasury_request(admin_1.account_id, ms_req.request_id)
    assert ms_req_1.current_approvals == 1
    assert ms_req_1.status == "PENDING_MULTISIG"

    # Second approval -> satisfies quorum (2) -> executes double entry from Treasury to Beneficiary (`Rule 5 & Rule 9`)
    ms_req_2 = cosmox_service.approve_multisig_treasury_request(admin_2.account_id, ms_req.request_id)
    assert ms_req_2.current_approvals == 2
    assert ms_req_2.status == "APPROVED_DISBURSED"

    beneficiary_krt_w = wallet_engine.get_wallet(beneficiary.krt_wallet_id)
    assert beneficiary_krt_w.balance == 250000.0
