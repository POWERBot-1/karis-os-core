"""
KARIS OS™ :: Multi-Tenant Integration Test Suite for KARIS BorderX™ East African Customs & Trade Engine (`Section 58`).
Verifies 9 Multi-Currency Trade Wallets Onboarding (`KES, UGX, TZS, RWF, BIF, SSP, USD, EUR, KRT`),
AI HS Code Classification, Smart Duty Calculator with KRT Fee Discounts, Double-Entry Duty Settlement (`Rule 5 & Rule 9`),
AI Customs Risk Engine catching Under-Valuation under Rule 10 mandatory inspection, Smart Border Queue congestion forecasts,
Trade Finance facilities under strictly enforced Rule 3, and SHA-256 verified Digital Trade Certificates.
"""

import pytest
from datetime import datetime, timezone
from src.core.wallet_engine import wallet_engine
from src.core.ledger_engine import ledger_engine
from src.core.event_bus import event_bus
from src.verticals.borderx.service import borderx_service
from src.domain.models import WalletType, AssetType

@pytest.fixture(autouse=True)
def setup_borderx_environment():
    """
    Reset singleton state and initialize clean test wallets and system reserve pools.
    """
    wallet_engine.wallets.clear()
    wallet_engine.lookup_index.clear()
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0" * 64
    event_bus.event_store.clear()

    borderx_service.accounts.clear()
    borderx_service.declarations.clear()
    borderx_service.duty_payments.clear()
    borderx_service.shipments.clear()
    borderx_service.inspections.clear()
    borderx_service.trade_finance_facilities.clear()
    borderx_service.marketplace_listings.clear()
    borderx_service.warehouse_items.clear()
    borderx_service.digital_documents.clear()
    borderx_service.risk_logs.clear()
    borderx_service.regional_statistics.clear()

    borderx_service._init_system_pools()
    yield

def test_borderx_multi_currency_wallets_onboarding_and_ai_hs_classification():
    """
    Verifies 9 multi-currency trade wallets onboarding across East Africa and AI HS Code classification.
    """
    trader = borderx_service.onboard_borderx_account("TRADER-EAC-001", entity_type="IMPORTER", initial_kes=2500000.0, initial_usd=20000.0, initial_krt=15000.0)
    agent = borderx_service.onboard_borderx_account("AGENT-EAC-002", entity_type="CLEARING_AGENT")

    assert trader.entity_type == "IMPORTER"
    assert "CUSTOMS-ACCOUNT-REF-TRADER-EAC-001" in trader.customs_account_ref

    # Verify all 9 multi-currency trade wallets exist for the trader
    kes_w = wallet_engine.get_wallet(trader.kes_wallet_id)
    ugx_w = wallet_engine.get_wallet(trader.ugx_wallet_id)
    tzs_w = wallet_engine.get_wallet(trader.tzs_wallet_id)
    rwf_w = wallet_engine.get_wallet(trader.rwf_wallet_id)
    bif_w = wallet_engine.get_wallet(trader.bif_wallet_id)
    ssp_w = wallet_engine.get_wallet(trader.ssp_wallet_id)
    usd_w = wallet_engine.get_wallet(trader.usd_wallet_id)
    eur_w = wallet_engine.get_wallet(trader.eur_wallet_id)
    krt_w = wallet_engine.get_wallet(trader.krt_wallet_id)

    assert kes_w and kes_w.balance == 2500000.0
    assert ugx_w and ugx_w.balance > 0.0
    assert tzs_w and tzs_w.balance > 0.0
    assert usd_w and usd_w.balance == 20000.0
    assert krt_w and krt_w.balance == 15000.0

    # Classify product via AI
    hs_res = borderx_service.ai_engine.ai_hs_classifier("Huawei Carrier Solar Inverter Components", "ELECTRONICS")
    assert hs_res["hs_code"] == "8517.13.00"
    assert hs_res["suggested_duty_pct"] == 25.0
    assert "CAK Equipment Homologation Certificate" in hs_res["required_permits"]
    assert "Rule 10 Advisory" in hs_res["rule_10_advisory"]

def test_borderx_declaration_filing_smart_duty_calculator_and_double_entry_settlement():
    """
    Verifies customs declaration filing, smart duty calculator precision breakdown,
    KRT fee discount application (`Rule 5 & Rule 9`), and cryptographic audit verification.
    """
    trader = borderx_service.onboard_borderx_account("TRADER-EAC-003", initial_krt=1000000.0)
    agent = borderx_service.onboard_borderx_account("AGENT-EAC-004", entity_type="CLEARING_AGENT")

    # File customs declaration ($10,000 USD CIF value)
    decl = borderx_service.file_customs_declaration(
        trader_account_id=trader.account_id,
        agent_account_id=agent.account_id,
        declaration_type="IMPORTS",
        origin_code="CN",
        destination_code="KE",
        border_post_code="BUSIA_EAC",
        commodity_category="ELECTRONICS",
        commodity_description="Carrier Networking Grade Equipment",
        cif_value_usd=10000.0,
        market_benchmark_cif_usd=10000.0
    )
    assert decl.hs_code == "8517.13.00"
    assert decl.status == "DECLARATION_FILED"
    assert decl.customs_risk_score == 15.0

    trader_krt_w_before = wallet_engine.get_wallet(trader.krt_wallet_id).balance
    customs_pool_before = borderx_service.customs_revenue_pool.balance

    # Settle duty via KRT (`Rule 5 & Rule 9`)
    pmt = borderx_service.calculate_and_settle_duty(decl.declaration_id, pay_fees_in_krt=True)
    assert pmt.settlement_currency == "KRT"
    assert pmt.krt_fee_discount_pct == 25.0  # 25% discount on clearing and agent fees
    assert decl.status == "DUTY_PAID_CLEARED_FOR_ENTRY"

    trader_krt_w_after = wallet_engine.get_wallet(trader.krt_wallet_id).balance
    customs_pool_after = borderx_service.customs_revenue_pool.balance

    assert abs((trader_krt_w_before - trader_krt_w_after) - pmt.total_amount_krt) < 0.001
    assert abs((customs_pool_after - customs_pool_before) - pmt.total_amount_krt) < 0.001

    # Verify cryptographic audit chain (`Rule 9`)
    from src.security.audit import audit_engine
    ledger_audit = audit_engine.verify_ledger_chain()
    assert ledger_audit["status"] == "VERIFIED_CLEAN"

