import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from src.domain.models import PowerBotFixtureModel

class PowerBotWhatsAppExperience:
    """
    KARIS OS™ :: POWER BOT X WhatsApp-First Experience Engine (`Experience Layer`).
    
    WhatsApp is the primary operating environment. The AI automatically creates:
    - Status posters
    - Animated status videos
    - Countdown timers
    - Match cards
    - Community polls
    - Referral cards
    - QR codes
    - Deep links
    - Voice notes
    - Daily summaries
    
    Users discover the platform via WhatsApp status/deep links and every interaction
    returns to WhatsApp with localized Swahili/Sheng/English content.
    """
    def __init__(self):
        self.bot_phone_number = "254700000000"

    def generate_whatsapp_status_package(
        self,
        fixture: PowerBotFixtureModel,
        agent_user_id: str,
        preferred_language: str = "SWAHILI_SHENG"
    ) -> Dict[str, Any]:
        """
        Generates a complete WhatsApp Status marketing kit for an agent or user to post.
        """
        team_a, _, team_b = fixture.title.partition(" vs ") if " vs " in fixture.title else (fixture.title, "", "Opponent")
        qr_deep_link = f"https://wa.me/{self.bot_phone_number}?text=JOIN_{agent_user_id}_{fixture.fixture_id}"
        
        if preferred_language == "SWAHILI_SHENG":
            caption = f"🔥 {team_a} vs {team_b} hapa Power BOT X! KRT yako iko ready? Check AI Copilot form na uweke prediction bila kubahatisha. Click link ama QR code tuanze! #PowerBotX #{team_a}"
            audio_script = f"Sasa buda! Komaa na Power BOT X. Hii mechi ya {team_a} na {team_b} ni moto. AI yetu imeshachora tactical breakdown yote kwa WhatsApp!"
        else:
            caption = f"⚽ Derby Countdown: {team_a} vs {team_b}! Use the Power BOT X AI Copilot to check form and confidence intervals before making your KRT prediction on WhatsApp! #DerbyDay"
            audio_script = f"Hello football fans! Get ready for {team_a} vs {team_b}. Check out the Power BOT X AI Copilot right here on WhatsApp to analyze player injuries and form before submitting your prediction."

        package = {
            "package_id": f"WA-STATUS-{uuid.uuid4().hex[:8]}",
            "agent_user_id": agent_user_id,
            "fixture_id": fixture.fixture_id,
            "target_channel": "WHATSAPP_STATUS",
            "language": preferred_language,
            "status_poster_image_url": f"/portal/assets/posters/{fixture.fixture_id}_status.png",
            "animated_status_video_metadata": {
                "duration_sec": 15,
                "aspect_ratio": "9:16",
                "animation_style": "EAST_AFRICAN_GOLD_PULSE",
                "video_url": f"/portal/assets/videos/{fixture.fixture_id}_animated.mp4"
            },
            "countdown_timer_sec": int((fixture.start_time_utc - datetime.now(timezone.utc)).total_seconds()),
            "match_card": {
                "team_a": team_a,
                "team_b": team_b,
                "start_time_utc": fixture.start_time_utc.isoformat(),
                "category": fixture.category
            },
            "community_poll": {
                "question": f"Who takes the 3 points in {team_a} vs {team_b}?",
                "options": [f"1. {team_a} Win", "2. Draw", f"3. {team_b} Win"]
            },
            "referral_card": {
                "headline": f"Join {agent_user_id}'s Prediction League on Power BOT X!",
                "bonus_offer": "Get 50 KRT Welcome Bonus on first deposit via M-Pesa."
            },
            "qr_code_svg_payload": f"<svg viewBox='0 0 100 100'><rect width='100' height='100' fill='white'/><text x='10' y='50' font-size='8'>QR: {qr_deep_link}</text></svg>",
            "deep_link": qr_deep_link,
            "voice_note_script": audio_script,
            "daily_summary": f"📊 Daily Power BOT X Summary: 420 active predictions across 14 East African fixtures. Top County: Machakos with 18,500 KRT volume!",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        return package

    def handle_whatsapp_incoming_message(self, phone_number: str, message_text: str) -> Dict[str, Any]:
        """
        Handles incoming WhatsApp bot commands (`JOIN_<agent>_<fixture>`, `COPILOT`, `DEPOSIT`, `SPEND_EATERY`).
        """
        text_clean = message_text.strip().upper()
        
        if text_clean.startswith("JOIN_"):
            parts = text_clean.split("_")
            agent_ref = parts[1] if len(parts) > 1 else "DIRECT"
            fixture_id = parts[2] if len(parts) > 2 else "LATEST"
            return {
                "reply_type": "WELCOME_JOIN",
                "message": f"🎉 Welcome to Power BOT X on WhatsApp! Referred by Agent {agent_ref}. Your account is linked to One Identity across KARIS OS. Reply '1' to deposit KES via M-Pesa or '2' to view AI Copilot analysis for fixture {fixture_id}.",
                "agent_attribution": agent_ref
            }
        elif text_clean in ("1", "DEPOSIT"):
            return {
                "reply_type": "MPESA_DEPOSIT_PROMPT",
                "message": "💰 To deposit and mint KRT:\n👉 Instant Web Checkout: Click our secure temporary payment link:\nhttps://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f\n\nOr use M-Pesa Paybill: 888880 | Account: POWERBOT\nYour deposit will convert instantly to KRT (1 KES = 1 KRT)."
            }
        elif text_clean in ("2", "COPILOT"):
            return {
                "reply_type": "COPILOT_SUMMARY",
                "message": "🧠 AI Prediction Copilot:\nGor Mahia vs AFC Leopards\n• Form: Gor Mahia unbeaten in 4; AFC Leopards 3-game away win streak.\n• Note: High second-half fatigue expected due to continental fixtures.\n• Confidence: High intensity derby (Derby uncertainty band).\nReply 'PREDICT GOR' or 'PREDICT AFC' alongside KRT stake to enter!"
            }
        elif text_clean.startswith("SPEND_"):
            return {
                "reply_type": "MERCHANT_GATEWAY",
                "message": "🍔 Digital Economy Marketplace Gateway:\nYou have 450 KRT winnings in your KARIS OS wallet! Reply 'ORDER EATERY 300' to instantly pay KES 300 equivalent for a hot meal at KARIS Eatery, or 'ORDER FARM 150' for fresh avocado delivery!"
            }
        else:
            return {
                "reply_type": "MENU_HELP",
                "message": "🤖 KARIS OS :: Power BOT X WhatsApp Copilot\nReply with a command:\n1 - Deposit M-Pesa -> Get KRT\n2 - AI Copilot Match Form & Stats\n3 - My Prediction Leagues & Reputation\n4 - Spend KRT Winnings at KARIS Eatery / FARM\n5 - Agent Marketing Kit Generator"
            }
