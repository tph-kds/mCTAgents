class CompletenessScorer:
    name = "completeness"
    
    def score(self, claims: list[dict]) -> float:
        if not claims:
            return 0.0
        # Score based on number of claims, types covered, and evidence status
        total = len(claims)
        supported = sum(1 for c in claims if c.get("evidence_status") == "supported")
        covered_types = len(set(c.get("claim_type", "") for c in claims))
        type_coverage = min(covered_types / 4, 1.0)  # 4+ types is full coverage
        support_rate = supported / total if total > 0 else 0
        return round(0.4 * type_coverage + 0.6 * support_rate, 3)
