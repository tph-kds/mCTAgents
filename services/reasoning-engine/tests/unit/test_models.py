"""Tests for CCSR protocol Pydantic models."""

import pytest
from pydantic import ValidationError
from mctagents.core.protocol import (
    Claim,
    ClaimScores,
    ClaimStatus,
    ClaimType,
    Decision,
    Event,
    EventType,
    Evidence,
    EvidenceStatus,
    FinalAnswer,
    Objection,
    ProblemFrame,
    Revision,
    RevisionType,
    RiskItem,
    Severity,
    SourceType,
)


class TestClaim:
    def test_minimal_claim(self):
        claim = Claim(
            id="c1", run_id="r1", author_agent_id="architect", text="test"
        )
        assert claim.id == "c1"
        assert claim.confidence == 0.5
        assert claim.status == ClaimStatus.PROPOSED

    def test_full_claim(self):
        claim = Claim(
            id="c1", run_id="r1", author_agent_id="architect",
            text="test", claim_type=ClaimType.ARCHITECTURE_DECISION,
            confidence=0.8, status=ClaimStatus.ACCEPTED,
            requires_evidence=True, evidence_status=EvidenceStatus.SUPPORTED,
            scores=ClaimScores(logic=0.9, evidence=0.8, final=0.85),
        )
        assert claim.claim_type == ClaimType.ARCHITECTURE_DECISION
        assert claim.scores.logic == 0.9

    def test_confidence_bounds(self):
        Claim(id="c1", run_id="r1", author_agent_id="a", text="t", confidence=0.0)
        Claim(id="c1", run_id="r1", author_agent_id="a", text="t", confidence=1.0)
        with pytest.raises(ValidationError):
            Claim(id="c1", run_id="r1", author_agent_id="a", text="t", confidence=1.5)
        with pytest.raises(ValidationError):
            Claim(id="c1", run_id="r1", author_agent_id="a", text="t", confidence=-0.1)

    def test_claim_scores_bounds(self):
        ClaimScores(logic=0.0, evidence=0.0, feasibility=0.0,
                     critic_resistance=0.0, risk_adjusted=0.0, final=0.0)
        ClaimScores(logic=1.0, evidence=1.0, feasibility=1.0,
                     critic_resistance=1.0, risk_adjusted=1.0, final=1.0)
        with pytest.raises(ValidationError):
            ClaimScores(logic=1.5)


class TestEvidence:
    def test_minimal_evidence(self):
        ev = Evidence(
            id="e1", run_id="r1", source_type=SourceType.UPLOADED_DOCUMENT,
            source_ref="doc.pdf", summary="test evidence",
        )
        assert ev.reliability_score == 0.5
        assert ev.supports_claim_ids == []

    def test_full_evidence(self):
        ev = Evidence(
            id="e1", run_id="r1", source_type=SourceType.WEB_SOURCE,
            source_ref="wiki", summary="test",
            reliability_score=0.9,
            supports_claim_ids=["c1"], attacks_claim_ids=["c2"],
        )
        assert ev.reliability_score == 0.9


class TestObjection:
    def test_minimal_objection(self):
        obj = Objection(
            id="o1", run_id="r1", target_claim_id="c1",
            author_agent_id="critic", reason="weak evidence",
        )
        assert obj.severity == Severity.MEDIUM


class TestRevision:
    def test_minimal_revision(self):
        rev = Revision(
            id="rev1", run_id="r1", old_claim_id="c1",
            new_claim_id="c2", reason="improved",
        )
        assert rev.revision_type == RevisionType.OBJECTION_DRIVEN

    def test_revision_with_improvement(self):
        rev = Revision(
            id="rev1", run_id="r1", old_claim_id="c1",
            new_claim_id="c2", reason="improved", improvement_score=0.3,
        )
        assert rev.improvement_score == 0.3


class TestDecision:
    def test_minimal_decision(self):
        dec = Decision(
            id="d1", run_id="r1",
            accepted_claim_ids=["c1"],
            rejected_claim_ids=["c2"],
            uncertain_claim_ids=[],
            score_breakdown={},
            confidence=0.8,
        )
        assert dec.needs_more_debate is False


class TestFinalAnswer:
    def test_minimal_final_answer(self):
        fa = FinalAnswer(
            id="fa1", run_id="r1", answer_text="answer",
        )
        assert fa.accepted_claim_ids == []
        assert fa.risks == []

    def test_final_answer_with_risks(self):
        fa = FinalAnswer(
            id="fa1", run_id="r1", answer_text="answer",
            risks=[RiskItem(description="risk1", severity="high")],
        )
        assert len(fa.risks) == 1
        assert fa.risks[0].severity == "high"


class TestProblemFrame:
    def test_minimal_problem_frame(self):
        pf = ProblemFrame(
            id="pf1", run_id="r1", original_input="test problem",
            normalized_problem="test problem",
        )
        assert pf.risk_level == "medium"

    def test_full_problem_frame(self):
        pf = ProblemFrame(
            id="pf1", run_id="r1", original_input="test",
            normalized_problem="test",
            domain="architecture",
            requires_business_decision=True,
            requires_research=True,
        )
        assert pf.domain == "architecture"


class TestAgentResult:
    def test_agent_result_has_thinking_steps(self):
        from mctagents.agents.base import AgentResult
        from mctagents.core.protocol.thinking_step import ThinkingStep

        result = AgentResult(
            agent_id="test_agent",
            thinking_steps=[
                ThinkingStep(step_type="reasoning", content="thinking...", agent_id="test_agent"),
            ],
        )
        assert len(result.thinking_steps) == 1
        assert result.thinking_steps[0].content == "thinking..."

    def test_agent_result_empty_thinking_steps(self):
        from mctagents.agents.base import AgentResult

        result = AgentResult(agent_id="test_agent")
        assert result.thinking_steps == []


class TestEvent:
    def test_minimal_event(self):
        ev = Event(
            id="evt1", event_id="evt_001", run_id="r1",
            sequence=1, type=EventType.RUN_STARTED,
            payload={"problem": "test"},
        )
        assert ev.type == EventType.RUN_STARTED

    def test_event_with_agent_id(self):
        ev = Event(
            id="evt1", event_id="evt_001", run_id="r1",
            sequence=1, type=EventType.AGENT_STARTED,
            agent_id="architect", payload={"phase": "framing"},
        )
        assert ev.agent_id == "architect"
