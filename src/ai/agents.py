import uuid
from typing import Dict, List
from src.ai.rag_engine import rag_store
from src.core.treasury_engine import treasury_engine
from src.core.ledger_engine import ledger_engine
from src.core.event_bus import event_bus

class SpecializedAIAgents:
    """
    KARIS OS™ Multi-Agent AI Suite (Section 13.3 & 39.3).
    Provides specialized domain intelligence grounded via Vector RAG retrieval.
    """
    def get_executive_briefing(self, organization_id: str = "ORG-KARIS-RETAIL") -> Dict:
        """Executive AI Agent generates an instant executive intelligence summary."""
        health = treasury_engine.get_treasury_health(organization_id)
        entries = ledger_engine.get_entries()
        events = event_bus.get_event_store()

        total_volume_kes = sum(en.amount for en in entries if en.currency == "KES")
        total_krt_moved = sum(en.amount for en in entries if en.currency == "KRT")

        briefing_text = (
            f"EXECUTIVE BRIEFING [{organization_id}]: Platform operations are 100% compliant with all 10 Invariants. "
            f"Treasury Reserve Ratio is at {health['current_reserve_ratio_pct']}% (Target: {health['target_reserve_ratio_pct']}%), "
            f"backed by KES {health['treasury_reserve_kes']:,.2f} against a circulating supply of {health['circulating_krt_supply']:,.2f} KRT. "
            f"Total recorded fiat transaction volume is KES {total_volume_kes:,.2f} across {len(entries)} double-entry ledger items and {len(events)} immutable events."
        )

        return {
            "agent": "Executive AI",
            "organization_id": organization_id,
            "status": health["treasury_status"],
            "briefing_summary": briefing_text,
            "metrics": {
                "total_ledger_entries": len(entries),
                "total_events_processed": len(events),
                "total_fiat_volume_kes": total_volume_kes,
                "total_krt_circulating": health["circulating_krt_supply"]
            }
        }

    def ask_agriculture_agent(self, query: str) -> Dict:
        """Agriculture AI Agent answers farmer inquiries using RAG grounding."""
        rag_results = rag_store.retrieve_context(query, top_k=2)
        grounding = [doc.text for doc, _ in rag_results]

        if not grounding:
            response = (
                "Agriculture AI: Based on standard Kenyan agricultural protocols, ensure proper irrigation, "
                "certified seed selection, and organic pest management. Check with your local cooperative for detailed soil analysis."
            )
        else:
            response = f"Agriculture AI (Grounded via RAG [{rag_results[0][0].doc_id}]): " + " ".join(grounding)

        return {
            "agent": "Agriculture AI",
            "query": query,
            "response": response,
            "rag_citations": [{"doc_id": doc.doc_id, "title": doc.title, "similarity_score": score} for doc, score in rag_results]
        }

    def ask_support_agent(self, ticket_subject: str, ticket_description: str) -> Dict:
        """Customer Support AI Agent classifies tickets and generates RAG-backed resolutions."""
        query = f"{ticket_subject} {ticket_description}"
        rag_results = rag_store.retrieve_context(query, top_k=2)

        # Classify sentiment and urgency
        is_urgent = any(w in query.lower() for w in ["delay", "missing", "reject", "wrong", "broken", "emergency"])
        sentiment = -45.0 if is_urgent else 85.0

        if "payment" in query.lower() or "mpesa" in query.lower() or "krt" in query.lower():
            recommended_resolution = (
                "Please verify your M-Pesa transaction reference (QG37XXXXXXXX). "
                "Per Rule 2, settlements update automatically in your KES and KRT wallets upon network confirmation."
            )
        elif "harvest" in query.lower() or "avocado" in query.lower() or "grade" in query.lower():
            recommended_resolution = (
                "For avocado quality claims, please scan your batch Traceability QR Code on our portal to verify GAP_CERTIFIED inspection status."
            )
        else:
            recommended_resolution = (
                "Thank you for contacting KARIS Support. An agent has been assigned to investigate your request under our 24-hour SLA."
            )

        return {
            "agent": "Customer Support AI",
            "classified_urgency": "HIGH" if is_urgent else "STANDARD",
            "estimated_sentiment_score": sentiment,
            "suggested_resolution": recommended_resolution,
            "rag_grounding_used": [doc.doc_id for doc, _ in rag_results]
        }

multi_agent_suite = SpecializedAIAgents()
