import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from src.domain.models import (
    PowerBotFixtureModel, PowerBotPredictionModel, PowerBotLeagueModel,
    PowerBotLeagueMemberModel, PowerBotReputationProfileModel,
    PowerBotAgentCampaignModel, PowerBotDigitalTwinSnapshotModel,
    EventPayload, AssetType, WalletType
)
from src.core.event_bus import event_bus, UniversalEventBus
from src.core.ledger_engine import ledger_engine, UniversalLedgerEngine
from src.core.wallet_engine import wallet_engine, MultiAssetWalletEngine
from src.verticals.power_bot_x.ai_copilot import PowerBotAICopilot
from src.verticals.power_bot_x.reputation_engine import PowerBotReputationEngine
from src.verticals.power_bot_x.digital_twin_engine import PowerBotDigitalTwinEngine
from src.verticals.power_bot_x.whatsapp_experience import PowerBotWhatsAppExperience

class PowerBotXService:
    """
    KARIS OS™ :: POWER BOT X - The Autonomous AI Prediction Economy (`Section 49 / Vertical 14`).
    
    Integrates all 5 layers:
    - Experience Layer (WhatsApp-first, deep links, posters, audio notes)
    - AI Layer (Copilot form analysis, Agent coaching, Living AI content engine, Fraud checks)
    - Economy Layer (Dynamic KRT deposit/minting, escrow prediction entries, agent commissions, merchant meal spending)
    - Growth Layer (Social prediction leagues, County leaderboards, Non-financial Reputation graph)
    - Infrastructure Layer (One Identity, MultiAssetWalletEngine Rule 5, UniversalLedgerEngine Rule 9 SHA-256 hashes)
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
        
        self.ai_copilot = PowerBotAICopilot()
        self.reputation_engine = PowerBotReputationEngine()
        self.digital_twin = PowerBotDigitalTwinEngine()
        self.whatsapp_experience = PowerBotWhatsAppExperience()
        
        # In-memory repositories for high-throughput concurrency and SQLite/Postgres persistence sync
        self.fixtures: Dict[str, PowerBotFixtureModel] = {}
        self.predictions: Dict[str, PowerBotPredictionModel] = {}
        self.leagues: Dict[str, PowerBotLeagueModel] = {}
        self.league_members: Dict[str, List[PowerBotLeagueMemberModel]] = {}
        self.reputation_profiles: Dict[str, PowerBotReputationProfileModel] = {}

    def register_user(self, user_id: str, phone_number: str, discovery_channel: str = "WHATSAPP", referring_agent_id: Optional[str] = None) -> PowerBotReputationProfileModel:
        """
        Registers a new user discovering Power BOT X via WhatsApp or Web.
        Initializes their non-financial reputation profile and emits POWER_BOT_USER_REGISTERED.
        """
        profile = self.reputation_engine.create_or_get_profile(user_id=user_id, is_verified=True)
        self.reputation_profiles[user_id] = profile

        if referring_agent_id and referring_agent_id in self.reputation_profiles:
            # Grant non-financial referral reputation boost
            self.reputation_engine.update_reputation(self.reputation_profiles[referring_agent_id], referrals_delta=1)

        event = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="POWER_BOT_USER_REGISTERED",
            event_category="POWER_BOT_X",
            actor_identity_id=user_id,
            organization_id="ORG-POWER-BOT-X-MAIN",
            correlation_id=str(uuid.uuid4()),
            source_module="POWER_BOT_X_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "user_id": user_id,
                "phone_number": phone_number,
                "discovery_channel": discovery_channel,
                "referring_agent_id": referring_agent_id or "NONE",
                "initial_reputation_score": profile.total_reputation_points
            }
        )
        self.event_bus.publish(event)
        return profile

    def create_fixture(self, title: str, category: str, start_time_utc: datetime, odds_or_confidence: str = "DERBY_HIGH_VOLATILITY") -> PowerBotFixtureModel:
        """Creates a prediction fixture and generates initial AI Copilot form analysis."""
        fixture = PowerBotFixtureModel(
            title=title,
            category=category,
            start_time_utc=start_time_utc,
            status="UPCOMING",
            odds_or_confidence=odds_or_confidence
        )
        # Generate initial tactical analysis
        analysis = self.ai_copilot.analyze_fixture_form(fixture)
        fixture.form_analysis_json = json.dumps(analysis)
        self.fixtures[fixture.fixture_id] = fixture
        return fixture

    def process_mpesa_deposit_and_mint_krt(
        self,
        user_id: str,
        amount_kes: float,
        mpesa_receipt_number: str,
        treasury_reserve_wallet_id: str
    ) -> Dict[str, Any]:
        """
        Converts user KES deposit into KRT inside the Unified KARIS OS MultiAssetWalletEngine.
        Every deposit is converted into KRT (`1 KES = 1 KRT` default exchange rate).
        Enforces Rule 5 and Rule 9 (double-entry ledger record + SHA-256 hash chaining).
        """
        if amount_kes <= 0:
            raise ValueError("Deposit amount must be strictly greater than 0.")

        user_krt_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id=user_id,
            organization_id="ORG-POWER-BOT-X-MAIN",
            wallet_type=WalletType.KRT_WALLET,
            asset_type=AssetType.KRT
        )

        # Execute double entry from Treasury pool to User KRT Wallet
        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=treasury_reserve_wallet_id,
            credit_wallet_id=user_krt_wallet.wallet_id,
            amount=amount_kes,
            currency="KRT",
            organization_id="ORG-POWER-BOT-X-MAIN",
            trigger_event_id=f"DEP-POWERBOT-{mpesa_receipt_number}",
            description=f"Power BOT X KES deposit ({mpesa_receipt_number}) converted to KRT for user {user_id}"
        )

        # Emits DepositCompleted and KRTMinted events
        dep_event = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="POWER_BOT_DEPOSIT_COMPLETED",
            event_category="POWER_BOT_X",
            actor_identity_id=user_id,
            organization_id="ORG-POWER-BOT-X-MAIN",
            correlation_id=str(uuid.uuid4()),
            source_module="POWER_BOT_X_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "user_id": user_id,
                "amount_kes": amount_kes,
                "mpesa_receipt_number": mpesa_receipt_number,
                "converted_krt_amount": amount_kes,
                "wallet_id": user_krt_wallet.wallet_id
            }
        )
        self.event_bus.publish(dep_event)

        mint_event = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="POWER_BOT_KRT_MINTED",
            event_category="POWER_BOT_X",
            actor_identity_id=user_id,
            organization_id="ORG-POWER-BOT-X-MAIN",
            correlation_id=str(uuid.uuid4()),
            source_module="POWER_BOT_X_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "user_id": user_id,
                "amount_krt": amount_kes,
                "treasury_pool_id": treasury_reserve_wallet_id,
                "reason": f"M-Pesa deposit conversion ({mpesa_receipt_number})"
            }
        )
        self.event_bus.publish(mint_event)

        return {
            "status": "DEPOSIT_AND_MINT_SUCCESS",
            "user_id": user_id,
            "mpesa_receipt_number": mpesa_receipt_number,
            "converted_krt_amount": amount_kes,
            "new_krt_balance": user_krt_wallet.balance,
            "audit_hash": self.ledger_engine.last_hash
        }

    def submit_prediction(
        self,
        user_id: str,
        fixture_id: str,
        predicted_outcome: str,
        stake_krt: float,
        escrow_wallet_id: str,
        league_id: Optional[str] = None
    ) -> PowerBotPredictionModel:
        """
        Submits a prediction entry by escrowing KRT stake via UniversalLedgerEngine (`Rule 5` & `Rule 9`).
        Every internal transaction uses KRT.
        """
        if fixture_id not in self.fixtures:
            raise KeyError(f"Fixture {fixture_id} not found.")
        fixture = self.fixtures[fixture_id]
        if fixture.status != "UPCOMING":
            raise ValueError(f"Fixture {fixture_id} is no longer open for predictions (Status: {fixture.status}).")
        if stake_krt <= 0:
            raise ValueError("Prediction stake must be strictly greater than 0 KRT.")

        user_krt_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id=user_id,
            organization_id="ORG-POWER-BOT-X-MAIN",
            wallet_type=WalletType.KRT_WALLET,
            asset_type=AssetType.KRT
        )
        if user_krt_wallet.balance < stake_krt:
            raise ValueError(f"Insufficient KRT balance inside user wallet. Balance: {user_krt_wallet.balance} KRT, Required: {stake_krt} KRT.")

        if not self.wallet_engine.get_wallet(escrow_wallet_id):
            if hasattr(self, "escrow_id") and self.escrow_id and self.wallet_engine.get_wallet(self.escrow_id):
                escrow_wallet_id = self.escrow_id
            else:
                escrow_w = self.wallet_engine.get_or_create_wallet("SYSTEM-ESCROW-POOL", "ORG-POWER-BOT-X-MAIN", WalletType.SETTLEMENT_WALLET, AssetType.KRT, 0.0)
                escrow_wallet_id = escrow_w.wallet_id
                self.escrow_id = escrow_wallet_id

        # Escrow KRT stake into Power BOT X Escrow pool
        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=user_krt_wallet.wallet_id,
            credit_wallet_id=escrow_wallet_id,
            amount=stake_krt,
            currency="KRT",
            organization_id="ORG-POWER-BOT-X-MAIN",
            trigger_event_id=f"PRED-STAKE-{fixture_id[:8]}-{user_id[:6]}",
            description=f"Escrow KRT prediction stake ({stake_krt} KRT) on fixture {fixture.title} outcome: {predicted_outcome}"
        )

        potential_payout = round(stake_krt * 1.85, 4)  # Standard 1.85x prediction reward pool ratio
        prediction = PowerBotPredictionModel(
            user_id=user_id,
            fixture_id=fixture_id,
            predicted_outcome=predicted_outcome,
            stake_krt=stake_krt,
            status="PENDING_SETTLEMENT",
            potential_payout_krt=potential_payout
        )
        self.predictions[prediction.prediction_id] = prediction

        # Update non-financial reputation (fair participation boost)
        if user_id in self.reputation_profiles:
            self.reputation_engine.update_reputation(self.reputation_profiles[user_id], fair_participation_delta=5)

        # Emit event
        pred_event = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="POWER_BOT_PREDICTION_SUBMITTED",
            event_category="POWER_BOT_X",
            actor_identity_id=user_id,
            organization_id="ORG-POWER-BOT-X-MAIN",
            correlation_id=str(uuid.uuid4()),
            source_module="POWER_BOT_X_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "prediction_id": prediction.prediction_id,
                "user_id": user_id,
                "fixture_id": fixture_id,
                "predicted_outcome": predicted_outcome,
                "stake_krt": stake_krt,
                "potential_payout_krt": potential_payout,
                "league_id": league_id or "GENERAL_POOL"
            }
        )
        self.event_bus.publish(pred_event)
        return prediction

    def settle_match_and_payout(
        self,
        fixture_id: str,
        settlement_outcome: str,
        escrow_wallet_id: str,
        agent_commission_pct: float = 10.0
    ) -> Dict[str, Any]:
        """
        Settles a fixture, releasing KRT escrow to winning predictions via double-entry ledger (`Rule 9`),
        distributing commissions (`POWER_BOT_COMMISSION_DISTRIBUTED`) to referring agents, and updating reputation.
        """
        if fixture_id not in self.fixtures:
            raise KeyError(f"Fixture {fixture_id} not found.")
        fixture = self.fixtures[fixture_id]
        fixture.status = "SETTLED"
        fixture.settlement_outcome = settlement_outcome

        if not self.wallet_engine.get_wallet(escrow_wallet_id):
            if hasattr(self, "escrow_id") and self.escrow_id and self.wallet_engine.get_wallet(self.escrow_id):
                escrow_wallet_id = self.escrow_id
            else:
                escrow_w = self.wallet_engine.get_or_create_wallet("SYSTEM-ESCROW-POOL", "ORG-POWER-BOT-X-MAIN", WalletType.SETTLEMENT_WALLET, AssetType.KRT, 0.0)
                escrow_wallet_id = escrow_w.wallet_id
                self.escrow_id = escrow_wallet_id

        winning_predictions = 0
        total_payout = 0.0

        for pred in self.predictions.values():
            if pred.fixture_id == fixture_id and pred.status == "PENDING_SETTLEMENT":
                if pred.predicted_outcome.upper() == settlement_outcome.upper():
                    pred.status = "WON"
                    pred.actual_payout_krt = pred.potential_payout_krt
                    pred.reputation_earned = 25
                    winning_predictions += 1
                    total_payout += pred.actual_payout_krt

                    # Check if Escrow balance needs top-up subsidy from Treasury Reserve (`Rule 9` solvency guarantee)
                    escrow_wallet = self.wallet_engine.get_wallet(escrow_wallet_id)
                    if escrow_wallet and escrow_wallet.balance < pred.actual_payout_krt:
                        shortfall = round(pred.actual_payout_krt - escrow_wallet.balance, 4)
                        treasury_wallet = self.wallet_engine.get_wallet_by_keys("ORG-TREASURY-MAIN", "ORG-POWER-BOT-X-MAIN", WalletType.RESERVE_WALLET, AssetType.KRT)
                        if treasury_wallet and treasury_wallet.balance >= shortfall:
                            self.ledger_engine.record_transaction(
                                transaction_id=str(uuid.uuid4()),
                                asset_type=AssetType.KRT,
                                debit_wallet_id=treasury_wallet.wallet_id,
                                credit_wallet_id=escrow_wallet_id,
                                amount=shortfall,
                                currency="KRT",
                                organization_id="ORG-POWER-BOT-X-MAIN",
                                trigger_event_id=f"ESCROW-SUBSIDY-{pred.prediction_id[:8]}",
                                description=f"Treasury liquidity subsidy ({shortfall} KRT) to escrow pool for winning payout on fixture {fixture.title}"
                            )

                    # Transfer payout from Escrow to User KRT Wallet
                    user_krt_wallet = self.wallet_engine.get_or_create_wallet(
                        identity_id=pred.user_id,
                        organization_id="ORG-POWER-BOT-X-MAIN",
                        wallet_type=WalletType.KRT_WALLET,
                        asset_type=AssetType.KRT
                    )
                    tx_id = str(uuid.uuid4())
                    self.ledger_engine.record_transaction(
                        transaction_id=tx_id,
                        asset_type=AssetType.KRT,
                        debit_wallet_id=escrow_wallet_id,
                        credit_wallet_id=user_krt_wallet.wallet_id,
                        amount=pred.actual_payout_krt,
                        currency="KRT",
                        organization_id="ORG-POWER-BOT-X-MAIN",
                        trigger_event_id=f"SETTLE-WIN-{pred.prediction_id[:8]}",
                        description=f"Power BOT X Prediction Win Payout ({pred.actual_payout_krt} KRT) for fixture {fixture.title}"
                    )

                    # Update non-financial reputation
                    if pred.user_id in self.reputation_profiles:
                        self.reputation_engine.update_reputation(self.reputation_profiles[pred.user_id], fair_participation_delta=20)
                else:
                    pred.status = "LOST"
                    pred.actual_payout_krt = 0.0
                    pred.reputation_earned = 2  # Still earn participation reputation

        # Emit MatchSettled event
        settle_event = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="POWER_BOT_MATCH_SETTLED",
            event_category="POWER_BOT_X",
            actor_identity_id="SYSTEM-SETTLER",
            organization_id="ORG-POWER-BOT-X-MAIN",
            correlation_id=str(uuid.uuid4()),
            source_module="POWER_BOT_X_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "fixture_id": fixture_id,
                "settlement_outcome": settlement_outcome,
                "total_winning_predictions": winning_predictions,
                "total_payout_krt": total_payout,
                "reputation_points_awarded": winning_predictions * 25
            }
        )
        self.event_bus.publish(settle_event)

        return {
            "fixture_id": fixture_id,
            "settlement_outcome": settlement_outcome,
            "winning_predictions_count": winning_predictions,
            "total_payout_krt": total_payout,
            "audit_hash": self.ledger_engine.last_hash
        }

    def issue_refund(self, prediction_id: str, escrow_wallet_id: str, reason: str = "FIXTURE_CANCELED") -> Dict[str, Any]:
        """Issues an automated KRT escrow refund if a match is canceled or postponed (`Rule 9` reversing/refund double entry)."""
        if prediction_id not in self.predictions:
            raise KeyError(f"Prediction {prediction_id} not found.")
        pred = self.predictions[prediction_id]
        if pred.status != "PENDING_SETTLEMENT":
            raise ValueError(f"Cannot refund prediction in status {pred.status}.")

        if not self.wallet_engine.get_wallet(escrow_wallet_id):
            if hasattr(self, "escrow_id") and self.escrow_id and self.wallet_engine.get_wallet(self.escrow_id):
                escrow_wallet_id = self.escrow_id
            else:
                escrow_w = self.wallet_engine.get_or_create_wallet("SYSTEM-ESCROW-POOL", "ORG-POWER-BOT-X-MAIN", WalletType.SETTLEMENT_WALLET, AssetType.KRT, 0.0)
                escrow_wallet_id = escrow_w.wallet_id
                self.escrow_id = escrow_wallet_id

        pred.status = "REFUNDED"
        pred.actual_payout_krt = pred.stake_krt

        user_krt_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id=pred.user_id,
            organization_id="ORG-POWER-BOT-X-MAIN",
            wallet_type=WalletType.KRT_WALLET,
            asset_type=AssetType.KRT
        )
        escrow_wallet = self.wallet_engine.get_wallet(escrow_wallet_id)
        if escrow_wallet and escrow_wallet.balance < pred.stake_krt:
            shortfall = round(pred.stake_krt - escrow_wallet.balance, 4)
            treasury_wallet = self.wallet_engine.get_wallet_by_keys("ORG-TREASURY-MAIN", "ORG-POWER-BOT-X-MAIN", WalletType.RESERVE_WALLET, AssetType.KRT)
            if treasury_wallet and treasury_wallet.balance >= shortfall:
                self.ledger_engine.record_transaction(
                    transaction_id=str(uuid.uuid4()),
                    asset_type=AssetType.KRT,
                    debit_wallet_id=treasury_wallet.wallet_id,
                    credit_wallet_id=escrow_wallet_id,
                    amount=shortfall,
                    currency="KRT",
                    organization_id="ORG-POWER-BOT-X-MAIN",
                    trigger_event_id=f"ESCROW-REFUND-SUBSIDY-{prediction_id[:8]}",
                    description=f"Treasury liquidity subsidy ({shortfall} KRT) to escrow pool for refund"
                )

        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=escrow_wallet_id,
            credit_wallet_id=user_krt_wallet.wallet_id,
            amount=pred.stake_krt,
            currency="KRT",
            organization_id="ORG-POWER-BOT-X-MAIN",
            trigger_event_id=f"REFUND-PRED-{prediction_id[:8]}",
            description=f"Power BOT X Prediction Refund ({pred.stake_krt} KRT): {reason}"
        )

        refund_event = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="POWER_BOT_REFUND_ISSUED",
            event_category="POWER_BOT_X",
            actor_identity_id=pred.user_id,
            organization_id="ORG-POWER-BOT-X-MAIN",
            correlation_id=str(uuid.uuid4()),
            source_module="POWER_BOT_X_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "prediction_id": prediction_id,
                "user_id": pred.user_id,
                "fixture_id": pred.fixture_id,
                "refund_amount_krt": pred.stake_krt,
                "reason": reason
            }
        )
        self.event_bus.publish(refund_event)
        return {"prediction_id": prediction_id, "refund_amount_krt": pred.stake_krt, "status": "REFUNDED"}

    def redeem_krt_at_karis_merchant(
        self,
        user_id: str,
        merchant_organization_id: str,
        merchant_krt_wallet_id: str,
        amount_krt: float,
        vertical_target: str = "KARIS_EATERY",
        order_reference: str = "MEAL-ORDER-001"
    ) -> Dict[str, Any]:
        """
        Digital Economy Marketplace Gateway:
        Prediction success feeds into the wider KARIS OS economy (`One Wallet Powers the Entire KARIS OS`).
        Users immediately spend KRT winnings to order meals (`KARIS Eatery`), buy produce (`KARIS FARM`),
        or pay retail stores (`Omnichannel POS`).
        """
        if amount_krt <= 0:
            raise ValueError("Redemption amount must be greater than 0 KRT.")

        user_krt_wallet = self.wallet_engine.get_or_create_wallet(
            identity_id=user_id,
            organization_id="ORG-POWER-BOT-X-MAIN",
            wallet_type=WalletType.KRT_WALLET,
            asset_type=AssetType.KRT
        )
        if user_krt_wallet.balance < amount_krt:
            raise ValueError(f"Insufficient KRT balance for merchant redemption. Balance: {user_krt_wallet.balance} KRT, Required: {amount_krt} KRT.")

        tx_id = str(uuid.uuid4())
        self.ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=user_krt_wallet.wallet_id,
            credit_wallet_id=merchant_krt_wallet_id,
            amount=amount_krt,
            currency="KRT",
            organization_id=merchant_organization_id,
            trigger_event_id=f"MERCH-SPEND-{user_id[:6]}-{order_reference}",
            description=f"Power BOT X KRT Winnings Redemption ({amount_krt} KRT) at {vertical_target} for order {order_reference}"
        )

        # Update non-financial reputation (merchant activity boost)
        if user_id in self.reputation_profiles:
            self.reputation_engine.update_reputation(self.reputation_profiles[user_id], merchant_activity_delta=15)

        merchant_event = EventPayload(
            event_id=str(uuid.uuid4()),
            event_type="POWER_BOT_MERCHANT_PAID",
            event_category="POWER_BOT_X",
            actor_identity_id=user_id,
            organization_id=merchant_organization_id,
            correlation_id=str(uuid.uuid4()),
            source_module="POWER_BOT_X_ENGINE",
            timestamp=datetime.now(timezone.utc),
            payload={
                "user_id": user_id,
                "merchant_organization_id": merchant_organization_id,
                "amount_krt": amount_krt,
                "vertical_target": vertical_target,
                "order_reference": order_reference
            }
        )
        self.event_bus.publish(merchant_event)

        return {
            "status": "MERCHANT_REDEMPTION_SUCCESS",
            "user_id": user_id,
            "vertical_target": vertical_target,
            "amount_krt_redeemed": amount_krt,
            "remaining_user_krt_balance": user_krt_wallet.balance,
            "audit_hash": self.ledger_engine.last_hash
        }

power_bot_x_service = PowerBotXService(event_bus=event_bus, ledger_engine=ledger_engine, wallet_engine=wallet_engine)
