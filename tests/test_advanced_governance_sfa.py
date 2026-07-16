import pytest
from src.core.ledger_engine import ledger_engine
from src.core.event_bus import event_bus
from src.verticals.sales_force.service import sales_force_engine
from src.verticals.loyalty.service import loyalty_engine
from src.core.workflow_engine import workflow_engine
from src.core.vertical_registry import vertical_registry
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType

def test_sales_force_automation_and_referral_commissions():
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    event_bus.event_store.clear()
    org = "ORG-KARIS-RETAIL"
    agent_id = "USER-AGENT-101"
    referred_id = "USER-REFERRED-202"

    agent = sales_force_engine.register_sales_agent(agent_id, org, "SFA-MACHAKOS-101")
    assert agent["agent_code"] == "SFA-MACHAKOS-101"

    visit = sales_force_engine.log_sales_visit(agent["agent_id"], org, referred_id, "FARMER_ONBOARDING")
    assert visit["visit_status"] == "TASK_COMPLETED"

    ref = sales_force_engine.register_referral(agent["agent_id"], referred_id, org, "REF-MACHAKOS-99")
    assert ref["conversion_status"] == "PENDING"

    # Ensure treasury reward pool exists
    wallet_engine.create_wallet("TREASURY_IDENTITY", org, WalletType.REWARD_POOL, AssetType.KRT, 500000.0)

    conv = sales_force_engine.convert_referral("REF-MACHAKOS-99", 5000.0)
    assert conv["status"] == "SUCCESS"
    assert conv["krt_bonus_granted"] == 100.0

    agent_krt = wallet_engine.get_wallet_by_keys(agent_id, org, WalletType.KRT_WALLET, AssetType.KRT)
    assert agent_krt.balance >= 100.0

def test_loyalty_promotional_campaign_grants():
    org = "ORG-KARIS-RETAIL"
    user_id = "USER-CUST-303"

    wallet_engine.create_wallet("TREASURY_IDENTITY", org, WalletType.REWARD_POOL, AssetType.KRT, 500000.0)
    camp = loyalty_engine.create_campaign(org, "CAMP-HARVEST-2X", "Harvest Double Points", "ALL", "KARIS_TOKENS_KRT", 2.0, 50.0)
    assert camp["campaign_code"] == "CAMP-HARVEST-2X"

    grant = loyalty_engine.grant_campaign_reward(camp["campaign_id"], user_id, org, "HARVEST_COMPLETED", 100.0)
    assert grant["status"] == "SUCCESS"
    assert grant["reward_awarded"] == 250.0  # 100 * 2.0 + 50.0 = 250.0

def test_declarative_workflow_state_machine():
    org = "ORG-KARIS-FARM"
    inst = workflow_engine.initiate_workflow("CREDIT_APPROVAL_WORKFLOW", "RESOURCE-APP-101", org, "USER-BORROWER-101")
    assert inst["current_state"] == "APPLICATION_SUBMITTED"

    inst = workflow_engine.advance_workflow_state(inst["instance_id"], "RISK_EVALUATION", "SYSTEM_AI")
    assert inst["current_state"] == "RISK_EVALUATION"

    inst = workflow_engine.advance_workflow_state(inst["instance_id"], "PENDING_HUMAN_REVIEW", "SYSTEM_AI")
    assert inst["current_state"] == "PENDING_HUMAN_REVIEW"

    inst = workflow_engine.advance_workflow_state(inst["instance_id"], "CREDIT_APPROVED", "ADMIN-USER-01", "Approved working capital facility")
    assert inst["current_state"] == "CREDIT_APPROVED"

def test_dynamic_vertical_registry_expansion():
    edu_vert = vertical_registry.register_new_vertical(
        "EDUCATION", "KARIS Education & Skills Hub", "School fee financing and student token incentives", ["STUDENT", "TEACHER", "SCHOOL_BURSAR"]
    )
    assert edu_vert["vertical_code"] == "EDUCATION"
    assert "EDUCATION" in vertical_registry.registered_verticals
