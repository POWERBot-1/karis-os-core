#!/usr/bin/env python3
"""
KARIS OS™ :: Option 4: Commercial White-Label Re-Branding Demonstration (`Frontier D`).
Demonstrates real-time multi-tenant white-label customization across East Africa.
Switches platform branding dynamically across Safaricom M-Pesa Green, Equity Bank Maroon,
PalPlus Blue, and KARIS OS Navy without modifying any source code (`Rule 7`).
Run: python3 run_whitelabel_rebranding_demo.py
"""

import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi.testclient import TestClient
from src.api.main import app
from src.core.whitelabel_engine import whitelabel_engine
from src.core.event_bus import event_bus

client = TestClient(app)

def print_header(title: str):
    print("\n" + "=" * 90)
    print(f"  {title}")
    print("=" * 90)

def run_demo():
    print_header("KARIS OS™ :: OPTION 4: WHITE-LABEL CLIENT CUSTOMIZATION ENGINE (`FRONTIER D`)")
    print("Demonstrating real-time platform re-branding across Safaricom, Equity Bank, PalPlus & KARIS OS.")
    
    event_bus.event_store.clear()

    # -------------------------------------------------------------------------
    # STEP 1: VERIFY INITIAL ACTIVE PROFILE (`KARIS_OS_DEFAULT`)
    # -------------------------------------------------------------------------
    print("\n[STEP 1] Inspecting Initial Active White-Label Profile...")
    res_initial = client.get("/api/v1/whitelabel/active")
    assert res_initial.status_code == 200
    init_prof = res_initial.json()
    print(f"  ✔ [Active Profile] Code: {init_prof['profile_code']} | Name: '{init_prof['platform_name']}'")
    print(f"  ✔ [Color Palette] Primary: {init_prof['primary_color_hex']} (KARIS Navy) | Secondary: {init_prof['secondary_color_hex']}")
    print(f"  ✔ [Universal Checkout Link] {init_prof['active_payment_link_id']}")

    # -------------------------------------------------------------------------
    # STEP 2: SWITCH TO SAFARICOM M-PESA ENTERPRISE PROFILE (`#10B981`)
    # -------------------------------------------------------------------------
    print("\n[STEP 2] Applying Profile #1: `SAFARICOM_MPESA_ENTERPRISE` (`Safaricom Green`)...")
    res_safaricom = client.post("/api/v1/whitelabel/apply", json={
        "profile_code": "SAFARICOM_MPESA_ENTERPRISE",
        "organization_id": "ORG-SAFARICOM-AGRI",
        "actor_identity_id": "ADMIN-CEO-SAFARICOM"
    })
    assert res_safaricom.status_code == 200, f"Failed Safaricom profile switch: {res_safaricom.text}"
    saf_data = res_safaricom.json()
    print(f"  ✔ [Profile Switch Accepted] New Platform Name: '{saf_data['active_profile']['platform_name']}'")
    print(f"  ✔ [Dynamic Color Theme Applied] Primary Color: {saf_data['active_profile']['primary_color_hex']} (Safaricom Green)")
    print(f"  ✔ [Target Verticals & Scope] {saf_data['active_profile']['description']}")
    print(f"  ✔ [Event Chaining (`Rule 6 & 7`)] Emitted `WHITELABEL_BRANDING_APPLIED` event (Correlation: {event_bus.event_store[-1].correlation_id}...)")

    # -------------------------------------------------------------------------
    # STEP 3: SWITCH TO EQUITY DIGITAL BANKING & AGRI-FINTECH PROFILE (`#8B0000`)
    # -------------------------------------------------------------------------
    print("\n[STEP 3] Applying Profile #2: `EQUITY_BANK_FINTECH_HUB` (`Equity Maroon/Red`)...")
    res_equity = client.post("/api/v1/whitelabel/apply", json={
        "profile_code": "EQUITY_BANK_FINTECH_HUB",
        "organization_id": "ORG-EQUITY-AGRI",
        "actor_identity_id": "ADMIN-MD-EQUITY"
    })
    assert res_equity.status_code == 200, f"Failed Equity profile switch: {res_equity.text}"
    eq_data = res_equity.json()
    print(f"  ✔ [Profile Switch Accepted] New Platform Name: '{eq_data['active_profile']['platform_name']}'")
    print(f"  ✔ [Dynamic Color Theme Applied] Primary Color: {eq_data['active_profile']['primary_color_hex']} (Equity Maroon/Red)")
    print(f"  ✔ [Target Verticals & Scope] {eq_data['active_profile']['description']}")

    # -------------------------------------------------------------------------
    # STEP 4: SWITCH TO PALPLUS UNIVERSAL COMMERCE & CHECKOUT PROFILE (`#2563EB`)
    # -------------------------------------------------------------------------
    print("\n[STEP 4] Applying Profile #3: `PALPLUS_GLOBAL_CHECKOUT_OS` (`PalPlus Blue`)...")
    res_palplus = client.post("/api/v1/whitelabel/apply", json={
        "profile_code": "PALPLUS_GLOBAL_CHECKOUT_OS",
        "organization_id": "ORG-PALPLUS-GLOBAL",
        "actor_identity_id": "ADMIN-VP-PALPLUS"
    })
    assert res_palplus.status_code == 200, f"Failed PalPlus profile switch: {res_palplus.text}"
    pal_data = res_palplus.json()
    print(f"  ✔ [Profile Switch Accepted] New Platform Name: '{pal_data['active_profile']['platform_name']}'")
    print(f"  ✔ [Dynamic Color Theme Applied] Primary Color: {pal_data['active_profile']['primary_color_hex']} (PalPlus Blue)")
    print(f"  ✔ [Target Verticals & Scope] {pal_data['active_profile']['description']}")

    # -------------------------------------------------------------------------
    # STEP 5: RESTORE KARIS OS™ DEFAULT ENTERPRISE PROFILE (`#0B2545`)
    # -------------------------------------------------------------------------
    print("\n[STEP 5] Restoring Default Profile: `KARIS_OS_DEFAULT` (`KARIS Navy`)....")
    res_restore = client.post("/api/v1/whitelabel/apply", json={
        "profile_code": "KARIS_OS_DEFAULT",
        "organization_id": "ORG-KARIS-RETAIL",
        "actor_identity_id": "ADMIN-CFO-01"
    })
    assert res_restore.status_code == 200, f"Failed default restoration: {res_restore.text}"
    restore_data = res_restore.json()
    print(f"  ✔ [Default Restoration Verified] Active Name: '{restore_data['active_profile']['platform_name']}'")
    print(f"  ✔ [Primary Theme Restored] Primary Color: {restore_data['active_profile']['primary_color_hex']} (KARIS Navy)")

    # -------------------------------------------------------------------------
    # FINAL AUDIT SWEEP ACROSS EVENT BUS (`RULE 6 & RULE 8`)
    # -------------------------------------------------------------------------
    print("\n[FINAL VERIFICATION] Auditing Event Store for Multi-Tenant Re-Branding Trails (`Rule 6`)...")
    wl_events = [e for e in event_bus.event_store if e.event_type == "WHITELABEL_BRANDING_APPLIED"]
    print(f"  ✔ Captured {len(wl_events)} complete `WHITELABEL_BRANDING_APPLIED` audit events in Event Store!")
    for idx, ev in enumerate(wl_events, 1):
        p_code = ev.payload["profile_code"]
        p_name = ev.payload["platform_name"]
        p_color = ev.payload["primary_color_hex"]
        print(f"    -> Event {idx}: Profile={p_code:<28} | Color={p_color} | Org={ev.organization_id}")

    print_header("COMMERCIAL WHITE-LABEL RE-BRANDING DEMONSTRATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_demo()
