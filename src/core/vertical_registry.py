from typing import Dict, List
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus

class VerticalRegistryEngine:
    """
    KARIS OS™ Vertical Registration Framework (Section 35).
    Enforces 'Build once. Configure many. Scale infinitely.'
    Allows dynamic registration of future industries without rebuilding core architecture.
    """
    def __init__(self):
        self.registered_verticals: Dict[str, Dict] = {}
        self._seed_default_verticals()

    def _seed_default_verticals(self):
        defaults = [
            ("AGRICULTURE", "KARIS FARM™ Vertical", "Digitizes agricultural value chains and produce traceability"),
            ("RETAIL_POS", "Omnichannel POS & Supermarket Vertical", "Multi-branch store checkouts, barcode scanning & pricing"),
            ("FOOD_SERVICES", "Eatery & Kitchen Display System KDS", "Cloud kitchen recipe deduction and cooking queues"),
            ("LOGISTICS", "Delivery & Logistics Engine", "AI rider dispatch, proof of delivery and escrow payouts"),
            ("HEALTHCARE", "Healthcare, EMR & Medical Services", "Patient profiles, teleconsultations, prescriptions & CHV checks"),
            ("MOBILITY", "Mobility & Ride-Hailing Vertical", "TukTuk and taxi fleet matching and surge pricing"),
            ("FINANCE", "Investor Capital & Lending Engine", "Growth fund pools, ROI distribution and AI credit scoring"),
            ("POWER_BOT_X", "Autonomous AI Prediction Economy", "WhatsApp-first AI prediction ecosystem, 7 intelligence engines, KRT economy & digital twin"),
            ("KARIS_ENERGY", "KARIS ENERGY & SMART SOLAR GRID™", "Pay-As-You-Go (PAYG) solar systems, IoT smart meter telemetry, KRT-JOULE rewards & microgrid P2P trading"),
            ("KARIS_PHARMA", "KARIS HEALTH & PHARMA-TRACE™", "Cold-chain pharmaceutical telemetry (<8°C), dispensary stockout forecasting & locking"),
            ("KARIS_PROP_SHARE", "KARIS PROP-SHARE & FRAC-EQUITY™", "Fractional real estate syndication, automated rental dividend distributions in KRT via double entry"),
            ("KARIS_EDU_PAY", "KARIS EDU-PAY & CAMPUS GRID™", "Tuition installment schedules, +150 KRT-EDU scholarship awards & campus cafeteria KDS checkouts"),
            ("KARIS_LOOP", "Karis Loop™ Social Intelligence Layer", "Unified 7-Graph social economy combining shoppable video checkouts, KRT tipping, multi-priority feeds & AI moderation")
        ]
        for code, name, desc in defaults:
            self.registered_verticals[code] = {
                "vertical_code": code,
                "vertical_name": name,
                "description": desc,
                "status": "ACTIVE_PRODUCTION"
            }

    def register_new_vertical(
        self,
        vertical_code: str,
        vertical_name: str,
        description: str,
        required_roles: List[str],
        default_currency: str = "KES"
    ) -> Dict:
        code = vertical_code.strip().upper()
        if code in self.registered_verticals:
            return self.registered_verticals[code]

        vert = {
            "vertical_code": code,
            "vertical_name": vertical_name,
            "description": description,
            "required_roles": required_roles,
            "default_currency": default_currency,
            "status": "REGISTERED_DYNAMIC"
        }
        self.registered_verticals[code] = vert

        ev = EventPayload(
            event_type="VERTICAL_REGISTERED",
            event_category=EventCategory.GOVERNANCE,
            actor_identity_id="SYSTEM_VERTICAL_REGISTRY",
            organization_id="SYSTEM_CORE_ORG",
            correlation_id=code,
            source_module="VERTICAL_REGISTRY_ENGINE",
            payload=vert
        )
        event_bus.publish(ev)
        return vert

vertical_registry = VerticalRegistryEngine()
