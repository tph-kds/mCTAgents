"""Tests for the evidence reliability scorer."""

import pytest

from mctagents.scoring.reliability import EvidenceReliabilityScorer


@pytest.fixture
def scorer():
    return EvidenceReliabilityScorer()


class TestEvidenceReliabilityScorer:
    def test_score_with_high_retrieval(self, scorer):
        score = scorer.score_from_retrieval(
            source_type="uploaded_document",
            retrieval_score=0.95,
        )
        assert 0.0 <= score <= 1.0
        assert score > 0.5

    def test_score_with_low_retrieval(self, scorer):
        score = scorer.score_from_retrieval(
            source_type="uploaded_document",
            retrieval_score=0.2,
        )
        assert 0.0 <= score <= 1.0
        assert score < 0.5

    def test_score_full_evidence_item(self, scorer):
        item = {
            "source_type": "uploaded_document",
            "retrieval_score": 0.9,
            "author": "test_author",
        }
        score = scorer.score(item)
        assert 0.0 <= score <= 1.0

    def test_score_empty_evidence_item(self, scorer):
        score = scorer.score({})
        assert 0.0 <= score <= 1.0
