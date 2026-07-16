import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from src.domain.models import PowerBotReputationProfileModel

class PowerBotReputationEngine:
    """
    KARIS OS™ :: POWER BOT X Reputation Graph Engine (`Growth Layer`).
    
    Calculates and updates non-financial reputation profiles based on:
    - fair participation
    - account longevity
    - verified identity
    - community engagement
    - referrals
    - merchant activity (`KARIS Eatery`, `KARIS FARM` purchases)
    
    Core Invariant:
    Reputation unlocks new experiences (creating county leagues, early AI copilot access, tier badges)
    but DOES NOT determine game outcomes or prediction payouts.
    """
    def __init__(self):
        self.tiers = {
            200: "SCOUT",
            500: "CLUB_STRATEGIST",
            1000: "COUNTY_CAPTAIN",
            2500: "NATIONAL_ORACLE",
            5000: "KARIS_LEGEND"
        }

    def compute_tier(self, total_points: int) -> str:
        current_tier = "SCOUT"
        for points_threshold in sorted(self.tiers.keys()):
            if total_points >= points_threshold:
                current_tier = self.tiers[points_threshold]
        return current_tier

    def create_or_get_profile(self, user_id: str, is_verified: bool = True) -> PowerBotReputationProfileModel:
        """Initializes a new reputation profile with default score bonuses."""
        verified_bonus = 50 if is_verified else 0
        total_points = 100 + 1 + verified_bonus + 50
        tier = self.compute_tier(total_points)
        
        profile = PowerBotReputationProfileModel(
            user_id=user_id,
            fair_participation_score=100,
            account_longevity_days=1,
            verified_identity_bonus=verified_bonus,
            community_engagement_score=50,
            referral_count=0,
            merchant_activity_score=0,
            total_reputation_points=total_points,
            tier=tier,
            updated_at=datetime.now(timezone.utc)
        )
        return profile

    def update_reputation(
        self,
        profile: PowerBotReputationProfileModel,
        fair_participation_delta: int = 0,
        longevity_days_delta: int = 0,
        community_engagement_delta: int = 0,
        referrals_delta: int = 0,
        merchant_activity_delta: int = 0
    ) -> PowerBotReputationProfileModel:
        """
        Updates the non-financial reputation profile after verified domain actions.
        """
        profile.fair_participation_score += fair_participation_delta
        profile.account_longevity_days += longevity_days_delta
        profile.community_engagement_score += community_engagement_delta
        profile.referral_count += referrals_delta
        profile.merchant_activity_score += merchant_activity_delta
        
        # Calculate total reputation points
        total = (
            profile.fair_participation_score
            + (profile.account_longevity_days * 2)
            + profile.verified_identity_bonus
            + profile.community_engagement_score
            + (profile.referral_count * 25)
            + (profile.merchant_activity_score * 10)
        )
        profile.total_reputation_points = total
        profile.tier = self.compute_tier(total)
        profile.updated_at = datetime.now(timezone.utc)
        return profile

    def get_unlocked_experiences(self, profile: PowerBotReputationProfileModel) -> Dict[str, Any]:
        """
        Returns what non-financial features the user's tier has unlocked.
        Does NOT influence match odds or monetary payouts.
        """
        unlocked = {
            "user_id": profile.user_id,
            "reputation_tier": profile.tier,
            "total_reputation_points": profile.total_reputation_points,
            "can_create_private_leagues": True,
            "can_create_county_leagues": profile.total_reputation_points >= 500,
            "can_access_vip_ai_copilot_summaries": profile.total_reputation_points >= 1000,
            "can_qualify_for_national_prediction_council": profile.total_reputation_points >= 2500,
            "game_outcome_influence": "NONE (Exact match outcomes and odds are strictly governed by double-entry escrow and match settlement rules)"
        }
        return unlocked
