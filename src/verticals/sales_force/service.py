import uuid
from typing import Dict, Optional
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine

class SalesForceAutomationEngine:
    """
    KARIS OS™ Sales Force Automation Engine (Section 22).
    Coordinates field representatives, route planning, visits, and referral conversion bonuses.
    """
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.visits: Dict[str, Dict] = {}
        self.referrals: Dict[str, Dict] = {}

    def register_sales_agent(
        self,
        identity_id: str,
        organization_id: str,
        agent_code: str,
        territory: str = "Machakos County - Mlolongo Ward"
    ) -> Dict:
        agent = {
            "agent_id": str(uuid.uuid4()),
            "identity_id": identity_id,
            "organization_id": organization_id,
            "agent_code": agent_code,
            "assigned_territory": territory,
            "status": "ACTIVE",
            "commission_rate_pct": 5.0,
            "total_referrals_converted": 0
        }
        self.agents[agent["agent_id"]] = agent
        return agent

    def log_sales_visit(
        self,
        agent_id: str,
        organization_id: str,
        customer_identity_id: str,
        visit_type: str = "FARMER_ONBOARDING",
        notes: str = "Onboarded avocado farmer successfully"
    ) -> Dict:
        if agent_id not in self.agents:
            raise KeyError(f"Sales Agent ID {agent_id} not found.")

        agent = self.agents[agent_id]
        visit_id = str(uuid.uuid4())
        visit = {
            "visit_id": visit_id,
            "agent_id": agent_id,
            "organization_id": organization_id,
            "customer_identity_id": customer_identity_id,
            "visit_type": visit_type,
            "notes": notes,
            "visit_status": "TASK_COMPLETED"
        }
        self.visits[visit_id] = visit

        ev = EventPayload(
            event_type="SALES_VISIT_COMPLETED",
            event_category=EventCategory.COMMERCE,
            actor_identity_id=agent["identity_id"],
            organization_id=organization_id,
            correlation_id=visit_id,
            source_module="SALES_FORCE_AUTOMATION_ENGINE",
            payload={
                "visit_id": visit_id,
                "agent_id": agent_id,
                "customer_identity_id": customer_identity_id,
                "visit_type": visit_type,
                "notes": notes
            }
        )
        event_bus.publish(ev)
        return visit

    def register_referral(
        self,
        agent_id: str,
        referred_identity_id: str,
        organization_id: str,
        referral_code: str
    ) -> Dict:
        if agent_id not in self.agents:
            raise KeyError(f"Sales Agent ID {agent_id} not found.")

        ref_id = str(uuid.uuid4())
        ref = {
            "referral_id": ref_id,
            "agent_id": agent_id,
            "referred_identity_id": referred_identity_id,
            "organization_id": organization_id,
            "referral_code": referral_code,
            "conversion_status": "PENDING",
            "krt_bonus_granted": 0.0
        }
        self.referrals[ref_code_key(referral_code)] = ref
        return ref

    def convert_referral(self, referral_code: str, first_order_kes: float) -> Dict:
        """Converts referral and awards 100 KRT field commission bonus to the agent's KRT wallet via Universal Ledger."""
        key = ref_code_key(referral_code)
        if key not in self.referrals:
            raise KeyError(f"Referral code {referral_code} not found.")

        ref = self.referrals[key]
        if ref["conversion_status"] == "CONVERTED_FIRST_PURCHASE":
            return {"status": "ALREADY_CONVERTED", "message": "Referral bonus already awarded."}

        ref["conversion_status"] = "CONVERTED_FIRST_PURCHASE"
        agent = self.agents.get(ref["agent_id"])
        if not agent:
            raise KeyError("Agent associated with referral not found.")

        agent["total_referrals_converted"] += 1
        krt_bonus = 100.0
        ref["krt_bonus_granted"] = krt_bonus

        # Execute double-entry transfer from Treasury Reward Pool -> Agent KRT Wallet (Rule 5)
        agent_krt = wallet_engine.get_wallet_by_keys(agent["identity_id"], ref["organization_id"], WalletType.KRT_WALLET, AssetType.KRT)
        if not agent_krt:
            agent_krt = wallet_engine.create_wallet(agent["identity_id"], ref["organization_id"], WalletType.KRT_WALLET, AssetType.KRT, 0.0)
        
        treasury_krt = wallet_engine.get_wallet_by_keys("TREASURY_IDENTITY", ref["organization_id"], WalletType.REWARD_POOL, AssetType.KRT)
        if not treasury_krt:
            treasury_krt = wallet_engine.create_wallet("TREASURY_IDENTITY", ref["organization_id"], WalletType.REWARD_POOL, AssetType.KRT, 1_000_000.0)

        tx_id = str(uuid.uuid4())
        ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=treasury_krt.wallet_id,
            credit_wallet_id=agent_krt.wallet_id,
            amount=krt_bonus,
            currency="KRT",
            organization_id=ref["organization_id"],
            trigger_event_id=tx_id,
            description=f"Sales Referral Conversion KRT Commission ({referral_code})"
        )

        ev = EventPayload(
            event_type="REFERRAL_CONFIRMED",
            event_category=EventCategory.COMMERCE,
            actor_identity_id=agent["identity_id"],
            organization_id=ref["organization_id"],
            correlation_id=tx_id,
            source_module="SALES_FORCE_AUTOMATION_ENGINE",
            payload={
                "referral_id": ref["referral_id"],
                "agent_id": ref["agent_id"],
                "referred_identity_id": ref["referred_identity_id"],
                "referral_code": referral_code,
                "krt_bonus_granted": krt_bonus
            }
        )
        event_bus.publish(ev)

        return {
            "status": "SUCCESS",
            "referral_code": referral_code,
            "agent_id": ref["agent_id"],
            "krt_bonus_granted": krt_bonus,
            "message": f"Referral {referral_code} converted! Awarded {krt_bonus} KRT field commission."
        }

def ref_code_key(code: str) -> str:
    return code.strip().upper()

sales_force_engine = SalesForceAutomationEngine()
