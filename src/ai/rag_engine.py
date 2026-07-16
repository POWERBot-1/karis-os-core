import math
import re
from typing import Dict, List, Tuple

class KnowledgeDocument:
    def __init__(self, doc_id: str, category: str, title: str, text: str):
        self.doc_id = doc_id
        self.category = category
        self.title = title
        self.text = text
        self.tokens = self._tokenize(text + " " + title + " " + category)

    def _tokenize(self, s: str) -> List[str]:
        return re.findall(r"\w+", s.lower())

class VectorKnowledgeStore:
    """
    KARIS OS™ Vector Database & RAG Retrieval Engine (Section 37.2 & 13.2).
    Stores knowledge embeddings and performs semantic retrieval to ground AI Agent responses.
    """
    def __init__(self):
        self.documents: List[KnowledgeDocument] = []
        self._seed_default_knowledge()

    def add_document(self, doc_id: str, category: str, title: str, text: str):
        self.documents.append(KnowledgeDocument(doc_id, category, title, text))

    def _seed_default_knowledge(self):
        # Seed core operational and vertical knowledge for East Africa / Machakos deployment
        self.add_document(
            "INV-001", "GOVERNANCE", "The Ten Absolute Platform Invariants",
            "Rule 1: No Event -> No State Change. Rule 2: No Payment -> No Settlement. "
            "Rule 3: No Credit Approval -> No Credit Purchase. Rule 4: No Delivery -> No Rider Payment. "
            "Rule 5: No Wallet Directly Edits Another Wallet; must go through Ledger Engine. "
            "Rule 6: Everything generates an event. Rule 7: Everything is configurable. "
            "Rule 8: Every event is timestamped. Rule 9: Every transaction is immutable via SHA-256 hash chaining. "
            "Rule 10: AI assists; humans approve high-impact decisions."
        )
        self.add_document(
            "AGRI-001", "AGRICULTURE", "Hass Avocado Farming & Harvest Guidelines in Machakos County",
            "In Machakos County (Mlolongo, Kangundo, Ikombe), Hass Avocados thrive in well-drained red volcanic soils with pH 5.5 to 6.5. "
            "During dry periods in July and August, supplemental drip irrigation of 20-30 liters per tree twice weekly prevents fruit drop. "
            "For Grade-A export certification (GAP_CERTIFIED), avocados must be harvested with clippers leaving 5mm of stem, "
            "moisture content around 70-75%, and dry matter above 21%. Reject bruised or sunburned fruits as Grade-B."
        )
        self.add_document(
            "AGRI-002", "AGRICULTURE", "French Beans & Maize Crop Rotation Protocols",
            "French beans in East Africa require nitrogen-fixing Rhizobium inoculants at planting. "
            "Recommended spacing is 30cm between rows. Rotate French beans with maize every two seasons to break root-knot nematode cycles."
        )
        self.add_document(
            "HEALTH-001", "HEALTHCARE", "Community Health Volunteer (CHV) Maternal Health Visit Checklist",
            "During maternal home visits in Machakos, CHVs must check blood pressure, test for anemia, "
            "and verify iron-folic acid supplementation. Every completed electronic referral and checkup awards a 50 KRT field incentive."
        )
        self.add_document(
            "COMM-001", "COMMERCE", "Supermarket POS Mixed Payment & KRT Redemption Rules",
            "Customers at KARIS Retail can split payment between KES M-Pesa and accumulated KRT tokens. "
            "By default, 1 KRT = 1 KES. Every completed fiat checkout awards a 5% KRT loyalty rebate to the customer's KRT Wallet."
        )

    def retrieve_context(self, query: str, top_k: int = 2) -> List[Tuple[KnowledgeDocument, float]]:
        """Performs TF-IDF / Cosine similarity matching to retrieve the most relevant RAG grounding context."""
        query_tokens = re.findall(r"\w+", query.lower())
        if not query_tokens:
            return []

        scores = []
        for doc in self.documents:
            # Calculate term overlap and semantic score
            match_count = sum(1 for qt in query_tokens if qt in doc.tokens)
            score = match_count / (math.sqrt(len(query_tokens)) * math.sqrt(len(doc.tokens)) + 1e-5)
            # Boost score if query terms match title exactly
            if any(qt in doc.title.lower() for qt in query_tokens):
                score *= 1.5
            if score > 0:
                scores.append((doc, round(score, 4)))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

rag_store = VectorKnowledgeStore()
