"""
KARIS OS™ :: Reward Engine for KARISFX (`Section 56.6`).
Tracks and distributes transparent KRT rewards across 10 core platform activities.
Enforces strict anti-abuse controls, wash-trading detection, and daily reward ceilings per Rule 1 and Rule 6.
"""

import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

class KarisFXRewardEngine:
    """
    Evaluates reward claims against anti-abuse guardrails and computes KRT payout amounts.
    """
    def __init__(self):
        self.reward_schedule = {
            "TRADING_ACTIVITY": {"base_krt": 15.0, "daily_cap_krt": 300.0, "desc": "Earned for executing verified multi-asset trades with valid holding durations."},
            "LEARNING_COMPLETION": {"base_krt": 100.0, "daily_cap_krt": 500.0, "desc": "Earned for completing educational courses and quizzes on AI & FX trading."},
            "COMMUNITY_CONTRIBUTIONS": {"base_krt": 25.0, "daily_cap_krt": 150.0, "desc": "Earned for high-value forum participation, market analysis, or help posts."},
            "VERIFIED_STRATEGIES": {"base_krt": 250.0, "daily_cap_krt": 1000.0, "desc": "Earned when a published trading strategy achieves verified profitable live performance."},
            "REFERRALS": {"base_krt": 150.0, "daily_cap_krt": 1500.0, "desc": "Earned for onboarding verified KYC Tier 3 traders into the KARISFX ecosystem."},
            "PLATFORM_GROWTH": {"base_krt": 50.0, "daily_cap_krt": 250.0, "desc": "Earned for participating in ecosystem expansion and liquidity bootstrapping."},
            "COMPETITIONS": {"base_krt": 500.0, "daily_cap_krt": 5000.0, "desc": "Earned for placing on official trading leaderboards or hackathon challenges."},
            "BUG_REPORTS": {"base_krt": 350.0, "daily_cap_krt": 3500.0, "desc": "Earned for reporting verified security vulnerabilities or engine anomalies."},
            "EDUCATIONAL_CONTENT": {"base_krt": 200.0, "daily_cap_krt": 1000.0, "desc": "Earned for authoring high-quality tutorials, indicators, or research articles."},
            "ECOSYSTEM_PARTICIPATION": {"base_krt": 20.0, "daily_cap_krt": 200.0, "desc": "Earned for casting votes in decentralized governance proposals."}
        }

    def verify_and_compute_reward(
        self,
        account_id: str,
        activity_type: str,
        custom_amount_krt: float = 0.0,
        recent_claims_today_krt: float = 0.0,
        trade_holding_seconds: float = 3600.0
    ) -> Tuple[bool, str, float, str]:
        """
        Executes anti-abuse verification against wash-trading, high velocity, and daily limits.
        Returns: (is_approved, status_reason, final_reward_krt, verification_hash)
        """
        act_upper = activity_type.upper()
        if act_upper not in self.reward_schedule:
            return (False, f"Invalid activity type: {activity_type}", 0.0, "")

        schedule = self.reward_schedule[act_upper]
        reward_amount = custom_amount_krt if custom_amount_krt > 0.0 else schedule["base_krt"]

        # Anti-abuse check 1: Wash trading check on trading activity
        if act_upper == "TRADING_ACTIVITY":
            # If trade holding duration is under 60 seconds (scalp/wash manipulation attempt), block reward
            if trade_holding_seconds < 60.0:
                return (False, "BLOCKED_WASH_TRADING_VELOCITY_CHECK", 0.0, "HASH_REJECTED_WASH")

        # Anti-abuse check 2: Daily cap check
        if (recent_claims_today_krt + reward_amount) > schedule["daily_cap_krt"]:
            # Partial or capped reward if approaching ceiling
            available = max(0.0, schedule["daily_cap_krt"] - recent_claims_today_krt)
            if available <= 0.0:
                return (False, "BLOCKED_DAILY_REWARD_CAP_EXCEEDED", 0.0, "HASH_REJECTED_CAP")
            reward_amount = round(available, 4)

        # Generate cryptographic verification hash
        payload = f"{account_id}:{act_upper}:{reward_amount}:{datetime.now(timezone.utc).isoformat()}"
        verification_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        return (True, "VERIFIED_CLEAN", round(reward_amount, 4), verification_hash)
