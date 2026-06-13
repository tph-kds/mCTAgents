"""Evidence reliability scoring based on source authority and quality signals."""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


class EvidenceReliabilityScorer:
    """Scores evidence reliability using weighted multi-signal assessment.

    Signals:
        - source_authority: How authoritative the source type is.
        - recency: How recent the evidence is.
        - specificity: How specific and on-topic the evidence is.
        - independence: How independent the source is.
        - retrieval_confidence: Confidence in the retrieval quality.
    """

    AUTHORITY_MAP: dict[str, float] = {
        "official_documentation": 0.9,
        "academic_paper": 0.85,
        "github_repository": 0.8,
        "uploaded_document": 0.7,
        "web_source": 0.6,
        "code_execution_result": 0.75,
        "database_result": 0.7,
        "internal_memory": 0.5,
        "human_confirmation": 0.65,
        "benchmark_result": 0.8,
    }

    WEIGHTS: dict[str, float] = {
        "source_authority": 0.25,
        "recency": 0.15,
        "specificity": 0.25,
        "independence": 0.15,
        "retrieval_confidence": 0.20,
    }

    def score(self, evidence_item: dict) -> float:
        """Compute an overall reliability score for an evidence item.

        Args:
            evidence_item: Dict containing evidence metadata. Expected keys:
                - source_type (str): The type of source.
                - recency (float, optional): Recency score 0-1.
                - specificity (float, optional): Specificity score 0-1.
                - independence (float, optional): Independence score 0-1.
                - retrieval_score (float, optional): Retrieval confidence 0-1.

        Returns:
            Overall reliability score between 0.0 and 1.0.
        """
        source_type = evidence_item.get("source_type", "")
        signals = {
            "source_authority": self.AUTHORITY_MAP.get(source_type, 0.5),
            "recency": float(evidence_item.get("recency", 0.7)),
            "specificity": float(evidence_item.get("specificity", 0.7)),
            "independence": float(evidence_item.get("independence", 0.7)),
            "retrieval_confidence": float(
                evidence_item.get("retrieval_score", 0.5),
            ),
        }

        overall = sum(
            signals[key] * self.WEIGHTS[key] for key in signals
        )
        overall = round(min(1.0, max(0.0, overall)), 3)

        logger.debug(
            "evidence_scored",
            source_type=source_type,
            signals=signals,
            overall=overall,
        )

        return overall

    def score_from_retrieval(
        self,
        source_type: str,
        retrieval_score: float,
        recency: float = 0.7,
        specificity: float = 0.7,
        independence: float = 0.7,
    ) -> float:
        """Convenience method for scoring from individual parameters.

        Args:
            source_type: The type of source.
            retrieval_score: Vector similarity score from retrieval.
            recency: Recency score 0-1.
            specificity: Specificity score 0-1.
            independence: Independence score 0-1.

        Returns:
            Overall reliability score between 0.0 and 1.0.
        """
        return self.score(
            {
                "source_type": source_type,
                "retrieval_score": retrieval_score,
                "recency": recency,
                "specificity": specificity,
                "independence": independence,
            },
        )