def test_borderx_ai_customs_risk_engine_rule_10_inspection_gate_and_smuggling_detection():
    """
    Verifies that the AI Customs Risk Engine detects under-valued CIF declarations (`< 60% of benchmark`),
    assigns high risk (`score >= 75`), hard-blocks duty settlement, and mandates Rule 10 human officer inspection.
    """
    trader = borderx_service.onboard_borderx_account("TRADER-EAC-005")
    agent = borderx_service.onboard_borderx_account("AGENT-EAC-006", entity_type="CLEARING_AGENT")

    # File declaration with under-valued CIF ($3,000 USD where market benchmark is $10,000 USD -> 30%)
    decl_risk = borderx_service.file_customs_declaration(
        trader_account_id=trader.account_id,
        agent_account_id=agent.account_id,
        declaration_type="IMPORTS",
        origin_code="CN",
        destination_code="KE",
        border_post_code="MOMBASA_PORT",
        commodity_category="ELECTRONICS",
        commodity_description="High-End Carrier Telecom Switches",
        cif_value_usd=3000.0,
        market_benchmark_cif_usd=10000.0
    )
    assert decl_risk.customs_risk_score == 85.0
    assert decl_risk.status == "UNDER_INSPECTION"

    # Check inspection scheduled
    insps = [i for i in borderx_service.inspections.values() if i.declaration_id == decl_risk.declaration_id]
    assert len(insps) == 1
    assert insps[0].inspection_status == "SCHEDULED_PENDING_INSPECTION"
    assert "Suspected under-valuation" in insps[0].reason

    # Attempt to settle duty while under inspection -> strictly blocked!
    with pytest.raises(PermissionError) as exc_info:
        borderx_service.calculate_and_settle_duty(decl_risk.declaration_id)
    assert "blocked under mandatory Rule 10 physical inspection" in str(exc_info.value)

def test_borderx_smart_border_queue_trade_finance_rule_3_and_digital_documentation():
    """
    Verifies Smart Border Queue congestion predictions (`Busia vs Malaba`), Trade Finance working capital facility
    under strictly enforced Rule 3 (`No Credit Approval -> No Credit Purchase`), and SHA-256 digital document generation.
    """
    borrower = borderx_service.onboard_borderx_account("BORROWER-EAC-007", initial_krt=1000.0)

    # 1. Smart Border Queue
    queue_busia = borderx_service.ai_engine.smart_border_queue("BUSIA_EAC")
    assert queue_busia["predicted_waiting_hours"] == 4.5
    assert queue_busia["congestion_status"] == "HEAVY_CONGESTION"
    assert queue_busia["ai_recommended_alternate_border"] == "MALABA_EAC"

    # 2. Trade Finance Facility (`Rule 3 & Rule 9`)
    borrower_krt_before = wallet_engine.get_wallet(borrower.krt_wallet_id).balance
    fac = borderx_service.apply_for_trade_finance(
        borrower_account_id=borrower.account_id,
        facility_type="WORKING_CAPITAL",
        requested_amount_usd=25000.0,
        cif_collateral_value_usd=50000.0
    )
    assert fac.credit_approval_status == "ACTIVE_DISBURSED"
    assert fac.principal_amount_usd == 25000.0
    assert fac.principal_amount_krt == 3250000.0  # 25,000 * 130

    borrower_krt_after = wallet_engine.get_wallet(borrower.krt_wallet_id).balance
    assert abs((borrower_krt_after - borrower_krt_before) - 3250000.0) < 0.001

    # 3. Digital Document Generation (`SHA-256`)
    decl = borderx_service.file_customs_declaration(borrower.account_id, borrower.account_id, "EXPORTS", "KE", "UG", "BUSIA_EAC", "AGRICULTURE", "Machakos Avocados", 5000.0, 5000.0)
    doc = borderx_service.generate_digital_document(decl.declaration_id, "CERTIFICATE_OF_ORIGIN")
    assert len(doc.sha256_verification_hash) == 64
    assert "BDX-SIG-" in doc.digital_signature

    # 4. AI Trade Assistant
    res_ai = borderx_service.ai_engine.ai_trade_assistant("How much duty for 500 bags of potatoes?")
    assert "0% Import Duty" in res_ai["ai_answer"]
    assert "Rule 10 Advisory" in res_ai["rule_10_advisory"]
