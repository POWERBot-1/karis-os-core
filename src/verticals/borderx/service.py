"""
KARIS OS™ :: KARIS BorderX™ East African Customs & Border Trade Clearing Engine (`Section 58 / Vertical 23`).
Unifies 9 Multi-Currency Trade Wallets (`kes, ugx, tzs, rwf, bif, ssp, usd, eur, krt`),
AI HS Code Classification, Smart Duty Calculator (with KRT Fee Discounts up to 50%),
Cross-Border Settlement Engine (`Rule 5 & Rule 9`), Smart Border Queue Congestion Forecasts,
AI Customs Risk & Smuggling Engine (`Rule 10 officer verification`), Trade Finance (`Rule 3`), and Document AI.
Enforces all 10 Platform Rules (`Rule 1 to Rule 10`).
"""

import uuid
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from src.domain.models import (
    BorderXAccountModel, BorderXDeclarationModel, BorderXDutyPaymentModel,
    BorderXShipmentModel, BorderXInspectionModel, BorderXTradeFinanceModel,
    BorderXMarketplaceListingModel, BorderXWarehouseItemModel,
    BorderXDigitalDocumentModel, BorderXRiskLogModel, BorderXTradeStatisticModel,
    EventPayload, AssetType, WalletType, EventCategory
)
from src.core.event_bus import event_bus, UniversalEventBus
from src.core.ledger_engine import ledger_engine, UniversalLedgerEngine
from src.core.wallet_engine import wallet_engine, MultiAssetWalletEngine
from src.verticals.borderx.ai_customs_engine import BorderXAICustomsEngine
from src.verticals.borderx.smart_duty_calculator import BorderXSmartDutyCalculator
from src.verticals.borderx.trade_finance_engine import BorderXTradeFinanceEngine

