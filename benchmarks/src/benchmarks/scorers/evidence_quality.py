class EvidenceQualityScorer:
    name = "evidence"
    
    def score(self, claims: list[dict]) -> float:
        if not claims:
            return 0.0
        evidence_claims = [c for c in claims if c.get("requires_evidence")]
        if not evidence_claims:
            return 0.7  # No claims needed evidence
        supported = sum(1 for c in evidence_claims if c.get("evidence_status") == "supported")
        return round(supported / len(evidence_claims), 3) if evidence_claims else 0.7
