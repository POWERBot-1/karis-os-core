import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from src.domain.models import EventCategory, EventPayload
from src.core.event_bus import event_bus

class OperationalPolicyAndKeyEngine:
    """
    KARIS OS™ Operational Governance Policy, API Key Lifecycle & Dynamic Tax Rule Engine (Section 43 & 47).
    Manages declarative operational policies (`Rule 7`), issues/rotates cryptographic API keys (`Section 38.4`),
    and maintains multi-jurisdictional tax rules (`16% VAT`, `5% Withholding`).
    """
    def __init__(self):
        self.policies: Dict[str, Dict] = {}
        self.api_keys: Dict[str, Dict] = {}
        self.tax_rules: Dict[str, Dict] = {}
        self._seed_default_rules()

    def _seed_default_rules(self):
        self.create_governance_policy("ORG-KARIS-RETAIL", "POL-GOV-RESERVE-RATIO-20PCT", "Treasury Liquidity Reserve Backing", "TREASURY_LIQUIDITY_RESERVE", '{"min_fiat_backing_pct": 20.0}')
        self.create_tax_rule("ORG-KARIS-RETAIL", "KE", "TAX-KE-VAT-16", "Kenya Standard VAT", 16.0)
        self.create_tax_rule("ORG-KARIS-RETAIL", "KE", "TAX-KE-WHT-5", "Kenya Withholding Tax", 5.0, is_withholding=True)

    def create_governance_policy(
        self,
        organization_id: str,
        code: str,
        name: str,
        category: str,
        params_json: str,
        enforcement_mode: str = "STRICT_BLOCKING"
    ) -> Dict:
        p_id = f"POL-GOV-{uuid.uuid4().hex[:6].upper()}"
        policy = {
            "policy_id": p_id,
            "organization_id": organization_id,
            "policy_code": code,
            "policy_name": name,
            "policy_category": category,
            "policy_parameters_json": params_json,
            "enforcement_mode": enforcement_mode,
            "is_active": True
        }
        self.policies[p_id] = policy
        return policy

    def issue_api_key(
        self,
        identity_id: str,
        organization_id: str,
        key_name: str,
        scopes: List[str] = None
    ) -> Dict:
        """Issues cryptographic enterprise API key (`KARIS_LIVE_...`) with SHA-256 secret hashing (`Section 38.4`)."""
        if scopes is None:
            scopes = ["ORDERS:WRITE", "LEDGER:READ", "TRACEABILITY:READ"]

        raw_secret = secrets.token_hex(24)
        prefix = f"KARIS_LIVE_{raw_secret[:8].upper()}"
        secret_hash = hashlib.sha256(raw_secret.encode("utf-8")).hexdigest()
        key_id = f"KEY-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc)

        record = {
            "key_id": key_id,
            "key_prefix": prefix,
            "secret_key_hash": secret_hash,
            "identity_id": identity_id,
            "organization_id": organization_id,
            "key_name": key_name,
            "scopes": scopes,
            "status": "ACTIVE",
            "issued_at": now.isoformat(),
            "expires_at": (now + timedelta(days=365)).isoformat(),
            "raw_api_secret_once": f"{prefix}_{raw_secret}" # Returned once upon creation
        }
        self.api_keys[key_id] = record

        ev = EventPayload(
            event_type="API_KEY_ISSUED_OR_REVOKED",
            event_category=EventCategory.GOVERNANCE,
            actor_identity_id=identity_id,
            organization_id=organization_id,
            correlation_id=key_id,
            source_module="OPERATIONAL_POLICY_AND_KEY_ENGINE",
            payload={
                "key_id": key_id,
                "key_prefix": prefix,
                "identity_id": identity_id,
                "key_name": key_name,
                "status": "ACTIVE"
            }
        )
        event_bus.publish(ev)
        return record

    def revoke_api_key(self, key_id: str, revoker_identity_id: str) -> Dict:
        if key_id not in self.api_keys:
            raise KeyError(f"API Key ID {key_id} not found.")

        rec = self.api_keys[key_id]
        rec["status"] = "REVOKED"

        ev = EventPayload(
            event_type="API_KEY_ISSUED_OR_REVOKED",
            event_category=EventCategory.GOVERNANCE,
            actor_identity_id=revoker_identity_id,
            organization_id=rec["organization_id"],
            correlation_id=key_id,
            source_module="OPERATIONAL_POLICY_AND_KEY_ENGINE",
            payload={
                "key_id": key_id,
                "key_prefix": rec["key_prefix"],
                "identity_id": rec["identity_id"],
                "key_name": rec["key_name"],
                "status": "REVOKED"
            }
        )
        event_bus.publish(ev)
        return {"status": "SUCCESS", "key_id": key_id, "key_prefix": rec["key_prefix"], "message": "API Key successfully revoked."}

    def create_tax_rule(
        self,
        organization_id: str,
        jurisdiction: str,
        code: str,
        name: str,
        rate_pct: float,
        is_withholding: bool = False
    ) -> Dict:
        t_id = f"TAX-R-{uuid.uuid4().hex[:6].upper()}"
        rule = {
            "tax_rule_id": t_id,
            "organization_id": organization_id,
            "jurisdiction_code": jurisdiction,
            "tax_code": code,
            "tax_name": name,
            "tax_rate_pct": rate_pct,
            "is_withholding": is_withholding,
            "is_active": True
        }
        self.tax_rules[t_id] = rule
        return rule

operational_policy_engine = OperationalPolicyAndKeyEngine()
