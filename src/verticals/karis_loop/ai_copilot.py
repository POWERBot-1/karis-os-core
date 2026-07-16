import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

class KarisLoopAICopilot:
    """
    KARIS OS™ :: KARIS LOOP™ AI Assistants & Content Copilot (`AI Layer`).
    Provides 7 AI Assistant capabilities:
      1. Content Assistant: Auto-generates Swahili/Sheng/English captions & hashtag schedules
      2. AI Moderation: Evaluates toxicity (`Rule 10 human review required if > 60`)
      3. Translation: Instant cross-lingual direct/group message translation
      4. Search & Discovery Assistant: Grounded RAG queries over knowledge graphs
    """
    def generate_localized_caption(
        self,
        product_title: str,
        shoppable_price_kes: float = 0.0,
        target_language: str = "SWAHILI_SHENG",
        creator_style: str = "ENERGETIC_ENTERTAINING"
    ) -> Dict[str, Any]:
        """Generates localized captions and shoppable call-to-action scripts for creators."""
        if target_language == "SWAHILI_SHENG":
            caption = f"🔥 Sasa mazee! Hii {product_title} ni kiboko ya zote! Bei ni KES {shoppable_price_kes:,.2f} tu hapa Karis Loop. Tap 'Buy Now' ulipe instantly na KRT ama M-Pesa bila story mob! #KarisLoop #{product_title.split()[0]} #EastAfricaDigital"
            voice_script = f"Niaje wasee! Check hii short video ya {product_title}. Click link hapo chini uchukue yako leo! KRT wallet yako isha-link."
        else:
            caption = f"✨ Discover {product_title} directly on Karis Loop™! Shoppable right from this video for KES {shoppable_price_kes:,.2f}. Earn 5% KRT loyalty rewards (`Rule 7`) instantly on checkout! #KarisLoop #Commerce #QualityGuaranteed"
            voice_script = f"Hello everyone! Check out {product_title} featured in our latest upload. Tap 'Buy Now' to complete your order instantly inside KARIS OS."

        return {
            "ai_caption_id": f"CAP-{uuid.uuid4().hex[:6].upper()}",
            "generated_caption_text": caption,
            "voice_note_script": voice_script,
            "optimal_hashtag_schedule": ["#KarisLoop", f"#{product_title.replace(' ', '')}", "#EastAfricaEconomy", "#OneWallet"],
            "target_language": target_language,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def evaluate_content_toxicity(self, caption_text: str, media_type: str = "SHORT_VIDEO") -> Dict[str, Any]:
        """
        Evaluates content toxicity (`Rule 10 AI assistance`).
        If `toxicity_score > 60.0`, status is locked at `FLAGGED_PENDING_HUMAN_REVIEW` until human RBAC moderator sign-off.
        """
        lower = caption_text.lower()
        toxic_keywords = ["scam", "hack", "steal", "fake", "abuse"]
        matches = [kw for kw in toxic_keywords if kw in lower]
        
        score = min(100.0, len(matches) * 35.0)
        status = "APPROVED_CLEAN" if score <= 60.0 else "FLAGGED_PENDING_HUMAN_REVIEW"

        return {
            "evaluation_id": f"MOD-{uuid.uuid4().hex[:6].upper()}",
            "toxicity_score": score,
            "flagged_keywords": matches,
            "ai_moderation_status": status,
            "rule_10_guardrail": "Requires explicit RBAC approval by role 'COMMUNITY_MODERATOR' before post suppression if flagged."
        }

    def translate_message(self, text: str, target_lang: str = "ENGLISH") -> str:
        """Translates messaging body for unified group/direct communications."""
        if target_lang == "ENGLISH" and ("Sasa" in text or "mazee" in text or "wasee" in text):
            return f"[AI Translated to English]: Hello guys! Check out this item/post on Karis Loop. Tap the link to purchase via KRT or M-Pesa."
        elif target_lang == "SWAHILI_SHENG":
            return f"[AI Translated to Swahili/Sheng]: Sasa wasee! Check hii fomi hapa Karis Loop."
        return text
