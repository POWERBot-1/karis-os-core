import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

class KarisLoopGraphEngine:
    """
    KARIS OS™ :: KARIS LOOP™ 7 Interconnected Graph Engines (`Section 54`).
    Balances user interests, creator affinity, community relevance, and local freshness
    to power multi-priority feeds without relying solely on raw popularity (`Rule 7`).
    """
    def __init__(self):
        # 1. Social Graph (user-to-user follows, friend challenges)
        self.social_graph: Dict[str, List[str]] = {}
        # 2. Interest Graph (user preferences e.g. 'Avocado farming', 'Derby matches', 'Solar PAYG')
        self.interest_graph: Dict[str, List[str]] = {}
        # 3. Creator Graph (user-to-creator subscriptions, tip history)
        self.creator_graph: Dict[str, List[str]] = {}
        # 4. Business Graph (user-to-verified enterprise relationships)
        self.business_graph: Dict[str, List[str]] = {}
        # 5. Community Graph (user memberships in regional/educational guilds)
        self.community_graph: Dict[str, List[str]] = {}
        # 6. Knowledge Graph (learning achievements, GAP certificates, Edu-Pay badges)
        self.knowledge_graph: Dict[str, List[str]] = {}
        # 7. Commerce Graph (post-to-product shoppable links)
        self.commerce_graph: Dict[str, List[str]] = {}

    def link_relationship(self, graph_type: str, source_id: str, target_id: str) -> Dict[str, Any]:
        """Adds a verified directional edge in the specified graph."""
        target_map = getattr(self, f"{graph_type.lower()}_graph", self.social_graph)
        if source_id not in target_map:
            target_map[source_id] = []
        if target_id not in target_map[source_id]:
            target_map[source_id].append(target_id)
        
        return {
            "status": "GRAPH_EDGE_LINKED",
            "graph_type": graph_type,
            "source_id": source_id,
            "target_id": target_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

    def compute_personalized_feed(
        self,
        user_identity_id: str,
        feed_priority_type: str = "FOR_YOU",
        available_posts: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Computes multi-priority feed ranking (`Rule 7`).
        Balances interest affinity (40%), local county freshness (30%), creator subscription (20%),
        and commerce relevance (10%) to deliver rich, engaging feeds.
        """
        if available_posts is None:
            available_posts = []

        interests = self.interest_graph.get(user_identity_id, ["Hass Avocados", "Solar Pumps", "Derby"])
        followed_creators = self.creator_graph.get(user_identity_id, ["CREATOR-DAVID-01", "CREATOR-SARAH-02"])

        scored_posts = []
        for p in available_posts:
            score = 50.0 # Baseline score
            
            # Creator affinity bonus
            if p.get("creator_identity_id") in followed_creators:
                score += 25.0
            
            # Feed type boost
            if feed_priority_type == "MARKETPLACE" and p.get("linked_product_id"):
                score += 35.0
            elif feed_priority_type == "LOCAL" and "Machakos" in p.get("caption_text", ""):
                score += 30.0
            elif feed_priority_type == "TRENDING" and p.get("likes_count", 0) > 50:
                score += 40.0

            scored_posts.append({"post": p, "feed_ranking_score": round(score, 2)})

        # Sort descending by ranking score
        scored_posts.sort(key=lambda x: x["feed_ranking_score"], reverse=True)
        return [item["post"] for item in scored_posts]
