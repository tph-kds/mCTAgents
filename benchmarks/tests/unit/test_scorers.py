"""Tests for benchmark scorers."""

import pytest
from benchmarks.scorers.completeness import CompletenessScorer
from benchmarks.scorers.consistency import ConsistencyScorer
from benchmarks.scorers.evidence_quality import EvidenceQualityScorer


class TestCompletenessScorer:
    def test_empty_claims(self):
        scorer = CompletenessScorer()
        score = scorer.score([])
        assert 0.0 <= score <= 1.0

    def test_single_claim(self):
        scorer = CompletenessScorer()
        claims = [{"text": "test claim", "status": "accepted", "confidence": 0.8}]
        score = scorer.score(claims)
        assert 0.0 <= score <= 1.0

    def test_multiple_claims(self):
        scorer = CompletenessScorer()
        claims = [
            {"text": "claim 1", "status": "accepted", "confidence": 0.9},
            {"text": "claim 2", "status": "rejected", "confidence": 0.3},
            {"text": "claim 3", "status": "uncertain", "confidence": 0.5},
        ]
        score = scorer.score(claims)
        assert 0.0 <= score <= 1.0


class TestConsistencyScorer:
    def test_empty_claims(self):
        scorer = ConsistencyScorer()
        score = scorer.score([])
        assert 0.0 <= score <= 1.0

    def test_all_accepted(self):
        scorer = ConsistencyScorer()
        claims = [
            {"status": "accepted", "confidence": 0.9},
            {"status": "accepted", "confidence": 0.8},
        ]
        score = scorer.score(claims)
        assert 0.0 <= score <= 1.0

    def test_mixed_statuses(self):
        scorer = ConsistencyScorer()
        claims = [
            {"status": "accepted", "confidence": 0.9},
            {"status": "rejected", "confidence": 0.3},
        ]
        score = scorer.score(claims)
        assert 0.0 <= score <= 1.0


class TestEvidenceQualityScorer:
    def test_empty_claims(self):
        scorer = EvidenceQualityScorer()
        score = scorer.score([])
        assert 0.0 <= score <= 1.0

    def test_claims_with_evidence(self):
        scorer = EvidenceQualityScorer()
        claims = [
            {"status": "accepted", "confidence": 0.8, "requires_evidence": True, "evidence_status": "supported"},
        ]
        score = scorer.score(claims)
        assert 0.0 <= score <= 1.0

    def test_claims_without_evidence(self):
        scorer = EvidenceQualityScorer()
        claims = [
            {"status": "accepted", "confidence": 0.8, "requires_evidence": True, "evidence_status": "unsupported"},
        ]
        score = scorer.score(claims)
        assert 0.0 <= score <= 1.0
