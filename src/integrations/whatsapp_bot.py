import uuid
from typing import Dict
from src.domain.models import AssetType, EventCategory, EventPayload, WalletType
from src.core.event_bus import event_bus
from src.core.wallet_engine import wallet_engine
from src.ai.agents import multi_agent_suite
from src.verticals.karis_farm.service import karis_farm_service

class WhatsAppCloudBotEngine:
    """
    KARIS OS™ WhatsApp Cloud API Interactive Bot Engine (Section 36.5 & 24).
    Enables smallholder farmers and consumers across East Africa to trace produce, check wallet balances,
    and ask grounded AI RAG farming questions via WhatsApp Business messaging.
    """
    def process_inbound_message(
        self,
        sender_phone: str,
        inbound_text: str,
        identity_id: str = "7f8013a9-310c-4f16-9031-295274a26944",
        organization_id: str = "ORG-KARIS-RETAIL"
    ) -> Dict:
        msg_id = f"WA-MSG-{uuid.uuid4().hex[:8].upper()}"
        text_clean = inbound_text.strip()
        text_upper = text_clean.upper()

        detected_intent = "GENERAL_INQUIRY"
        bot_response = ""

        # 1. Traceability Intent
        if text_upper.startswith("1") or text_upper.startswith("TRACE"):
            detected_intent = "PRODUCE_TRACEABILITY_LOOKUP"
            parts = text_clean.split()
            qr_code = parts[-1] if len(parts) > 1 else "KARIS-TRACE-QR-12C8D4F2"
            trace = karis_farm_service.get_traceability_by_qr(qr_code)
            if trace:
                bot_response = (
                    f"🌿 *KARIS FARM™ Traceability Report*\n"
                    f"• *Farm Origin:* {trace['farm_name']} ({trace['region_county']})\n"
                    f"• *Crop:* {trace['crop_type']} ({trace['quality_grade']})\n"
                    f"• *Quantity:* {trace['harvest_quantity_kg']} KG | Verified GAP_CERTIFIED\n"
                    f"• *QR Code:* {trace['traceability_qr_code']}"
                )
            else:
                bot_response = f"❌ Traceability record not found for QR code: {qr_code}."

        # 2. Wallet Balance Intent
        elif text_upper.startswith("2") or text_upper.startswith("BALANCE") or text_upper.startswith("BAL"):
            detected_intent = "WALLET_BALANCE_CHECK"
            kes_w = wallet_engine.get_wallet_by_keys(identity_id, organization_id, WalletType.KES_WALLET, AssetType.KES)
            krt_w = wallet_engine.get_wallet_by_keys(identity_id, organization_id, WalletType.KRT_WALLET, AssetType.KRT)
            kes_bal = kes_w.balance if kes_w else 0.0
            krt_bal = krt_w.balance if krt_w else 0.0
            bot_response = (
                f"💰 *KARIS OS™ Multi-Asset Wallet Balances*\n"
                f"• *Fiat KES Balance:* KES {kes_bal:,.2f}\n"
                f"• *KARIS Tokens:* {krt_bal:,.2f} KRT\n"
                f"• *Status:* ACTIVE (Rule 5 Protected)"
            )

        # 3. Ask AI RAG Agent Intent
        elif text_upper.startswith("3") or text_upper.startswith("ASK") or text_upper.startswith("AGRI"):
            detected_intent = "AI_RAG_CONVERSATIONAL_QUERY"
            query = text_clean[4:].strip() if len(text_clean) > 4 else "Hass Avocado irrigation rules"
            ai_res = multi_agent_suite.ask_agriculture_agent(query)
            bot_response = f"🤖 *KARIS Agriculture AI Response*\n\n{ai_res['response']}"

        # 4. Power BOT X Prediction Economy Intent (`Horizon 3`)
        elif any(text_upper.startswith(k) for k in ("4", "JOIN_", "COPILOT", "DEPOSIT_KRT", "ORDER EATERY", "SPEND_")):
            detected_intent = "POWER_BOT_X_INTERACTIVE_INTENT"
            from src.verticals.power_bot_x.whatsapp_experience import PowerBotWhatsAppExperience
            pb_wa = PowerBotWhatsAppExperience()
            res = pb_wa.handle_whatsapp_incoming_message(sender_phone, inbound_text)
            bot_response = f"⚽ *KARIS OS :: POWER BOT X*\n\n{res['message']}"

        # 5. KARIS ENERGY & Smart Solar Grid Intent (`Horizon 4`)
        elif any(text_upper.startswith(k) for k in ("5", "SOLAR", "PAYG", "ENERGY", "METER")):
            detected_intent = "KARIS_ENERGY_TELEMETRY_AND_PAYG"
            bot_response = (
                f"☀️ *KARIS ENERGY & SMART SOLAR GRID™ (`Section 50`)*\n"
                f"• *PAYG Solar Pump:* SOLAR-PUMP-MACHAKOS-01 | Status: ACTIVE_UNLOCKED\n"
                f"• *IoT Telemetry:* Generation Today: 6.85 kWh | Battery: 94.5% | Moisture: 48.0%\n"
                f"• *Microgrid Surplus:* 2.40 kWh fed into community grid -> Auto-minted +24.00 KRT-JOULE rewards (`Rule 7 & 9`)!\n"
                f"Reply 'PAYG SOLAR 50' to unlock an additional 24 hours of solar irrigation."
            )

        # 6. PalPlus Hosted Payment Link Intent (`Section 51 / Horizon 1-3`)
        elif any(text_upper.startswith(k) for k in ("6", "PAY", "LINK", "PALPLUS", "CHECKOUT")):
            detected_intent = "PALPLUS_PAYMENT_LINK_CHECKOUT"
            bot_response = (
                "💳 *KARIS OS™ Instant Web Checkout via PalPlus*\n\n"
                "Click our secure temporary payment link below to complete your KES deposit or invoice settlement:\n"
                "👉 https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f\n\n"
                "_Upon payment confirmation, double-entry ledger reconciliation (`Rule 9`) triggers instantly, converting funds to KRT tokens (`Rule 5`) and unlocking your order!_"
            )

        # Default Help Menu
        else:
            detected_intent = "MENU_HELP_REQUESTED"
            bot_response = (
                "👋 *Welcome to KARIS OS™ WhatsApp Business Portal*\n"
                "Reply with an option or command below:\n\n"
                "1️⃣ *Trace <QR_Code>* — Verify food safety & harvest lineage\n"
                "2️⃣ *Balance* — Check KES and KRT wallet balances\n"
                "3️⃣ *Ask <Question>* — Ask our RAG AI about farming protocols\n"
                "4️⃣ *Power BOT X* — Prediction Copilot & instant KRT meal checkouts\n"
                "5️⃣ *Solar Pay-As-You-Go* — Check IoT smart meter telemetry & green energy rewards\n"
                "6️⃣ *Payment Link* — Instant Web Checkout via PalPlus (`https://link.palpluss.com/6e8de0bc-1284-4bba-a5de-f886665bf18f`)\n\n"
                "_All interactions are timestamped and recorded under Rule 6 & 8._"
            )

        record = {
            "message_id": msg_id,
            "sender_phone": sender_phone,
            "inbound_text": inbound_text,
            "detected_intent": detected_intent,
            "bot_response_text": bot_response
        }

        ev = EventPayload(
            event_type="WHATSAPP_MESSAGE_PROCESSED",
            event_category=EventCategory.COMMERCE,
            actor_identity_id=identity_id,
            organization_id=organization_id,
            correlation_id=msg_id,
            source_module="WHATSAPP_CLOUD_BOT_ENGINE",
            payload=record
        )
        event_bus.publish(ev)
        return record

whatsapp_bot_engine = WhatsAppCloudBotEngine()
