import uuid
from typing import Dict
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.ledger_engine import ledger_engine
from src.core.wallet_engine import wallet_engine
from src.integrations.erp_tax_sync import erp_notification_engine

class AiCrmIntelligenceEngine:
    """
    KARIS OS™ AI CRM Intelligence Engine (Section 23.4).
    Predicts customer churn risk, calculates exact Lifetime Value (LTV), segments customers,
    and automatically dispatches win-back retention loyalty grants (`500 KRT`) when churn risk exceeds 60%.
    """
    def __init__(self):
        self.evaluations: Dict[str, Dict] = {}

    def evaluate_customer_ltv_and_churn(
        self,
        identity_id: str,
        historical_spend_kes: float,
        purchase_frequency_days: float,
        organization_id: str = "ORG-KARIS-RETAIL",
        customer_name: str = "Amina Wanjiku"
    ) -> Dict:
        # LTV Formula: spend * frequency factor * 5-year retention
        ltv = round(historical_spend_kes * max((365.0 / max(purchase_frequency_days, 1.0)) * 2.5, 1.2), 2)
        
        # Churn Risk estimation
        if purchase_frequency_days > 90.0:
            churn_risk = 82.5
            tier = "AT_RISK_LOYALIST"
            action = "ALERT: High churn risk detected (>90 days inactive). Triggering automatic 500 KRT win-back retention grant!"
            triggered = True
        elif purchase_frequency_days > 45.0:
            churn_risk = 48.0
            tier = "HIGH_GROWTH_LEAD"
            action = "Recommend promotional discount coupon."
            triggered = False
        else:
            churn_risk = 12.0
            tier = "LIFETIME_CHAMPION"
            action = "Optimal engagement. Enqueue VIP priority support SLA."
            triggered = False

        eval_id = f"CRM-EVAL-{uuid.uuid4().hex[:8].upper()}"
        record = {
            "evaluation_id": eval_id,
            "identity_id": identity_id,
            "organization_id": organization_id,
            "historical_spend_kes": historical_spend_kes,
            "purchase_frequency_days": purchase_frequency_days,
            "calculated_lifetime_value_kes": ltv,
            "predicted_churn_risk_pct": churn_risk,
            "customer_segment_tier": tier,
            "ai_recommended_action": action,
            "retention_campaign_triggered": triggered
        }
        self.evaluations[eval_id] = record

        # Emit CRM Evaluation Event
        ev = EventPayload(
            event_type="CRM_CHURN_PREDICTION_EVALUATED",
            event_category=EventCategory.IDENTITY,
            actor_identity_id="AI_CRM_ENGINE",
            organization_id=organization_id,
            correlation_id=eval_id,
            source_module="AI_CRM_INTELLIGENCE_ENGINE",
            payload={
                "evaluation_id": eval_id,
                "identity_id": identity_id,
                "calculated_lifetime_value_kes": ltv,
                "predicted_churn_risk_pct": churn_risk,
                "customer_segment_tier": tier,
                "retention_campaign_triggered": triggered
            }
        )
        event_bus.publish(ev)

        # If retention triggered, execute automatic KRT grant and dispatch email notification (Rule 5 & Rule 7)
        if triggered:
            self.execute_automated_retention_campaign(identity_id, organization_id, customer_name, 500.0)

        return record

    def execute_automated_retention_campaign(
        self,
        identity_id: str,
        organization_id: str,
        customer_name: str,
        bonus_tokens: float = 500.0
    ) -> Dict:
        cust_krt = wallet_engine.get_wallet_by_keys(identity_id, organization_id, WalletType.KRT_WALLET, AssetType.KRT)
        if not cust_krt:
            cust_krt = wallet_engine.create_wallet(identity_id, organization_id, WalletType.KRT_WALLET, AssetType.KRT, 0.0)
        
        treasury_krt = wallet_engine.get_wallet_by_keys("TREASURY_IDENTITY", organization_id, WalletType.REWARD_POOL, AssetType.KRT)
        if not treasury_krt:
            treasury_krt = wallet_engine.create_wallet("TREASURY_IDENTITY", organization_id, WalletType.REWARD_POOL, AssetType.KRT, 1_000_000.0)

        tx_id = str(uuid.uuid4())
        ledger_engine.record_transaction(
            transaction_id=tx_id,
            asset_type=AssetType.KRT,
            debit_wallet_id=treasury_krt.wallet_id,
            credit_wallet_id=cust_krt.wallet_id,
            amount=bonus_tokens,
            currency="KRT",
            organization_id=organization_id,
            trigger_event_id=tx_id,
            description=f"Automated AI CRM Win-Back Retention Grant ({bonus_tokens} KRT)"
        )

        # Dispatch retention email notification
        erp_notification_engine.dispatch_notification(
            "TPL-RETENTION-DISCOUNT-EMAIL", identity_id, "amina.w@gmail.com",
            {"customer_name": customer_name, "bonus_tokens": str(bonus_tokens)}, organization_id
        )
        return {"status": "RETENTION_GRANTED", "identity_id": identity_id, "bonus_awarded": bonus_tokens}

crm_ai_engine = AiCrmIntelligenceEngine()
