"""
KARIS OS™ :: KRT Staking Engine for KARISFX (`Section 56.5`).
Manages staking lockup durations (`30, 90, 180, 365 days`), tier evaluation (`BRONZE -> PLATINUM`),
APY reward calculations (`12% - 25%`), fee discounts (`up to 60%`), and reputation boosts.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple

class KarisFXStakingEngine:
    """
    Evaluates KRT staking positions and calculates fee discounts across the multi-asset trading platform.
    """
    def __init__(self):
        self.tiers = {
            "BRONZE": {"min_krt": 500.0, "apy_pct": 12.0, "fee_discount_pct": 15.0, "reputation_boost": 50, "ai_premium": False},
            "SILVER": {"min_krt": 2000.0, "apy_pct": 15.0, "fee_discount_pct": 30.0, "reputation_boost": 150, "ai_premium": True},
            "GOLD": {"min_krt": 5000.0, "apy_pct": 20.0, "fee_discount_pct": 45.0, "reputation_boost": 300, "ai_premium": True},
            "PLATINUM": {"min_krt": 15000.0, "apy_pct": 25.0, "fee_discount_pct": 60.0, "reputation_boost": 500, "ai_premium": True}
        }

    def evaluate_staking_tier(self, amount_krt: float) -> Tuple[str, float, float, int, bool]:
        """
        Determines the applicable staking tier based on staked KRT amount.
        Returns: (tier_name, apy_pct, fee_discount_pct, reputation_boost, ai_premium)
        """
        if amount_krt >= 15000.0:
            tier = "PLATINUM"
        elif amount_krt >= 5000.0:
            tier = "GOLD"
        elif amount_krt >= 2000.0:
            tier = "SILVER"
        elif amount_krt >= 500.0:
            tier = "BRONZE"
        else:
            return ("STANDARD", 5.0, 0.0, 10, False)

        cfg = self.tiers[tier]
        return (tier, cfg["apy_pct"], cfg["fee_discount_pct"], cfg["reputation_boost"], cfg["ai_premium"])

    def calculate_staking_position_specs(
        self,
        amount_krt: float,
        lockup_days: int
    ) -> Dict[str, Any]:
        """
        Calculates expected APY, maturity unlock date, fee discount percentage, and governance voting power.
        """
        if lockup_days not in [30, 90, 180, 365]:
            # Default or normalize duration
            lockup_days = max(30, min(365, lockup_days))

        tier_name, apy_pct, fee_discount_pct, rep_boost, ai_premium = self.evaluate_staking_tier(amount_krt)

        # Longer lockups get an APY duration multiplier bonus (up to +3% APY for 365 days)
        if lockup_days == 365:
            apy_pct += 3.0
        elif lockup_days == 180:
            apy_pct += 1.5

        estimated_annual_reward_krt = amount_krt * (apy_pct / 100.0)
        estimated_period_reward_krt = estimated_annual_reward_krt * (lockup_days / 365.0)

        # Governance voting power is weighted by amount staked times sqrt(lockup_days / 30)
        voting_power = round(amount_krt * ((lockup_days / 30.0) ** 0.5), 4)

        now = datetime.now(timezone.utc)
        unlocks_at = now + timedelta(days=lockup_days)

        return {
            "staking_tier": tier_name,
            "staked_amount_krt": amount_krt,
            "lockup_duration_days": lockup_days,
            "apy_pct": round(apy_pct, 2),
            "fee_discount_pct": fee_discount_pct,
            "reputation_boost": rep_boost,
            "ai_premium_unlocked": ai_premium,
            "governance_voting_power": voting_power,
            "estimated_period_reward_krt": round(estimated_period_reward_krt, 4),
            "staked_at": now.isoformat(),
            "unlocks_at": unlocks_at.isoformat()
        }
