class ConsistencyScorer:
    name = "consistency"
    
    def score(self, claims: list[dict]) -> float:
        if not claims:
            return 0.0
        # Check for contradictions (simplified: penalize if both accepted and rejected for similar topics)
        statuses = [c.get("status", "") for c in claims]
        accepted = sum(1 for s in statuses if s == "accepted")
        rejected = sum(1 for s in statuses if s == "rejected")
        total = len(claims)
        # Higher score if most claims converge
        if total == 0:
            return 0.0
        dominant = max(accepted, rejected) / total
        return round(dominant, 3)
