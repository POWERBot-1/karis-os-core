import uuid
from typing import Dict, List, Optional
from src.domain.models import EventCategory, EventPayload, InvestmentPoolModel
from src.core.event_bus import event_bus
from src.core.ai_gateway import ai_gateway
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.domain.models import AssetType, WalletType

class FinanceInvestmentService:
    """
    KARIS OS™ Investor Capital & Lending Service.
    Enforces Section 19 (Credit & Lending Engine) & Section 25 (Investor & Capital Management Engine).
    Enforces Rule 3 (No Credit Approval -> No Credit Purchase) and Rule 10 (AI Risk Evaluation).
    """
    def __init__(self):
        self.pools: Dict[str, InvestmentPoolModel] = {}
        self.allocations: Dict[str, Dict] = {}
        self.credit_applications: Dict[str, Dict] = {}

    def create_investment_pool(
        self,
        pool_code: str,
        pool_name: str,
        category: str,
        target_capital_kes: float,
        expected_roi_pct: float
    ) -> InvestmentPoolModel:
        pool = InvestmentPoolModel(
            pool_id=str(uuid.uuid4()),
            pool_code=pool_code,
            pool_name=pool_name,
            pool_category=category,
            target_capital_kes=target_capital_kes,
            expected_annual_roi_pct=expected_roi_pct
        )
        self.pools[pool.pool_id] = pool
        return pool

    def deposit_capital(
        self,
        pool_id: str,
        investor_identity_id: str,
        organization_id: str,
        amount_kes: float
    ) -> Dict:
        if pool_id not in self.pools:
            raise KeyError(f"Investment Pool ID {pool_id} not found.")

        pool = self.pools[pool_id]
        units = round(amount_kes / 100.0, 4) # 100 KES = 1 Unit
        pool.total_capital_raised_kes += amount_kes

        alloc_id = str(uuid.uuid4())
        alloc = {
            "allocation_id": alloc_id,
            "pool_id": pool_id,
            "investor_identity_id": investor_identity_id,
            "capital_invested_kes": amount_kes,
            "units_owned": units
        }
        self.allocations[alloc_id] = alloc

        ev = EventPayload(
            event_type="INVESTOR_CAPITAL_DEPOSITED",
            event_category=EventCategory.TREASURY,
            actor_identity_id=investor_identity_id,
            organization_id=organization_id,
            correlation_id=alloc_id,
            source_module="INVESTOR_CAPITAL_ENGINE",
            payload={
                "allocation_id": alloc_id,
                "pool_id": pool_id,
                "investor_identity_id": investor_identity_id,
                "capital_invested_kes": amount_kes,
                "investment_units_owned": units
            }
        )
        event_bus.publish(ev)
        return alloc

    def distribute_pool_returns(
        self,
        pool_id: str,
        allocation_id: str,
        return_amount_kes: float,
        organization_id: str
    ) -> Dict:
        if allocation_id not in self.allocations:
            raise KeyError(f"Allocation ID {allocation_id} not found.")

        alloc = self.allocations[allocation_id]
        investor_id = alloc["investor_identity_id"]

        ev = EventPayload(
            event_type="TREASURY_RETURN_DISTRIBUTED",
            event_category=EventCategory.TREASURY,
            actor_identity_id="TREASURY_ENGINE",
            organization_id=organization_id,
            correlation_id=str(uuid.uuid4()),
            source_module="TREASURY_ENGINE",
            payload={
                "distribution_id": str(uuid.uuid4()),
                "pool_id": pool_id,
                "allocation_id": allocation_id,
                "investor_identity_id": investor_id,
                "return_amount_kes": return_amount_kes,
                "krt_bonus_reward": round(return_amount_kes * 0.05, 2)
            }
        )
        event_bus.publish(ev)
        return {"status": "SUCCESS", "return_amount_kes": return_amount_kes, "investor_id": investor_id}

    def apply_for_credit(
        self,
        borrower_identity_id: str,
        organization_id: str,
        requested_amount_kes: float,
        historical_spend_kes: float = 50000.0
    ) -> Dict:
        # Ask Risk AI to evaluate application (Rule 3 & Rule 10)
        ai_eval = ai_gateway.evaluate_credit_risk(borrower_identity_id, requested_amount_kes, historical_spend_kes)

        app_id = str(uuid.uuid4())
        app = {
            "application_id": app_id,
            "organization_id": organization_id,
            "borrower_identity_id": borrower_identity_id,
            "requested_amount_kes": requested_amount_kes,
            "ai_risk_score": ai_eval.risk_score,
            "ai_recommendation": ai_eval.recommendation,
            "status": "CREDIT_APPROVED" if "APPROVE" in ai_eval.recommendation else "PENDING_HUMAN_REVIEW"
        }
        self.credit_applications[app_id] = app
        return app

    def approve_and_disburse_loan(self, application_id: str, approver_identity_id: str) -> Dict:
        """Enforces Rule 3: No Credit Approval -> No Credit Purchase."""
        if application_id not in self.credit_applications:
            raise KeyError(f"Application ID {application_id} not found.")

        app = self.credit_applications[application_id]
        app["status"] = "CREDIT_APPROVED"
        app["approved_by_identity_id"] = approver_identity_id

        # Disburse funds into borrower CREDIT_WALLET from Treasury CREDIT_WALLET
        borrower_credit_wallet = wallet_engine.get_wallet_by_keys(
            identity_id=app["borrower_identity_id"],
            organization_id=app["organization_id"],
            wallet_type=WalletType.CREDIT_WALLET,
            asset_type=AssetType.CREDIT
        )
        treasury_credit_wallet = wallet_engine.get_wallet_by_keys(
            identity_id="TREASURY_IDENTITY",
            organization_id=app["organization_id"],
            wallet_type=WalletType.CREDIT_WALLET,
            asset_type=AssetType.CREDIT
        )
        if not treasury_credit_wallet:
            treasury_credit_wallet = wallet_engine.create_wallet(
                identity_id="TREASURY_IDENTITY",
                organization_id=app["organization_id"],
                wallet_type=WalletType.CREDIT_WALLET,
                asset_type=AssetType.CREDIT,
                initial_balance=10_000_000.0
            )

        if borrower_credit_wallet and treasury_credit_wallet:
            ledger_engine.record_transaction(
                transaction_id=str(uuid.uuid4()),
                asset_type=AssetType.CREDIT,
                debit_wallet_id=treasury_credit_wallet.wallet_id,
                credit_wallet_id=borrower_credit_wallet.wallet_id,
                amount=app["requested_amount_kes"],
                currency="CREDIT",
                organization_id=app["organization_id"],
                trigger_event_id=application_id,
                description=f"Loan Disbursement for application {application_id} approved by {approver_identity_id}"
            )

        return {"status": "SUCCESS", "application_id": application_id, "disbursed_amount": app["requested_amount_kes"]}

finance_investment_service = FinanceInvestmentService()
