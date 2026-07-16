import pytest
from src.core.ledger_engine import ledger_engine
from src.core.event_bus import event_bus
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType
from src.verticals.open_banking_cbdc.service import innovation_2_0_engine
from src.integrations.whatsapp_bot import whatsapp_bot_engine
from src.db.cqrs_projections import cqrs_projections_engine
from src.verticals.karis_farm.service import karis_farm_service

def test_cbdc_open_banking_and_cross_border_settlement():
    org = "ORG-KARIS-RETAIL"
    bank_a = "BANK-CBK-EQUITY-01"
    bank_b = "BANK-CBK-KCB-02"

    # 1. Wholesale CBDC Settlement
    cbdc_res = innovation_2_0_engine.execute_cbdc_settlement(bank_a, bank_b, 5000000.0, "CBDC_KES", "WHOLESALE_INTERBANK", org)
    assert cbdc_res["cbdc_asset_code"] == "CBDC_KES"
    assert cbdc_res["amount"] == 5000000.0

    # 2. Open Banking Consent
    consent = innovation_2_0_engine.grant_open_banking_consent("USER-101", bank_a, "Equity Bank Kenya", "XXXX-XXXX-8822")
    assert consent["status"] == "ACTIVE"

    # 3. Cross-Border EAC Transfer (KES -> UGX)
    eac_xfer = innovation_2_0_engine.initiate_cross_border_eac_transfer("USER-101", "USER-UG-202", "KE", "UG", "KES", "UGX", 10000.0, org)
    assert eac_xfer["destination_amount"] == 285000.0 # 10,000 * 28.50 UGX

def test_esg_carbon_footprint_and_green_token_minting():
    ledger_engine.entries.clear()
    ledger_engine.last_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    event_bus.event_store.clear()
    org = "ORG-KARIS-FARM"

    wallet_engine.create_wallet("TREASURY_IDENTITY", org, WalletType.REWARD_POOL, AssetType.KRT, 500000.0)

    # Record low-emission organic avocado batch
    esg_res = innovation_2_0_engine.record_esg_carbon_footprint(org, "BATCH-FARM-HAS-1BF01C", "PRODUCE_BATCH", 0.5, 0.3, 0.2)
    assert esg_res["sustainability_rating"] == "CARBON_NEGATIVE"
    assert esg_res["krt_green_tokens_minted"] == 50.0

    org_w = wallet_engine.get_wallet_by_keys("SYSTEM_ESG_HOLDER", org, WalletType.KRT_WALLET, AssetType.KRT)
    assert org_w.balance >= 50.0

def test_whatsapp_cloud_bot_interactive_intents():
    phone = "+254711223344"
    org = "ORG-KARIS-RETAIL"
    user_id = "USER-WA-101"

    wallet_engine.create_wallet(user_id, org, WalletType.KES_WALLET, AssetType.KES, 45000.0)
    wallet_engine.create_wallet(user_id, org, WalletType.KRT_WALLET, AssetType.KRT, 320.0)

    # Ensure farm & batch exist for QR check
    farm = karis_farm_service.register_farm("USER-WA-101", org, "WA Orchards", "Machakos County", 10.0)
    batch = karis_farm_service.log_harvest(farm["farm_id"], "HASS_AVOCADO", 500.0, "GRADE_A", 140.0)
    qr = batch.traceability_qr_code

    # Test Balance Intent
    msg_bal = whatsapp_bot_engine.process_inbound_message(phone, "2 Balance", user_id, org)
    assert msg_bal["detected_intent"] == "WALLET_BALANCE_CHECK"
    assert "KES 45,000.00" in msg_bal["bot_response_text"]
    assert "320.00 KRT" in msg_bal["bot_response_text"]

    # Test Traceability Intent
    msg_trace = whatsapp_bot_engine.process_inbound_message(phone, f"1 Trace {qr}", user_id, org)
    assert msg_trace["detected_intent"] == "PRODUCE_TRACEABILITY_LOOKUP"
    assert "KARIS FARM™ Traceability Report" in msg_trace["bot_response_text"]

    # Test Ask Agri AI Intent
    msg_agri = whatsapp_bot_engine.process_inbound_message(phone, "3 Ask Agri: Avocado soil pH requirements", user_id, org)
    assert msg_agri["detected_intent"] == "AI_RAG_CONVERSATIONAL_QUERY"
    assert "pH 5.5 to 6.5" in msg_agri["bot_response_text"] or "drip irrigation" in msg_agri["bot_response_text"]

def test_cqrs_read_model_projections():
    dash = cqrs_projections_engine.get_projections_dashboard()
    assert dash["cqrs_read_model_status"] == "ONLINE_ACTIVE_SYNC"
    assert dash["stream_buffer_size"] >= 0
