import pytest
from fastapi import HTTPException
from src.core.ledger_engine import ledger_engine
from src.core.event_bus import event_bus
from src.security.auth import auth_engine
from src.security.rbac import enforce_tenant_boundary, get_current_user
from src.security.audit import audit_engine
from src.ai.agents import multi_agent_suite
from src.verticals.financial_services.service import financial_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType

def test_security_auth_otp_and_jwt():
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    event_bus.event_store.clear()
    phone = "+254711999888"
    otp = auth_engine.generate_otp(phone)
    assert len(otp) == 6
    assert auth_engine.verify_otp(phone, otp) is True
    assert auth_engine.verify_otp(phone, otp) is False  # Cannot reuse OTP

    token = auth_engine.create_access_token("USER_ID_101", "ORG-KARIS-RETAIL", roles=["USER", "CUSTOMER"])
    payload = auth_engine.decode_access_token(token)
    assert payload is not None
    assert payload.identity_id == "USER_ID_101"
    assert payload.organization_id == "ORG-KARIS-RETAIL"

def test_rbac_multi_tenant_boundary_enforcement():
    user = auth_engine.decode_access_token(
        auth_engine.create_access_token("USER_ID_101", "ORG-KARIS-RETAIL", roles=["USER"])
    )
    # Accessing own tenant passes
    enforce_tenant_boundary(user, "ORG-KARIS-RETAIL")
    
    # Accessing another tenant throws 403 Forbidden (Multi-Tenant Security Violation)
    with pytest.raises(HTTPException) as exc_info:
        enforce_tenant_boundary(user, "ORG-KARIS-FARM")
    assert exc_info.value.status_code == 403
    assert "Multi-Tenant Security Violation" in exc_info.value.detail

def test_ai_rag_grounding_and_briefing():
    # Test Agriculture RAG
    agri_res = multi_agent_suite.ask_agriculture_agent("What soil pH and harvest protocols apply to Hass Avocados in Machakos?")
    assert "Agriculture AI" in agri_res["agent"]
    assert "pH 5.5 to 6.5" in agri_res["response"] or "drip irrigation" in agri_res["response"]
    assert len(agri_res["rag_citations"]) > 0

    # Test Support RAG & Urgency Classification
    supp_res = multi_agent_suite.ask_support_agent("Order delay emergency", "My M-Pesa payment QG37112233 confirmed but order is delayed!")
    assert supp_res["classified_urgency"] == "HIGH"
    assert "QG37XXXXXXXX" in supp_res["suggested_resolution"] or "Rule 2" in supp_res["suggested_resolution"]

    # Test Executive Briefing
    exec_res = multi_agent_suite.get_executive_briefing("ORG-KARIS-RETAIL")
    assert "EXECUTIVE BRIEFING" in exec_res["briefing_summary"]

def test_financial_mpesa_webhook_and_loan_repayment():
    org = "ORG-KARIS-RETAIL"
    payer = "USER_ID_101"

    # 1. Process M-Pesa C2B Callback
    mpesa_res = financial_engine.process_mpesa_c2b_callback(
        trans_id="QG37TEST999", amount_kes=4500.0, bill_ref_number="ORD-TEST-450", msisdn="254711999888",
        organization_id=org, payer_identity_id=payer
    )
    assert mpesa_res["status"] == "SUCCESS"
    assert mpesa_res["reconciled_amount_kes"] == 4500.0

    # 2. Process Loan Repayment & Check 8% KRT credit-building loyalty bonus
    borrower_w = wallet_engine.create_wallet(payer, org, WalletType.KES_WALLET, AssetType.KES, 30000.0)
    borrower_w.balance = 30000.0  # Ensure sufficient balance for loan repayment test
    wallet_engine.create_wallet("TREASURY_IDENTITY", org, WalletType.RESERVE_WALLET, AssetType.KES, 1000000.0)
    borrower_krt = wallet_engine.create_wallet(payer, org, WalletType.KRT_WALLET, AssetType.KRT, 100.0)
    borrower_krt.balance = 100.0
    treasury_krt = wallet_engine.create_wallet("TREASURY_IDENTITY", org, WalletType.REWARD_POOL, AssetType.KRT, 500000.0)
    treasury_krt.balance = 500000.0

    repay_res = financial_engine.process_loan_repayment(
        application_id="APP-LOAN-99", borrower_identity_id=payer, organization_id=org,
        amount_paid_kes=5000.0, mpesa_reference="QG37TEST888"
    )
    assert repay_res["status"] == "SUCCESS"
    assert repay_res["krt_bonus_awarded"] == round(5000.0 * 0.08, 2)  # 400 KRT awarded

def test_cryptographic_audit_verification():
    ledger_audit = audit_engine.verify_ledger_chain()
    assert ledger_audit["status"] == "VERIFIED_CLEAN"

    event_audit = audit_engine.verify_event_store_integrity()
    assert event_audit["status"] == "VERIFIED_CLEAN"
