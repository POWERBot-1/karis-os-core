import pytest
from src.core.event_bus import event_bus
from src.core.whitelabel_engine import whitelabel_engine
from src.config import config

@pytest.fixture
def whitelabel_env():
    event_bus.event_store.clear()
    return whitelabel_engine, event_bus

def test_whitelabel_customization_and_branding_switch(whitelabel_env):
    engine, eb = whitelabel_env

    # 1. Verify exact pre-seeded profiles exist
    profiles = engine.get_all_profiles()
    assert len(profiles) >= 4
    assert any(p["profile_code"] == "SAFARICOM_MPESA_ENTERPRISE" for p in profiles)
    assert any(p["profile_code"] == "EQUITY_BANK_FINTECH_HUB" for p in profiles)
    assert any(p["profile_code"] == "PALPLUS_GLOBAL_CHECKOUT_OS" for p in profiles)

    # 2. Apply Safaricom M-Pesa Enterprise Profile
    res_saf = engine.apply_whitelabel_profile("SAFARICOM_MPESA_ENTERPRISE", "ORG-KARIS-RETAIL", "ADMIN-CFO-01")
    assert res_saf["status"] == "WHITELABEL_APPLIED_SUCCESS"
    assert config.PLATFORM_NAME == "M-Pesa Enterprise & Digital Economy OS"
    assert engine.active_profile_code == "SAFARICOM_MPESA_ENTERPRISE"

    # Verify WHITELABEL_BRANDING_APPLIED event emitted (`Rule 6`)
    wl_events = [e for e in eb.event_store if e.event_type == "WHITELABEL_BRANDING_APPLIED"]
    assert len(wl_events) == 1
    assert wl_events[0].payload["profile_code"] == "SAFARICOM_MPESA_ENTERPRISE"

    # 3. Apply PalPlus Global Checkout OS Profile
    res_pal = engine.apply_whitelabel_profile("PALPLUS_GLOBAL_CHECKOUT_OS", "ORG-KARIS-RETAIL", "ADMIN-CFO-01")
    assert config.PLATFORM_NAME == "PalPlus Universal Commerce & Checkout OS"
    assert res_pal["active_profile"]["active_payment_link_id"] == "6e8de0bc-1284-4bba-a5de-f886665bf18f"

    # 4. Restore Default
    engine.apply_whitelabel_profile("KARIS_OS_DEFAULT")
    assert config.PLATFORM_NAME == "KARIS OS™ Enterprise Platform"