class BorderXService:
    """
    East African Customs & Border Trade Clearing Engine (`Vertical 23`).
    """
    def __init__(
        self,
        event_bus: UniversalEventBus,
        ledger_engine: UniversalLedgerEngine,
        wallet_engine: MultiAssetWalletEngine
    ):
        self.event_bus = event_bus
        self.ledger_engine = ledger_engine
        self.wallet_engine = wallet_engine

        self.ai_engine = BorderXAICustomsEngine()
        self.duty_calculator = BorderXSmartDutyCalculator()
        self.finance_engine = BorderXTradeFinanceEngine()

        # In-memory domain repositories synced with database projections
        self.accounts: Dict[str, BorderXAccountModel] = {}
        self.declarations: Dict[str, BorderXDeclarationModel] = {}
        self.duty_payments: Dict[str, BorderXDutyPaymentModel] = {}
        self.shipments: Dict[str, BorderXShipmentModel] = {}
        self.inspections: Dict[str, BorderXInspectionModel] = {}
        self.trade_finance_facilities: Dict[str, BorderXTradeFinanceModel] = {}
        self.marketplace_listings: Dict[str, BorderXMarketplaceListingModel] = {}
        self.warehouse_items: Dict[str, BorderXWarehouseItemModel] = {}
        self.digital_documents: Dict[str, BorderXDigitalDocumentModel] = {}
        self.risk_logs: Dict[str, BorderXRiskLogModel] = {}
        self.regional_statistics: Dict[str, BorderXTradeStatisticModel] = {}

        self._init_system_pools()

    def _init_system_pools(self):
        """
        Auto-initializes system reserve pools for Customs Revenue, Trade Finance, and Escrow.
        """
        self.customs_revenue_pool = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-BORDERX-REVENUE",
            organization_id="ORG-BORDERX-MAIN",
            wallet_type=WalletType.TREASURY_WALLET,
            asset_type=AssetType.KRT,
            initial_balance=10000000.0
        )
        self.trade_finance_pool = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-BORDERX-FINANCE",
            organization_id="ORG-BORDERX-MAIN",
            wallet_type=WalletType.RESERVE_WALLET,
            asset_type=AssetType.KRT,
            initial_balance=50000000.0
        )
        self.customs_escrow_pool = self.wallet_engine.get_or_create_wallet(
            identity_id="POOL-BORDERX-ESCROW",
            organization_id="ORG-BORDERX-MAIN",
            wallet_type=WalletType.ESCROW_WALLET,
            asset_type=AssetType.KRT,
            initial_balance=5000000.0
        )

    # =========================================================================
    # 1. TRADE ACCOUNTS & 9 MULTI-CURRENCY WALLETS ONBOARDING (`Section 58.4`)
    # =========================================================================
    def onboard_borderx_account(
        self,
        identity_id: str,
        entity_type: str = "IMPORTER",
        initial_kes: float = 1300000.0,
        initial_usd: float = 10000.0,
        initial_krt: float = 10000.0
    ) -> BorderXAccountModel:
        """
        Onboards a regional trade entity across East Africa. Automatically issues 9 multi-currency wallets:
        `KES, UGX, TZS, RWF, BIF, SSP, USD, EUR, KRT` plus `CUSTOMS-ACCOUNT-REF`.
        Enforces Rule 1 & Rule 6.
        """
        account_number = f"BDX-{uuid.uuid4().hex[:8].upper()}"
        e_type = entity_type.upper()
        if e_type not in ["IMPORTER", "EXPORTER", "CLEARING_AGENT", "TRANSPORTER", "FREIGHT_COMPANY", "SHIPPING_LINE", "CUSTOMS_OFFICER"]:
            e_type = "IMPORTER"

        customs_ref = f"CUSTOMS-ACCOUNT-REF-{identity_id}"

        # Create 9 multi-currency wallets
        kes_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-bdx-kes", "ORG-BORDERX-MAIN", WalletType.KES_WALLET, AssetType.KES, initial_kes)
        ugx_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-bdx-ugx", "ORG-BORDERX-MAIN", WalletType.UGX_WALLET, AssetType.UGX, initial_usd * 3700.0)
        tzs_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-bdx-tzs", "ORG-BORDERX-MAIN", WalletType.TZS_WALLET, AssetType.TZS, initial_usd * 2600.0)
        rwf_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-bdx-rwf", "ORG-BORDERX-MAIN", WalletType.RWF_WALLET, AssetType.RWF, initial_usd * 1300.0)
        bif_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-bdx-bif", "ORG-BORDERX-MAIN", WalletType.BIF_WALLET, AssetType.BIF, initial_usd * 2800.0)
        ssp_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-bdx-ssp", "ORG-BORDERX-MAIN", WalletType.SSP_WALLET, AssetType.SSP, initial_usd * 1000.0)
        usd_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-bdx-usd", "ORG-BORDERX-MAIN", WalletType.USD_WALLET, AssetType.USD, initial_usd)
        eur_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-bdx-eur", "ORG-BORDERX-MAIN", WalletType.EUR_WALLET, AssetType.EUR, initial_usd * 0.92)
        krt_w = self.wallet_engine.get_or_create_wallet(f"{identity_id}-bdx-krt", "ORG-BORDERX-MAIN", WalletType.KRT_WALLET, AssetType.KRT, initial_krt)

        acc = BorderXAccountModel(
            identity_id=identity_id,
            account_number=account_number,
            entity_type=e_type,
            kyc_status="VERIFIED_TIER_3",
            kes_wallet_id=kes_w.wallet_id,
            ugx_wallet_id=ugx_w.wallet_id,
            tzs_wallet_id=tzs_w.wallet_id,
            rwf_wallet_id=rwf_w.wallet_id,
            bif_wallet_id=bif_w.wallet_id,
            ssp_wallet_id=ssp_w.wallet_id,
            usd_wallet_id=usd_w.wallet_id,
            eur_wallet_id=eur_w.wallet_id,
            krt_wallet_id=krt_w.wallet_id,
            customs_account_ref=customs_ref,
            reputation_score=100
        )
        self.accounts[acc.account_id] = acc

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="BORDERX_ACCOUNT_ONBOARDED",
            event_category=EventCategory.BORDERX_CUSTOMS,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=identity_id,
            source_module="borderx",
            organization_id="ORG-BORDERX-MAIN",
            payload={
                "account_id": acc.account_id,
                "identity_id": identity_id,
                "account_number": account_number,
                "entity_type": acc.entity_type,
                "kes_wallet_id": kes_w.wallet_id,
                "ugx_wallet_id": ugx_w.wallet_id,
                "tzs_wallet_id": tzs_w.wallet_id,
                "rwf_wallet_id": rwf_w.wallet_id,
                "bif_wallet_id": bif_w.wallet_id,
                "ssp_wallet_id": ssp_w.wallet_id,
                "usd_wallet_id": usd_w.wallet_id,
                "eur_wallet_id": eur_w.wallet_id,
                "krt_wallet_id": krt_w.wallet_id,
                "customs_account_ref": customs_ref
            }
        )
        self.event_bus.publish(evt)
        return acc

    # =========================================================================
    # 2. CUSTOMS DECLARATIONS, HS CODE AI & RISK ENGINE (`Section 58.2 & 58.8`)
    # =========================================================================
    def file_customs_declaration(
        self,
        trader_account_id: str,
        agent_account_id: str,
        declaration_type: str,
        origin_code: str,
        destination_code: str,
        border_post_code: str,
        commodity_category: str,
        commodity_description: str,
        cif_value_usd: float,
        market_benchmark_cif_usd: float = 0.0
    ) -> BorderXDeclarationModel:
        """
        Files a customs declaration across East African trade corridors.
        Auto-classifies HS Code via AI (`ai_hs_classifier`) and checks customs risk (`evaluate_customs_risk`).
        If Risk Score >= 75.0, schedules mandatory physical inspection under Rule 10.
        """
        if trader_account_id not in self.accounts or agent_account_id not in self.accounts:
            raise KeyError("Trader or Agent Account not found.")

        trader = self.accounts[trader_account_id]

        # 1. Classify product under HS Code using AI
        hs_res = self.ai_engine.ai_hs_classifier(commodity_description, commodity_category)
        hs_code = hs_res["hs_code"]

        # 2. Compute preliminary duty assessment in KES and KRT
        duty_res = self.duty_calculator.calculate_duty(
            cif_value_usd=cif_value_usd,
            duty_pct=hs_res["suggested_duty_pct"],
            vat_pct=hs_res["vat_pct"],
            railway_levy_pct=hs_res["railway_levy_pct"],
            idf_pct=hs_res["idf_pct"],
            rdl_pct=hs_res["rdl_pct"],
            pay_fees_in_krt=True
        )

        # 3. Evaluate AI Customs Risk Engine (`Rule 10`)
        benchmark = market_benchmark_cif_usd if market_benchmark_cif_usd > 0 else cif_value_usd
        risk_res = self.ai_engine.evaluate_customs_risk(
            trader_account_id, hs_code, cif_value_usd, benchmark, trader.reputation_score
        )

        status = "DECLARATION_FILED"
        if risk_res["is_blocked_for_inspection"]:
            status = "UNDER_INSPECTION"

        decl = BorderXDeclarationModel(
            trader_account_id=trader_account_id,
            agent_account_id=agent_account_id,
            declaration_type=declaration_type.upper(),
            origin_country_code=origin_code.upper(),
            destination_country_code=destination_code.upper(),
            border_post_code=border_post_code.upper(),
            hs_code=hs_code,
            commodity_description=commodity_description,
            cif_value_usd=cif_value_usd,
            cif_value_kes=duty_res["cif_value_kes"],
            total_duty_assessed_kes=duty_res["total_amount_kes"],
            total_duty_assessed_krt=duty_res["total_amount_krt"],
            customs_risk_score=risk_res["ai_risk_score"],
            status=status
        )
        self.declarations[decl.declaration_id] = decl

        # If high risk or under-valuation, log and schedule physical inspection under Rule 10
        if risk_res["is_blocked_for_inspection"]:
            risk_log = BorderXRiskLogModel(
                trader_account_id=trader_account_id,
                declaration_id=decl.declaration_id,
                fraud_type=risk_res["fraud_type"],
                detected_value_usd=cif_value_usd,
                ai_risk_score=risk_res["ai_risk_score"],
                status="FLAGGED_HIGH_RISK_BLOCKED",
                audit_notes=risk_res["audit_reasons"][0]
            )
            self.risk_logs[risk_log.log_id] = risk_log

            # Schedule physical inspection
            insp = BorderXInspectionModel(
                declaration_id=decl.declaration_id,
                customs_officer_account_id="OFFICER-KRA-EAC-01",
                border_post=border_post_code.upper(),
                reason=risk_res["audit_reasons"][0],
                ai_risk_flag_summary=f"HS Code: {hs_code} | CIF: ${cif_value_usd} vs Benchmark: ${benchmark} | Score: {risk_res['ai_risk_score']}",
                inspection_status="SCHEDULED_PENDING_INSPECTION"
            )
            self.inspections[insp.inspection_id] = insp

            evt_insp = EventPayload(
                event_id=str(uuid.uuid4()),
                event_type="BORDERX_INSPECTION_SCHEDULED",
                event_category=EventCategory.BORDERX_CUSTOMS,
                timestamp=datetime.now(timezone.utc),
                actor_identity_id=trader.identity_id,
                source_module="borderx",
                organization_id="ORG-BORDERX-MAIN",
                payload={
                    "inspection_id": insp.inspection_id,
                    "declaration_id": decl.declaration_id,
                    "customs_officer_account_id": insp.customs_officer_account_id,
                    "border_post": insp.border_post,
                    "reason": insp.reason,
                    "inspection_status": insp.inspection_status
                }
            )
            self.event_bus.publish(evt_insp)

        # Publish declaration filed event
        evt_decl = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="BORDERX_DECLARATION_FILED",
            event_category=EventCategory.BORDERX_CUSTOMS,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=trader.identity_id,
            source_module="borderx",
            organization_id="ORG-BORDERX-MAIN",
            payload={
                "declaration_id": decl.declaration_id,
                "trader_account_id": trader_account_id,
                "declaration_type": decl.declaration_type,
                "origin_country_code": decl.origin_country_code,
                "destination_country_code": decl.destination_country_code,
                "border_post_code": decl.border_post_code,
                "hs_code": decl.hs_code,
                "cif_value_usd": decl.cif_value_usd,
                "customs_risk_score": decl.customs_risk_score,
                "status": decl.status
            }
        )
        self.event_bus.publish(evt_decl)
        return decl

    # =========================================================================
    # 3. SMART DUTY SETTLEMENT & KRT CLEARING FEE DISCOUNT (`Section 58.3 & 58.5`)
    # =========================================================================
    def calculate_and_settle_duty(
        self,
        declaration_id: str,
        pay_fees_in_krt: bool = True
    ) -> BorderXDutyPaymentModel:
        """
        Calculates exact duty breakdown and settles payment via double-entry ledger (`Rule 5 & Rule 9`).
        Applies KRT clearing fee discounts (`up to 50% discount when paying fees in KRT`).
        """
        if declaration_id not in self.declarations:
            raise KeyError(f"Declaration '{declaration_id}' not found.")
        decl = self.declarations[declaration_id]
        if decl.status == "UNDER_INSPECTION":
            raise PermissionError("Customs Declaration is blocked under mandatory Rule 10 physical inspection. Cannot settle duty until cleared by a customs officer.")

        trader = self.accounts[decl.trader_account_id]

        # Re-verify calculation breakdown
        hs_spec = self.ai_engine.hs_catalog.get(decl.hs_code, {"duty_pct": 25.0, "vat_pct": 16.0, "railway_levy_pct": 1.5, "idf_pct": 2.5, "rdl_pct": 1.5})
        duty_res = self.duty_calculator.calculate_duty(
            cif_value_usd=decl.cif_value_usd,
            duty_pct=hs_spec["duty_pct"],
            vat_pct=hs_spec["vat_pct"],
            railway_levy_pct=hs_spec["railway_levy_pct"],
            idf_pct=hs_spec["idf_pct"],
            rdl_pct=hs_spec["rdl_pct"],
            pay_fees_in_krt=pay_fees_in_krt
        )

        amount_to_settle = duty_res["total_amount_krt"] if pay_fees_in_krt else duty_res["total_amount_kes"]
        asset_type = AssetType.KRT if pay_fees_in_krt else AssetType.KES
        source_wallet_id = trader.krt_wallet_id if pay_fees_in_krt else trader.kes_wallet_id

        source_w = self.wallet_engine.get_wallet(source_wallet_id)
        if not source_w or source_w.balance < amount_to_settle:
            raise ValueError(f"Insufficient {'KRT' if pay_fees_in_krt else 'KES'} balance for duty settlement. Balance: {source_w.balance if source_w else 0.0}, Required: {amount_to_settle}.")

        tx_id = str(uuid.uuid4())
        ledger_entry = self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=asset_type,
            debit_wallet_id=source_wallet_id,
            credit_wallet_id=self.customs_revenue_pool.wallet_id,
            amount=amount_to_settle,
            currency="KRT" if pay_fees_in_krt else "KES",
            organization_id="ORG-BORDERX-MAIN",
            trigger_event_id=f"BDX-DUTY-SETTLE-{tx_id}",
            description=f"KARIS BorderX Duty & Fee Settlement ({decl.declaration_id}): {amount_to_settle} {'KRT' if pay_fees_in_krt else 'KES'} with {duty_res['krt_fee_discount_pct']}% Fee Discount"
        )

        decl.status = "DUTY_PAID_CLEARED_FOR_ENTRY"
        trader.reputation_score += 20

        pmt = BorderXDutyPaymentModel(
            payment_id=tx_id,
            declaration_id=declaration_id,
            trader_account_id=decl.trader_account_id,
            import_duty_kes=duty_res["import_duty_kes"],
            export_duty_kes=duty_res["export_duty_kes"],
            vat_kes=duty_res["vat_kes"],
            excise_kes=duty_res["excise_kes"],
            railway_levy_kes=duty_res["railway_levy_kes"],
            idf_kes=duty_res["idf_kes"],
            rdl_kes=duty_res["rdl_kes"],
            port_charges_kes=duty_res["port_charges_kes"],
            clearing_fees_kes=duty_res["clearing_fees_kes"],
            agent_fees_kes=duty_res["agent_fees_kes"],
            inspection_fees_kes=duty_res["inspection_fees_kes"],
            total_amount_kes=duty_res["total_amount_kes"],
            total_amount_krt=duty_res["total_amount_krt"],
            krt_fee_discount_pct=duty_res["krt_fee_discount_pct"],
            settlement_currency="KRT" if pay_fees_in_krt else "KES",
            ledger_entry_id=ledger_entry.entry_id
        )
        self.duty_payments[pmt.payment_id] = pmt

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="BORDERX_DUTY_PAID_AND_SETTLED",
            event_category=EventCategory.BORDERX_CUSTOMS,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=trader.identity_id,
            source_module="borderx",
            organization_id="ORG-BORDERX-MAIN",
            payload={
                "payment_id": pmt.payment_id,
                "declaration_id": declaration_id,
                "trader_account_id": pmt.trader_account_id,
                "total_amount_kes": pmt.total_amount_kes,
                "total_amount_krt": pmt.total_amount_krt,
                "krt_fee_discount_pct": pmt.krt_fee_discount_pct,
                "settlement_currency": pmt.settlement_currency,
                "ledger_entry_id": pmt.ledger_entry_id
            }
        )
        self.event_bus.publish(evt)
        return pmt

    # =========================================================================
    # 4. TRADE FINANCE FACILITIES (`Section 58.10 & Rule 3`)
    # =========================================================================
    def apply_for_trade_finance(
        self,
        borrower_account_id: str,
        facility_type: str,
        requested_amount_usd: float,
        cif_collateral_value_usd: float = 0.0
    ) -> BorderXTradeFinanceModel:
        """
        Structures working capital, invoice financing, or letters of credit.
        Enforces strictly: Rule 3 (No Credit Approval -> No Credit Purchase) & Rule 9 double-entry accounting.
        """
        if borrower_account_id not in self.accounts:
            raise KeyError(f"Borrower Account '{borrower_account_id}' not found.")
        borrower = self.accounts[borrower_account_id]

        is_approved, status_reason, approved_usd = self.finance_engine.evaluate_credit_application(
            borrower_account_id, facility_type, requested_amount_usd, borrower.reputation_score, cif_collateral_value_usd
        )

        if not is_approved or approved_usd <= 0.0:
            rejected = BorderXTradeFinanceModel(
                borrower_account_id=borrower_account_id,
                facility_type=facility_type.upper(),
                principal_amount_usd=requested_amount_usd,
                principal_amount_krt=requested_amount_usd * 130.0,
                credit_approval_status=status_reason
            )
            self.trade_finance_facilities[rejected.facility_id] = rejected
            return rejected

        approved_krt = round(approved_usd * 130.0, 4)

        # Disburse funds from Trade Finance Pool to Borrower KRT Wallet via double entry (`Rule 3 & Rule 9`)
        tx_id = str(uuid.uuid4())
        ledger_entry = self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=self.trade_finance_pool.wallet_id,
            credit_wallet_id=borrower.krt_wallet_id,
            amount=approved_krt,
            currency="KRT",
            organization_id="ORG-BORDERX-MAIN",
            trigger_event_id=f"BDX-LOAN-DISBURSE-{tx_id}",
            description=f"KARIS BorderX Trade Finance Disbursement ({facility_type.upper()}): {approved_krt} KRT under Rule 3"
        )

        fac = BorderXTradeFinanceModel(
            facility_id=tx_id,
            borrower_account_id=borrower_account_id,
            facility_type=facility_type.upper(),
            principal_amount_usd=approved_usd,
            principal_amount_krt=approved_krt,
            interest_rate_pct=8.5,
            tenor_days=90,
            credit_approval_status="ACTIVE_DISBURSED",
            disbursement_ledger_id=ledger_entry.entry_id
        )
        self.trade_finance_facilities[fac.facility_id] = fac

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="BORDERX_TRADE_FINANCE_DISBURSED",
            event_category=EventCategory.BORDERX_FINANCE,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=borrower.identity_id,
            source_module="borderx",
            organization_id="ORG-BORDERX-MAIN",
            payload={
                "facility_id": fac.facility_id,
                "borrower_account_id": borrower_account_id,
                "facility_type": fac.facility_type,
                "principal_amount_usd": fac.principal_amount_usd,
                "principal_amount_krt": fac.principal_amount_krt,
                "credit_approval_status": fac.credit_approval_status,
                "disbursement_ledger_id": fac.disbursement_ledger_id
            }
        )
        self.event_bus.publish(evt)
        return fac

    # =========================================================================
    # 5. SMART BORDER QUEUE & SHIPMENT TRACKING (`Section 58.7`)
    # =========================================================================
    def dispatch_shipment_to_border(
        self,
        declaration_id: str,
        transporter_account_id: str,
        transport_mode: str,
        container_number: str,
        seal_number: str,
        target_border_post: str = "BUSIA_EAC"
    ) -> BorderXShipmentModel:
        """
        Registers shipment tracking and queries AI Smart Border Queue to predict waiting time and alternate routes.
        """
        if declaration_id not in self.declarations or transporter_account_id not in self.accounts:
            raise KeyError("Declaration or Transporter Account not found.")

        # Query Smart Border Queue
        queue_res = self.ai_engine.smart_border_queue(target_border_post)

        shipment = BorderXShipmentModel(
            declaration_id=declaration_id,
            transporter_account_id=transporter_account_id,
            transport_mode=transport_mode.upper(),
            container_number=container_number.upper(),
            seal_number=seal_number.upper(),
            seal_verification_status="SEAL_INTACT_VERIFIED",
            current_border_post=queue_res["border_post"],
            ai_predicted_waiting_hours=queue_res["predicted_waiting_hours"],
            congestion_status=queue_res["congestion_status"],
            ai_recommended_alternate_border=queue_res["ai_recommended_alternate_border"],
            status="IN_TRANSIT_TO_BORDER"
        )
        self.shipments[shipment.shipment_id] = shipment
        return shipment

    # =========================================================================
    # 6. DIGITAL TRADE DOCUMENTATION GENERATION (`Section 58.12`)
    # =========================================================================
    def generate_digital_document(
        self,
        declaration_id: str,
        document_type: str
    ) -> BorderXDigitalDocumentModel:
        """
        Auto-generates an immutable digital trade document with exact SHA-256 verification hash.
        """
        if declaration_id not in self.declarations:
            raise KeyError(f"Declaration '{declaration_id}' not found.")
        decl = self.declarations[declaration_id]
        trader = self.accounts[decl.trader_account_id]

        payload = {
            "declaration_id": declaration_id,
            "document_type": document_type.upper(),
            "trader_account_number": trader.account_number,
            "hs_code": decl.hs_code,
            "commodity": decl.commodity_description,
            "cif_usd": decl.cif_value_usd,
            "status": decl.status,
            "issued_at": datetime.now(timezone.utc).isoformat()
        }
        payload_str = json.dumps(payload, sort_keys=True)
        sha256_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        digital_sig = f"BDX-SIG-{sha256_hash[:16].upper()}"

        doc = BorderXDigitalDocumentModel(
            declaration_id=declaration_id,
            document_type=document_type.upper(),
            document_title=f"East African {document_type.replace('_', ' ').title()} Certificate",
            payload_json=payload_str,
            sha256_verification_hash=sha256_hash,
            digital_signature=digital_sig
        )
        self.digital_documents[doc.document_id] = doc

        evt = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="BORDERX_DOCUMENT_GENERATED",
            event_category=EventCategory.BORDERX_CUSTOMS,
            timestamp=datetime.now(timezone.utc),
            actor_identity_id=trader.identity_id,
            source_module="borderx",
            organization_id="ORG-BORDERX-MAIN",
            payload={
                "document_id": doc.document_id,
                "declaration_id": declaration_id,
                "document_type": doc.document_type,
                "document_title": doc.document_title,
                "sha256_verification_hash": sha256_hash,
                "digital_signature": digital_sig
            }
        )
        self.event_bus.publish(evt)
        return doc

# Export global singleton
borderx_service = BorderXService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
