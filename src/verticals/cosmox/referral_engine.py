"""
KARIS OS™ :: COSMOX Referral Network Engine (`Section 57.7`).
Manages and verifies referral payouts across three core partner tiers:
1. INDIVIDUAL (`+100 KRT` for active buyer onboarding)
2. MERCHANT (`+500 KRT` upon first verified marketplace sale)
3. DELIVERY_PARTNER (`+250 KRT` upon first verified logistics delivery)
"""

from typing import Dict, Any, Tuple

class CosmoxReferralEngine:
    """
    Evaluates referral qualification status and computes KRT reward bonuses.
    """
    def __init__(self):
        self.referral_tiers = {
            "INDIVIDUAL": {"reward_krt": 100.0, "desc": "Earned when referred buyer verifies KYC Tier 3 and completes first marketplace purchase."},
            "MERCHANT": {"reward_krt": 500.0, "desc": "Earned when referred merchant lists products and settles first order."},
            "DELIVERY_PARTNER": {"reward_krt": 250.0, "desc": "Earned when referred driver completes first verified logistics delivery under Rule 4."}
        }

    def verify_and_compute_referral_reward(
        self,
        referral_type: str,
        referred_kyc_status: str
    ) -> Tuple[bool, str, float]:
        """
        Verifies KYC qualification and returns eligible KRT reward.
        Returns: (is_approved, status_reason, reward_amount_krt)
        """
        r_type = referral_type.upper()
        if r_type not in self.referral_tiers:
            return (False, f"Invalid referral type '{referral_type}'", 0.0)

        if referred_kyc_status != "VERIFIED_TIER_3":
            return (False, "REJECTED_KYC_NOT_VERIFIED", 0.0)

        reward = self.referral_tiers[r_type]["reward_krt"]
        return (True, "REWARDED_CLEAN", reward)
