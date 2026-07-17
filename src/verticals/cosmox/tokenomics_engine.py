"""
KARIS OS™ :: COSMOX Tokenomics Engine (`Section 57.10`).
Manages reward budgets, vesting schedules, deflationary burn mechanics (`burn_krt`),
reserve allocations, and systemic KRT circulation analytics across the universal marketplace.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple

class CosmoxTokenomicsEngine:
    """
    Evaluates vesting releases, computes deflationary burns, and tracks KRT circulation parameters.
    """
    def __init__(self):
        self.max_krt_supply = 1000000000.0  # 1 Billion KRT cap
        self.burn_fee_percentage = 2.0      # 2% of platform treasury commissions burned to maintain deflationary value

    def compute_deflationary_burn(self, platform_commission_krt: float) -> float:
        """
        Calculates exact KRT amount to permanently burn from platform commissions (`Rule 5 & Rule 9`).
        """
        if platform_commission_krt <= 0.0:
            return 0.0
        burn_amount = round(platform_commission_krt * (self.burn_fee_percentage / 100.0), 4)
        return burn_amount

    def evaluate_vesting_release(
        self,
        total_allocated_krt: float,
        released_krt: float,
        duration_months: int,
        start_date_iso: str
    ) -> Tuple[float, str]:
        """
        Calculates the monthly vested KRT tranche eligible for release to a beneficiary.
        Returns: (release_amount_krt, status_message)
        """
        if released_krt >= total_allocated_krt:
            return (0.0, "FULLY_VESTED")

        start_dt = datetime.fromisoformat(start_date_iso)
        now = datetime.now(timezone.utc)
        months_elapsed = max(1, int((now - start_dt).days / 30))

        if months_elapsed > duration_months:
            months_elapsed = duration_months

        expected_vested = round(total_allocated_krt * (months_elapsed / float(duration_months)), 4)
        eligible_now = round(max(0.0, expected_vested - released_krt), 4)

        if eligible_now <= 0.0:
            return (0.0, "NO_VESTED_TRANCHE_DUE")

        return (eligible_now, "ELIGIBLE_FOR_RELEASE")

    def generate_token_analytics_snapshot(
        self,
        staked_krt: float,
        burned_krt: float,
        treasury_balance_krt: float,
        reserve_pool_krt: float,
        reward_pool_krt: float
    ) -> Dict[str, Any]:
        """
        Generates executive telemetry on KRT circulation, staking lockups, and reward budgeting.
        """
        circulating_supply = round(self.max_krt_supply - burned_krt - reserve_pool_krt, 4)
        staking_ratio_pct = round((staked_krt / max(1.0, circulating_supply)) * 100.0, 2)

        return {
            "max_krt_supply": self.max_krt_supply,
            "circulating_supply_krt": circulating_supply,
            "total_staked_krt": staked_krt,
            "staking_ratio_pct": staking_ratio_pct,
            "total_burned_krt": burned_krt,
            "treasury_balance_krt": treasury_balance_krt,
            "reserve_pool_balance_krt": reserve_pool_krt,
            "reward_budget_balance_krt": reward_pool_krt,
            "health_status": "OPTIMAL_DEFLATIONARY_EQUILIBRIUM" if burned_krt > 0 else "STABLE_CIRCULATION",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
