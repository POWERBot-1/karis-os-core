import uuid
from typing import Dict
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine

class FutureIndustriesSuiteEngine:
    """
    KARIS OS™ Future Industries Suite (Section 35.3).
    Enforces 'Build once. Configure many. Scale infinitely.'
    Provides concrete implementations across:
    1. Education Hub (`KARIS Edu-Pay` tuition fee installments & scholarship tokens).
    2. Tourism & Hospitality Hub (`KARIS Safari & Stays` eco-lodge bookings & carbon offsets).
    3. Real Estate & Construction Hub (`KARIS Prop-Share` fractional syndication units).
    """
    def __init__(self):
        self.tuition_plans: Dict[str, Dict] = {}
        self.safari_bookings: Dict[str, Dict] = {}
        self.syndications: Dict[str, Dict] = {}

    # --- 1. EDUCATION HUB (`KARIS Edu-Pay`) ---
    def register_tuition_plan(
        self,
        student_id: str,
        parent_id: str,
        institution_name: str = "Machakos Academy of Technology",
        term: str = "Term 3 2026",
        total_fee_kes: float = 45000.0,
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        plan_id = f"EDU-PLAN-{uuid.uuid4().hex[:6].upper()}"
        plan = {
            "plan_id": plan_id,
            "organization_id": organization_id,
            "student_identity_id": student_id,
            "parent_identity_id": parent_id,
            "institution_name": institution_name,
            "academic_term": term,
            "total_tuition_fee_kes": total_fee_kes,
            "amount_paid_kes": 0.0,
            "status": "ACTIVE_INSTALLMENT",
            "krt_edu_tokens_awarded": 0.0
        }
        self.tuition_plans[plan_id] = plan
        return plan

    def pay_tuition_installment(self, plan_id: str, amount_paid_kes: float) -> Dict:
        if plan_id not in self.tuition_plans:
            raise KeyError(f"Tuition Plan ID {plan_id} not found.")

        plan = self.tuition_plans[plan_id]
        plan["amount_paid_kes"] += amount_paid_kes
        if plan["amount_paid_kes"] >= plan["total_tuition_fee_kes"]:
            plan["status"] = "FULLY_PAID_SCHOLARSHIP"

        krt_scholarship = round(amount_paid_kes * 0.10, 2) # 10% KRT-EDU scholarship grant
        plan["krt_edu_tokens_awarded"] += krt_scholarship

        # Double-entry transfer of scholarship tokens
        stud_krt = wallet_engine.get_wallet_by_keys(plan["student_identity_id"], plan["organization_id"], WalletType.KRT_WALLET, AssetType.KRT)
        if not stud_krt:
            stud_krt = wallet_engine.create_wallet(plan["student_identity_id"], plan["organization_id"], WalletType.KRT_WALLET, AssetType.KRT, 0.0)
        treasury_krt = wallet_engine.get_wallet_by_keys("TREASURY_IDENTITY", plan["organization_id"], WalletType.REWARD_POOL, AssetType.KRT)
        if not treasury_krt:
            treasury_krt = wallet_engine.create_wallet("TREASURY_IDENTITY", plan["organization_id"], WalletType.REWARD_POOL, AssetType.KRT, 1_000_000.0)

        tx_id = str(uuid.uuid4())
        ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=treasury_krt.wallet_id,
            credit_wallet_id=stud_krt.wallet_id,
            amount=krt_scholarship,
            currency="KRT",
            organization_id=plan["organization_id"],
            trigger_event_id=tx_id,
            description=f"KARIS Edu-Pay Academic Scholarship Loyalty Tokens ({krt_scholarship} KRT)"
        )

        ev = EventPayload(
            event_type="EDUCATION_TUITION_INSTALLMENT_PAID",
            event_category=EventCategory.COMMERCE,
            actor_identity_id=plan["parent_identity_id"],
            organization_id=plan["organization_id"],
            correlation_id=tx_id,
            source_module="FUTURE_INDUSTRIES_EDUCATION_ENGINE",
            payload={
                "plan_id": plan_id,
                "student_identity_id": plan["student_identity_id"],
                "institution_name": plan["institution_name"],
                "amount_paid_kes": amount_paid_kes,
                "krt_edu_tokens_awarded": krt_scholarship,
                "status": plan["status"]
            }
        )
        event_bus.publish(ev)
        return {"status": "SUCCESS", "plan_id": plan_id, "amount_paid_kes": amount_paid_kes, "krt_scholarship_awarded": krt_scholarship}

    # --- 2. TOURISM & HOSPITALITY HUB (`KARIS Safari & Stays`) ---
    def book_safari_lodge(
        self,
        guest_id: str,
        lodge_name: str = "Machakos Luxury Eco-Safari Camp",
        nights: int = 3,
        price_per_night_kes: float = 12000.0,
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        total_price = round(nights * price_per_night_kes, 2)
        carbon_offset_krt = round(nights * 25.0, 2) # 25 KRT-GREEN per eco-night

        book_id = f"SAFARI-BK-{uuid.uuid4().hex[:6].upper()}"
        booking = {
            "booking_id": book_id,
            "booking_code": book_id,
            "guest_identity_id": guest_id,
            "lodge_or_hotel_name": lodge_name,
            "number_of_nights": nights,
            "total_booking_price_kes": total_price,
            "krt_green_carbon_offset_tokens": carbon_offset_krt,
            "booking_status": "CONFIRMED"
        }
        self.safari_bookings[book_id] = booking

        ev = EventPayload(
            event_type="HOSPITALITY_BOOKING_CONFIRMED",
            event_category=EventCategory.COMMERCE,
            actor_identity_id=guest_id,
            organization_id=organization_id,
            correlation_id=book_id,
            source_module="FUTURE_INDUSTRIES_HOSPITALITY_ENGINE",
            payload=booking
        )
        event_bus.publish(ev)
        return booking

    # --- 3. REAL ESTATE & CONSTRUCTION HUB (`KARIS Prop-Share`) ---
    def create_property_syndication(
        self,
        property_code: str = "PROP-MLOLONGO-TOWERS-01",
        property_name: str = "Mlolongo Trade Towers",
        total_valuation_kes: float = 100_000_000.0,
        total_units: float = 10000.0,
        yield_pct: float = 13.8,
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        syn_id = f"PROP-SYN-{uuid.uuid4().hex[:6].upper()}"
        syn = {
            "syndication_id": syn_id,
            "property_code": property_code,
            "organization_id": organization_id,
            "property_name": property_name,
            "total_valuation_kes": total_valuation_kes,
            "total_units": total_units,
            "price_per_unit_kes": round(total_valuation_kes / total_units, 2),
            "units_sold": 0.0,
            "expected_rental_yield_pct": yield_pct,
            "status": "OPEN_SYNDICATION"
        }
        self.syndications[syn_id] = syn
        return syn

    def allocate_fractional_units(self, syndication_id: str, investor_id: str, units_purchased: float) -> Dict:
        if syndication_id not in self.syndications:
            raise KeyError(f"Syndication ID {syndication_id} not found.")

        syn = self.syndications[syndication_id]
        total_cost = round(units_purchased * syn["price_per_unit_kes"], 2)
        syn["units_sold"] += units_purchased
        if syn["units_sold"] >= syn["total_units"]:
            syn["status"] = "FULLY_SUBSCRIBED"

        # Allocate INVESTMENT units via Universal Ledger (Rule 5)
        inv_w = wallet_engine.get_wallet_by_keys(investor_id, syn["organization_id"], WalletType.INVESTMENT_WALLET, AssetType.INVESTMENT)
        if not inv_w:
            inv_w = wallet_engine.create_wallet(investor_id, syn["organization_id"], WalletType.INVESTMENT_WALLET, AssetType.INVESTMENT, 0.0)
        treasury_inv = wallet_engine.get_wallet_by_keys("TREASURY_IDENTITY", syn["organization_id"], WalletType.RESERVE_WALLET, AssetType.INVESTMENT)
        if not treasury_inv:
            treasury_inv = wallet_engine.create_wallet("TREASURY_IDENTITY", syn["organization_id"], WalletType.RESERVE_WALLET, AssetType.INVESTMENT, 10_000_000.0)

        tx_id = str(uuid.uuid4())
        ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.INVESTMENT,
            debit_wallet_id=treasury_inv.wallet_id,
            credit_wallet_id=inv_w.wallet_id,
            amount=units_purchased,
            currency="INVESTMENT",
            organization_id=syn["organization_id"],
            trigger_event_id=tx_id,
            description=f"KARIS Prop-Share Fractional Syndication ({syn['property_code']}) - {units_purchased} Units"
        )

        ev = EventPayload(
            event_type="REAL_ESTATE_SYNDICATION_ALLOCATED",
            event_category=EventCategory.TREASURY,
            actor_identity_id=investor_id,
            organization_id=syn["organization_id"],
            correlation_id=tx_id,
            source_module="FUTURE_INDUSTRIES_REAL_ESTATE_ENGINE",
            payload={
                "syndication_id": syndication_id,
                "property_code": syn["property_code"],
                "investor_identity_id": investor_id,
                "units_purchased": units_purchased,
                "total_amount_kes": total_cost,
                "expected_rental_yield_pct": syn["expected_rental_yield_pct"]
            }
        )
        event_bus.publish(ev)
        return {"status": "SUCCESS", "syndication_id": syndication_id, "units_purchased": units_purchased, "total_cost_kes": total_cost}

future_industries_engine = FutureIndustriesSuiteEngine()
