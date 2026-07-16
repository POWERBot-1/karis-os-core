import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus
from src.config import config

class WhiteLabelCustomizationEngine:
    """
    KARIS OS™ White-Label Client Customization & Multi-Tenant Branding Engine (`Frontier D / Section 35`).
    Enforces Rule 7 ('Everything is Configurable'). Allows commercial partners (`Safaricom`, `Equity Bank`, `PalPlus`)
    to dynamically reconfigure platform metadata, color palettes, active payment links (`6e8de0bc...`), and default currencies
    without modifying underlying double-entry accounting kernel code (`Rule 5 & Rule 9`).
    """
    def __init__(self):
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.active_profile_code: str = "KARIS_OS_DEFAULT"
        self._seed_default_whitelabel_profiles()

    def _seed_default_whitelabel_profiles(self):
        defaults = [
            (
                "KARIS_OS_DEFAULT", "KARIS OS™ Enterprise Platform", "#0B2545", "#1D4ED8", "KES",
                "6e8de0bc-1284-4bba-a5de-f886665bf18f", "Unified Enterprise & Digital Economy Operating System for East Africa."
            ),
            (
                "SAFARICOM_MPESA_ENTERPRISE", "M-Pesa Enterprise & Digital Economy OS", "#10B981", "#059669", "KES",
                "6e8de0bc-1284-4bba-a5de-f886665bf18f", "Safaricom M-Pesa Daraja-powered multi-vertical enterprise and smallholder aggregation hub."
            ),
            (
                "EQUITY_BANK_FINTECH_HUB", "Equity Digital Banking & Agri-Fintech OS", "#8B0000", "#B22222", "KES",
                "6e8de0bc-1284-4bba-a5de-f886665bf18f", "Equity Bank agricultural input financing, PAYG solar lending, and regional CBDC clearing platform."
            ),
            (
                "PALPLUS_GLOBAL_CHECKOUT_OS", "PalPlus Universal Commerce & Checkout OS", "#2563EB", "#1E40AF", "KES",
                "6e8de0bc-1284-4bba-a5de-f886665bf18f", "PalPlus hosted payment link checkout gateway powering 18 omnichannel commerce and prediction verticals."
            )
        ]
        for code, name, p_color, s_color, curr, link_id, desc in defaults:
            self.profiles[code] = {
                "profile_code": code,
                "platform_name": name,
                "primary_color_hex": p_color,
                "secondary_color_hex": s_color,
                "default_currency": curr,
                "active_payment_link_id": link_id,
                "description": desc,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

    def get_all_profiles(self) -> List[Dict[str, Any]]:
        return list(self.profiles.values())

    def get_active_profile(self) -> Dict[str, Any]:
        return self.profiles.get(self.active_profile_code, self.profiles["KARIS_OS_DEFAULT"])

    def apply_whitelabel_profile(
        self,
        profile_code: str,
        organization_id: str = "ORG-KARIS-RETAIL",
        actor_identity_id: str = "ADMIN-CFO-01"
    ) -> Dict[str, Any]:
        """
        Applies a white-label branding profile across the operating system (`Rule 7 & Rule 6`).
        """
        code_upper = profile_code.strip().upper()
        if code_upper not in self.profiles:
            raise KeyError(f"White-label profile code '{profile_code}' not found in registry.")

        prof = self.profiles[code_upper]
        self.active_profile_code = code_upper

        # Dynamically update configuration properties (`Rule 7`)
        config.PLATFORM_NAME = prof["platform_name"]
        config.DEFAULT_CURRENCY = prof["default_currency"]

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="WHITELABEL_BRANDING_APPLIED",
            event_category=EventCategory.GOVERNANCE,
            actor_identity_id=actor_identity_id,
            organization_id=organization_id,
            correlation_id=prof["profile_code"],
            source_module="WHITELABEL_CUSTOMIZATION_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "profile_code": prof["profile_code"],
                "platform_name": prof["platform_name"],
                "primary_color_hex": prof["primary_color_hex"],
                "default_currency": prof["default_currency"],
                "active_payment_link_id": prof["active_payment_link_id"]
            }
        )
        event_bus.publish(ev)

        return {
            "status": "WHITELABEL_APPLIED_SUCCESS",
            "active_profile": prof,
            "system_config_updated": {
                "PLATFORM_NAME": config.PLATFORM_NAME,
                "DEFAULT_CURRENCY": config.DEFAULT_CURRENCY
            },
            "message": f"Platform successfully white-labeled to '{prof['platform_name']}' (`{prof['profile_code']}`). All 18 verticals active under double-entry Rule 9 protection."
        }

whitelabel_engine = WhiteLabelCustomizationEngine()
