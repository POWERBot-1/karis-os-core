import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from src.domain.models import (
    PharmaColdChainBatchModel, PharmaTemperatureTelemetryModel,
    PropShareSyndicationModel, PropShareAllocationModel,
    EduPayTuitionPlanModel, EduPayTuitionInstallmentModel,
    EventPayload, AssetType, WalletType
)
from src.core.event_bus import event_bus, UniversalEventBus
from src.core.ledger_engine import ledger_engine, UniversalLedgerEngine
from src.core.wallet_engine import wallet_engine, MultiAssetWalletEngine

class KarisExpansionSuiteService:
    """
    KARIS OS™ :: KARIS INNOVATION EXPANSION SUITE (`Section 52 - Verticals 16, 17, 18`).
    
    Provides:
    1. Pharma-Trace: Cold-chain batch registration and IoT temperature telemetry (`< 8°C`). Auto-locks breached batches (`Rule 1 & 6`).
    2. Prop-Share: Commercial real estate syndication and automated double-entry rental dividend distributions (`Rule 5 & Rule 9`).
    3. Edu-Pay: Student academic term tuition installment plans and double-entry payments awarding `+150 KRT-EDU` campus cafeteria tokens (`Rule 7 & 9`).
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
        
        self.pharma_batches: Dict[str, PharmaColdChainBatchModel] = {}
        self.pharma_telemetry: Dict[str, PharmaTemperatureTelemetryModel] = {}
        self.syndications: Dict[str, PropShareSyndicationModel] = {}
        self.allocations: Dict[str, PropShareAllocationModel] = {}
        self.tuition_plans: Dict[str, EduPayTuitionPlanModel] = {}
        self.tuition_installments: Dict[str, EduPayTuitionInstallmentModel] = {}

    # --- 1. KARIS HEALTH PHARMA-TRACE™ (`Vertical 16`) ---
    def log_pharma_batch(self, product_id: str, organization_id: str, storage_min: float = 2.0, storage_max: float = 8.0) -> PharmaColdChainBatchModel:
        batch = PharmaColdChainBatchModel(
            product_id=product_id,
            organization_id=organization_id,
            batch_number=f"BATCH-PHARMA-{uuid.uuid4().hex[:6].upper()}",
            qr_traceability_code=f"KARIS-PHARMA-QR-{uuid.uuid4().hex[:8].upper()}",
            storage_min_celsius=storage_min,
            storage_max_celsius=storage_max
        )
        self.pharma_batches[batch.batch_id] = batch

        ev = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="EXPSUITE_PHARMA_BATCH_LOGGED",
            event_category="PHARMA",
            actor_identity_id="SYSTEM-PHARMA-DISPENSARY",
            organization_id=organization_id,
            correlation_id=str(uuid.uuid4()),
            source_module="KARIS_PHARMA_TRACE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "batch_id": batch.batch_id,
                "product_id": product_id,
                "batch_number": batch.batch_number,
                "qr_traceability_code": batch.qr_traceability_code,
                "storage_min_celsius": storage_min,
                "storage_max_celsius": storage_max
            }
        )
        self.event_bus.publish(ev)
        return batch

    def log_pharma_temperature_telemetry(self, batch_id: str, temperature_c: float, humidity: float = 55.0, gps: str = "(-1.3850, 36.9400)") -> Dict[str, Any]:
        if batch_id not in self.pharma_batches:
            raise KeyError(f"Pharma Batch {batch_id} not registered.")
        batch = self.pharma_batches[batch_id]
        batch.current_temperature_celsius = temperature_c

        tel = PharmaTemperatureTelemetryModel(batch_id=batch_id, temperature_celsius=temperature_c, humidity_pct=humidity, gps_location=gps)
        self.pharma_telemetry[tel.telemetry_id] = tel

        is_breached = temperature_c > batch.storage_max_celsius or temperature_c < batch.storage_min_celsius
        if is_breached:
            batch.status = "COLD_CHAIN_BREACHED_LOCKED"
            ev = EventPayload(
                event_id=str(uuid.uuid4()),
                event_type="EXPSUITE_PHARMA_COLD_CHAIN_BREACHED",
                event_category="PHARMA",
                actor_identity_id="IOT-SENSOR-COLD-01",
                organization_id=batch.organization_id,
                correlation_id=tel.telemetry_id,
                source_module="KARIS_PHARMA_TRACE",
                timestamp=datetime.now(timezone.utc),
                payload={"telemetry_id": tel.telemetry_id, "batch_id": batch_id, "temperature_celsius": temperature_c, "storage_max_celsius": batch.storage_max_celsius, "gps_location": gps}
            )
            self.event_bus.publish(ev)
        else:
            batch.status = "SAFE_COLD_CHAIN"

        return {"telemetry_id": tel.telemetry_id, "batch_id": batch_id, "temperature_celsius": temperature_c, "status": batch.status, "cold_chain_breached": is_breached}

    # --- 2. KARIS PROP-SHARE & FRAC-EQUITY™ (`Vertical 17`) ---
    def create_syndication(self, organization_id: str, title: str, location: str, total_shares: int, share_price_kes: float) -> PropShareSyndicationModel:
        synd = PropShareSyndicationModel(organization_id=organization_id, property_title=title, location_county=location, total_shares=total_shares, share_price_kes=share_price_kes)
        self.syndications[synd.syndication_id] = synd
        return synd

    def allocate_shares(self, syndication_id: str, investor_id: str, shares: int) -> PropShareAllocationModel:
        if syndication_id not in self.syndications:
            raise KeyError(f"Syndication {syndication_id} not found.")
        synd = self.syndications[syndication_id]
        total_inv = round(shares * synd.share_price_kes, 4)

        alloc = PropShareAllocationModel(syndication_id=syndication_id, investor_identity_id=investor_id, shares_owned=shares, total_invested_kes=total_inv)
        self.allocations[alloc.allocation_id] = alloc

        ev = EventPayload(
            event_id=str(uuid.uuid4()), event_type="EXPSUITE_PROP_SHARE_ALLOCATED", event_category="PROP_SHARE",
            actor_identity_id=investor_id, organization_id=synd.organization_id, correlation_id=alloc.allocation_id, source_module="KARIS_PROP_SHARE",
            timestamp=datetime.now(timezone.utc), payload={"allocation_id": alloc.allocation_id, "syndication_id": syndication_id, "investor_identity_id": investor_id, "shares_owned": shares, "total_invested_kes": total_inv}
        )
        self.event_bus.publish(ev)
        return alloc

    def distribute_monthly_rental_dividends(self, syndication_id: str, total_rental_pool_krt: float) -> Dict[str, Any]:
        """Distributes monthly rental income dividends in KRT via double-entry ledger (`Rule 5 & Rule 9`)."""
        if syndication_id not in self.syndications:
            raise KeyError(f"Syndication {syndication_id} not found.")
        synd = self.syndications[syndication_id]
        if total_rental_pool_krt <= 0:
            raise ValueError("Rental pool must be greater than 0.")

        treasury_wallet = self.wallet_engine.get_or_create_wallet("ORG-TREASURY-MAIN", synd.organization_id, WalletType.RESERVE_WALLET, AssetType.KRT, 1000000.0)
        payouts = []

        for alloc in self.allocations.values():
            if alloc.syndication_id == syndication_id and alloc.shares_owned > 0:
                share_ratio = alloc.shares_owned / synd.total_shares
                div_amount = round(total_rental_pool_krt * share_ratio, 4)
                if div_amount > 0:
                    alloc.total_dividends_earned_kes = round(alloc.total_dividends_earned_kes + div_amount, 4)
                    inv_wallet = self.wallet_engine.get_or_create_wallet(alloc.investor_identity_id, synd.organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)
                    tx_id = str(uuid.uuid4())
                    self.ledger_engine.record_transaction(
                        transaction_id=tx_id, asset_type=AssetType.KRT, debit_wallet_id=treasury_wallet.wallet_id, credit_wallet_id=inv_wallet.wallet_id,
                        amount=div_amount, currency="KRT", organization_id=synd.organization_id, trigger_event_id=f"PROP-DIV-{syndication_id[:8]}",
                        description=f"Monthly rental dividend ({div_amount} KRT) for {synd.property_title}"
                    )
                    self.event_bus.publish(EventPayload(
                        event_id=str(uuid.uuid4()), event_type="EXPSUITE_PROP_SHARE_DIVIDEND_DISTRIBUTED", event_category="PROP_SHARE",
                        actor_identity_id="SYSTEM-PROP-SHARE", organization_id=synd.organization_id, correlation_id=tx_id, source_module="KARIS_PROP_SHARE",
                        timestamp=datetime.now(timezone.utc), payload={"syndication_id": syndication_id, "investor_identity_id": alloc.investor_identity_id, "dividend_amount_krt": div_amount, "reference_transaction_id": tx_id}
                    ))
                    payouts.append({"investor_id": alloc.investor_identity_id, "shares": alloc.shares_owned, "dividend_krt": div_amount})

        return {"syndication_id": syndication_id, "property_title": synd.property_title, "total_rental_pool_krt": total_rental_pool_krt, "investor_payouts_count": len(payouts), "payouts": payouts, "audit_hash": self.ledger_engine.last_hash}

    # --- 3. KARIS EDU-PAY & CAMPUS GRID™ (`Vertical 18`) ---
    def create_tuition_plan(self, student_id: str, institution_org_id: str, term: str, total_tuition_kes: float) -> EduPayTuitionPlanModel:
        plan = EduPayTuitionPlanModel(student_identity_id=student_id, institution_organization_id=institution_org_id, academic_term=term, total_tuition_kes=total_tuition_kes, remaining_balance_kes=total_tuition_kes)
        self.tuition_plans[plan.plan_id] = plan
        return plan

    def pay_tuition_installment(self, plan_id: str, payer_id: str, amount_kes: float, external_ref: str = "PALPLUS-EDU-01") -> Dict[str, Any]:
        """Reconciles tuition installment, debits payer KES, credits college KES (`Rule 9`), and awards +150 KRT-EDU (`Rule 7`)."""
        if plan_id not in self.tuition_plans:
            raise KeyError(f"Tuition Plan {plan_id} not found.")
        plan = self.tuition_plans[plan_id]
        if amount_kes <= 0:
            raise ValueError("Tuition installment must be greater than 0.")

        plan.paid_amount_kes = round(plan.paid_amount_kes + amount_kes, 4)
        plan.remaining_balance_kes = round(max(0.0, plan.total_tuition_kes - plan.paid_amount_kes), 4)

        payer_kes = self.wallet_engine.get_or_create_wallet(payer_id, plan.institution_organization_id, WalletType.KES_WALLET, AssetType.KES, amount_kes)
        college_kes = self.wallet_engine.get_or_create_wallet(plan.institution_organization_id, plan.institution_organization_id, WalletType.KES_WALLET, AssetType.KES, 0.0)

        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id, asset_type=AssetType.KES, debit_wallet_id=payer_kes.wallet_id, credit_wallet_id=college_kes.wallet_id,
            amount=amount_kes, currency="KES", organization_id=plan.institution_organization_id, trigger_event_id=external_ref,
            description=f"Edu-Pay Tuition Installment ({amount_kes} KES) for student {plan.student_identity_id}"
        )

        # Award +150 KRT-EDU campus cafeteria bonus (`Rule 7 & Rule 9`)
        bonus_krt = 150.0
        treasury_w = self.wallet_engine.get_or_create_wallet("ORG-TREASURY-MAIN", plan.institution_organization_id, WalletType.RESERVE_WALLET, AssetType.KRT, 1000000.0)
        student_krt = self.wallet_engine.get_or_create_wallet(plan.student_identity_id, plan.institution_organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)
        self.ledger_engine.record_transaction(
            transaction_id=str(uuid.uuid4()), asset_type=AssetType.KRT, debit_wallet_id=treasury_w.wallet_id, credit_wallet_id=student_krt.wallet_id,
            amount=bonus_krt, currency="KRT", organization_id=plan.institution_organization_id, trigger_event_id=f"EDU-BONUS-{plan_id[:8]}",
            description=f"Edu-Pay Scholarship & Cafeteria Bonus (+150 KRT-EDU)"
        )

        inst = EduPayTuitionInstallmentModel(plan_id=plan_id, payer_identity_id=payer_id, amount_kes=amount_kes, external_reference=external_ref, reconciled_ledger_hash=self.ledger_engine.last_hash)
        self.tuition_installments[inst.installment_id] = inst

        self.event_bus.publish(EventPayload(
            event_id=str(uuid.uuid4()), event_type="EXPSUITE_EDUPAY_INSTALLMENT_SETTLED", event_category="EDU_PAY",
            actor_identity_id=payer_id, organization_id=plan.institution_organization_id, correlation_id=external_ref, source_module="KARIS_EDU_PAY",
            timestamp=datetime.now(timezone.utc), payload={"installment_id": inst.installment_id, "plan_id": plan_id, "student_identity_id": plan.student_identity_id, "amount_kes": amount_kes, "bonus_krt_edu_awarded": bonus_krt}
        ))

        return {"installment_id": inst.installment_id, "plan_id": plan_id, "student_identity_id": plan.student_identity_id, "paid_amount_kes": amount_kes, "remaining_tuition_kes": plan.remaining_balance_kes, "bonus_krt_awarded": bonus_krt, "audit_hash": self.ledger_engine.last_hash}

expansion_suite_service = KarisExpansionSuiteService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
