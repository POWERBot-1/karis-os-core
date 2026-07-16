import uuid
from typing import Dict
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.core.exchange_engine import exchange_engine

class OpenBankingCbdcEsgEngine:
    """
    KARIS OS™ 2.0 Innovation Engine (Section 48).
    Manages Central Bank Digital Currency (CBDC) wholesale/retail settlement,
    Open Banking PSD2 API consents, East African Community cross-border multi-currency transfers,
    and Scope 1/2/3 ESG Carbon Footprint tracking.
    """
    def __init__(self):
        self.cbdc_ledger: Dict[str, Dict] = {}
        self.open_banking_consents: Dict[str, Dict] = {}
        self.cross_border_transfers: Dict[str, Dict] = {}
        self.esg_records: Dict[str, Dict] = {}

    def execute_cbdc_settlement(
        self,
        sender_institution_id: str,
        recipient_institution_id: str,
        amount: float,
        cbdc_asset_code: str = "CBDC_KES",
        settlement_type: str = "WHOLESALE_INTERBANK",
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        """Executes instant CBDC settlement across participating financial institutions."""
        if amount <= 0:
            raise ValueError("CBDC settlement amount must be strictly positive.")

        cbdc_tx_id = f"CBDC-TX-{uuid.uuid4().hex[:8].upper()}"
        signature = f"SIG-CBK-SHA256-{uuid.uuid4().hex[:12].upper()}"

        record = {
            "cbdc_tx_id": cbdc_tx_id,
            "central_bank_identifier": "CBK-KENYA-CENTRAL-BANK",
            "sender_institution_id": sender_institution_id,
            "recipient_institution_id": recipient_institution_id,
            "cbdc_asset_code": cbdc_asset_code,
            "amount": amount,
            "settlement_type": settlement_type,
            "cryptographic_signature": signature
        }
        self.cbdc_ledger[cbdc_tx_id] = record

        ev = EventPayload(
            event_type="CBDC_SETTLEMENT_COMPLETED",
            event_category=EventCategory.TREASURY,
            actor_identity_id=sender_institution_id,
            organization_id=organization_id,
            correlation_id=cbdc_tx_id,
            source_module="CBDC_OPEN_BANKING_ENGINE",
            payload=record
        )
        event_bus.publish(ev)
        return record

    def grant_open_banking_consent(
        self,
        identity_id: str,
        bank_institution_id: str,
        bank_name: str,
        account_masked: str,
        consent_type: str = "ACCOUNT_INFORMATION_AIS",
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        """Registers Open Banking PSD2 consent connecting commercial bank accounts directly to KARIS OS."""
        consent_id = f"PSD2-CONSENT-{uuid.uuid4().hex[:6].upper()}"
        record = {
            "consent_id": consent_id,
            "identity_id": identity_id,
            "bank_institution_id": bank_institution_id,
            "bank_name": bank_name,
            "account_masked": account_masked,
            "consent_type": consent_type,
            "status": "ACTIVE"
        }
        self.open_banking_consents[consent_id] = record

        ev = EventPayload(
            event_type="OPEN_BANKING_CONSENT_GRANTED",
            event_category=EventCategory.IDENTITY,
            actor_identity_id=identity_id,
            organization_id=organization_id,
            correlation_id=consent_id,
            source_module="CBDC_OPEN_BANKING_ENGINE",
            payload=record
        )
        event_bus.publish(ev)
        return record

    def initiate_cross_border_eac_transfer(
        self,
        sender_identity_id: str,
        recipient_identity_id: str,
        source_country: str,
        destination_country: str,
        source_currency: str,
        destination_currency: str,
        source_amount: float,
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        """Initiates cross-border East African Community (EAC) regional settlement."""
        # Regional FX rates relative to KES
        fx_table = {
            "KES": 1.0,
            "UGX": 28.50, # 1 KES = 28.50 UGX
            "TZS": 19.80, # 1 KES = 19.80 TZS
            "RWF": 10.20  # 1 KES = 10.20 RWF
        }
        src_rate = fx_table.get(source_currency.upper(), 1.0)
        dst_rate = fx_table.get(destination_currency.upper(), 1.0)

        # Convert src -> base KES -> dst
        kes_equiv = source_amount / src_rate
        dest_amount = round(kes_equiv * dst_rate, 2)
        effective_rate = round(dst_rate / src_rate, 4)

        transfer_id = f"EAC-XFER-{uuid.uuid4().hex[:6].upper()}"
        record = {
            "transfer_id": transfer_id,
            "sender_identity_id": sender_identity_id,
            "recipient_identity_id": recipient_identity_id,
            "source_country": source_country,
            "destination_country": destination_country,
            "source_currency": source_currency,
            "destination_currency": destination_currency,
            "source_amount": source_amount,
            "destination_amount": dest_amount,
            "exchange_rate_used": effective_rate,
            "settlement_status": "COMPLETED"
        }
        self.cross_border_transfers[transfer_id] = record

        ev = EventPayload(
            event_type="CROSS_BORDER_TRANSFER_INITIATED",
            event_category=EventCategory.PAYMENT,
            actor_identity_id=sender_identity_id,
            organization_id=organization_id,
            correlation_id=transfer_id,
            source_module="CBDC_OPEN_BANKING_ENGINE",
            payload=record
        )
        event_bus.publish(ev)
        return record

    def record_esg_carbon_footprint(
        self,
        organization_id: str,
        target_resource_id: str,
        target_resource_type: str,
        scope_1_kg: float = 0.0,
        scope_2_kg: float = 0.0,
        scope_3_kg: float = 0.0
    ) -> Dict:
        """Section 48.2: Tracks Scope 1/2/3 carbon footprint and mints KRT-GREEN tokens for sustainability."""
        total_co2 = round(scope_1_kg + scope_2_kg + scope_3_kg, 4)
        
        if total_co2 <= 5.0:
            rating = "CARBON_NEGATIVE"
            krt_green = 50.0
        elif total_co2 <= 20.0:
            rating = "CARBON_NEUTRAL"
            krt_green = 25.0
        elif total_co2 <= 100.0:
            rating = "LOW_EMISSION"
            krt_green = 10.0
        else:
            rating = "HIGH_EMISSION"
            krt_green = 0.0

        record_id = f"ESG-CO2-{uuid.uuid4().hex[:6].upper()}"
        record = {
            "esg_record_id": record_id,
            "organization_id": organization_id,
            "target_resource_id": target_resource_id,
            "target_resource_type": target_resource_type,
            "scope_1_emissions_kg_co2": scope_1_kg,
            "scope_2_emissions_kg_co2": scope_2_kg,
            "scope_3_emissions_kg_co2": scope_3_kg,
            "total_carbon_footprint_kg_co2": total_co2,
            "sustainability_rating": rating,
            "krt_green_tokens_minted": krt_green
        }
        self.esg_records[record_id] = record

        # Award KRT-GREEN tokens into organization reward pool via Universal Ledger (Rule 5 & Rule 6)
        if krt_green > 0:
            org_krt = wallet_engine.get_wallet_by_keys("SYSTEM_ESG_HOLDER", organization_id, WalletType.KRT_WALLET, AssetType.KRT)
            if not org_krt:
                org_krt = wallet_engine.create_wallet("SYSTEM_ESG_HOLDER", organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)
            treasury_krt = wallet_engine.get_wallet_by_keys("TREASURY_IDENTITY", organization_id, WalletType.REWARD_POOL, AssetType.KRT)
            if not treasury_krt:
                treasury_krt = wallet_engine.create_wallet("TREASURY_IDENTITY", organization_id, WalletType.REWARD_POOL, AssetType.KRT, 1_000_000.0)

            tx_id = str(uuid.uuid4())
            ledger_engine.record_transaction(
                transaction_id=tx_id,
                asset_type=AssetType.KRT,
                debit_wallet_id=treasury_krt.wallet_id,
                credit_wallet_id=org_krt.wallet_id,
                amount=krt_green,
                currency="KRT",
                organization_id=organization_id,
                trigger_event_id=tx_id,
                description=f"ESG Carbon Credit KRT-GREEN Minting ({rating})"
            )

        ev = EventPayload(
            event_type="ESG_CARBON_CREDIT_MINTED",
            event_category=EventCategory.TREASURY,
            actor_identity_id="ESG_CARBON_ENGINE",
            organization_id=organization_id,
            correlation_id=record_id,
            source_module="ESG_CARBON_ENGINE",
            payload=record
        )
        event_bus.publish(ev)
        return record

innovation_2_0_engine = OpenBankingCbdcEsgEngine()
