import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus

class DeclarativeTaxHolidayAndTariffEngine:
    """
    KARIS OS™ Declarative Multi-Tenant Tax Holiday & Dynamic Tariff Override Engine (Section 43 & 47).
    Allows statutory tax exemptions (`0% VAT during planting season for certified cooperative farmers`)
    to dynamically override standard KRA eTIMS invoice calculation without modifying source code (`Rule 7`).
    """
    def __init__(self):
        self.holidays: Dict[str, Dict] = {}
        self._seed_default_holidays()

    def _seed_default_holidays(self):
        self.create_tax_holiday(
            "ORG-KARIS-FARM", "HOLIDAY-KE-AGRI-EXEMPT-2026", "AGRICULTURAL_INPUTS_SEEDS_FERTILIZERS",
            "Kenyan Agricultural Input Planting Season Exemption", 0.0, "Statutory exemption under KRA Agri-Growth Act 2026"
        )

    def create_tax_holiday(
        self,
        organization_id: str,
        code: str,
        category: str,
        name: str,
        override_pct: float,
        rationale: str
    ) -> Dict:
        h_id = f"TAX-HOL-{uuid.uuid4().hex[:6].upper()}"
        now = datetime.now(timezone.utc)
        record = {
            "holiday_id": h_id,
            "holiday_code": code,
            "organization_id": organization_id,
            "product_category": category,
            "holiday_name": name,
            "override_tax_rate_pct": override_pct,
            "statutory_rationale": rationale,
            "start_date": now.isoformat(),
            "end_date": (now + timedelta(days=180)).isoformat(),
            "is_active": True
        }
        self.holidays[code] = record
        return record

    def evaluate_and_apply_tax_override(
        self,
        organization_id: str,
        product_category: str,
        base_amount_kes: float,
        standard_tax_pct: float = 16.0
    ) -> Dict:
        """Checks for active tax holiday. Returns exact override rate and tax amount (`Rule 7`)."""
        active_holiday = None
        for h in self.holidays.values():
            if h["organization_id"] == organization_id and h["product_category"] == product_category and h["is_active"]:
                active_holiday = h
                break

        if active_holiday:
            override_rate = float(active_holiday["override_tax_rate_pct"])
            tax_kes = round(base_amount_kes * (override_rate / 100.0), 2)
            
            ev = EventPayload(
                event_type="TAX_HOLIDAY_EXEMPTION_APPLIED",
                event_category=EventCategory.GOVERNANCE,
                actor_identity_id="SYSTEM_TAX_ENGINE",
                organization_id=organization_id,
                correlation_id=active_holiday["holiday_id"],
                source_module="TAX_OVERRIDE_ENGINE",
                payload={
                    "holiday_id": active_holiday["holiday_id"],
                    "holiday_code": active_holiday["holiday_code"],
                    "product_category": product_category,
                    "original_tax_pct": standard_tax_pct,
                    "override_tax_pct": override_rate,
                    "statutory_rationale": active_holiday["statutory_rationale"]
                }
            )
            event_bus.publish(ev)

            return {
                "status": "EXEMPTION_APPLIED",
                "applied_tax_rate_pct": override_rate,
                "tax_amount_kes": tax_kes,
                "holiday_code": active_holiday["holiday_code"],
                "rationale": active_holiday["statutory_rationale"]
            }
        else:
            tax_kes = round(base_amount_kes * (standard_tax_pct / 100.0), 2)
            return {
                "status": "STANDARD_TAX_APPLIED",
                "applied_tax_rate_pct": standard_tax_pct,
                "tax_amount_kes": tax_kes,
                "holiday_code": "NONE",
                "rationale": f"Standard {standard_tax_pct}% VAT applied."
            }

tax_override_engine = DeclarativeTaxHolidayAndTariffEngine()
