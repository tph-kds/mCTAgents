"""Tests for CCSR protocol invariants."""

import pytest
from mctagents.core.protocol import (
    Claim,
    ClaimStatus,
    FinalAnswer,
    RiskItem,
    Revision,
)
from mctagents.core.protocol.invariants import (
    validate_all_invariants,
    validate_claim_has_unique_id,
    validate_final_answer_declares_risks,
    validate_final_answer_references_accepted_claims,
    validate_high_confidence_claims_have_evidence,
    validate_rejected_claims_have_reason,
    validate_revisions_link_claims,
)


def _make_claim(
    claim_id: str = "c1",
    confidence: float = 0.5,
    status: str = "proposed",
    requires_evidence: bool = False,
    evidence_status: str = "unsupported",
    rejection_reason: str | None = None,
) -> Claim:
    return Claim(
        id=claim_id,
        run_id="r1",
        author_agent_id="architect",
        text="test claim",
        confidence=confidence,
        status=status,
        requires_evidence=requires_evidence,
        evidence_status=evidence_status,
        rejection_reason=rejection_reason,
    )


def _make_revision(
    rev_id: str = "rev1",
    old_claim_id: str = "c1",
    new_claim_id: str = "c2",
) -> Revision:
    return Revision(
        id=rev_id,
        run_id="r1",
        old_claim_id=old_claim_id,
        new_claim_id=new_claim_id,
        reason=" improved reasoning",
    )


def _make_final_answer(
    answer_id: str = "fa1",
    accepted_claim_ids: list[str] | None = None,
    risks: list[RiskItem] | None = None,
) -> FinalAnswer:
    return FinalAnswer(
        id=answer_id,
        run_id="r1",
        answer_text="final answer",
        accepted_claim_ids=accepted_claim_ids or [],
        risks=risks or [],
    )


class TestFinalAnswerReferencesAcceptedClaims:
    def test_valid_references(self):
        claims = [_make_claim("c1", status="accepted")]
        fa = _make_final_answer(accepted_claim_ids=["c1"])
        errors = validate_final_answer_references_accepted_claims(fa, claims)
        assert errors == []

    def test_references_non_accepted_claim(self):
        claims = [_make_claim("c1", status="proposed")]
        fa = _make_final_answer(accepted_claim_ids=["c1"])
        errors = validate_final_answer_references_accepted_claims(fa, claims)
        assert len(errors) == 1
        assert "c1" in errors[0]

    def test_references_nonexistent_claim(self):
        fa = _make_final_answer(accepted_claim_ids=["nonexistent"])
        errors = validate_final_answer_references_accepted_claims(fa, [])
        assert len(errors) == 1


class TestHighConfidenceClaimsHaveEvidence:
    def test_low_confidence_no_evidence_ok(self):
        claims = [_make_claim("c1", confidence=0.3, requires_evidence=True)]
        errors = validate_high_confidence_claims_have_evidence(claims)
        assert errors == []

    def test_high_confidence_no_evidence_fails(self):
        claims = [_make_claim(
            "c1", confidence=0.8, requires_evidence=True,
            evidence_status="unsupported",
        )]
        errors = validate_high_confidence_claims_have_evidence(claims)
        assert len(errors) == 1
        assert "c1" in errors[0]

    def test_high_confidence_with_evidence_ok(self):
        claims = [_make_claim(
            "c1", confidence=0.8, requires_evidence=True,
            evidence_status="supported",
        )]
        errors = validate_high_confidence_claims_have_evidence(claims)
        assert errors == []

    def test_high_confidence_uncertain_status_ok(self):
        claims = [_make_claim(
            "c1", confidence=0.8, requires_evidence=True,
            evidence_status="unsupported", status="uncertain",
        )]
        errors = validate_high_confidence_claims_have_evidence(claims)
        assert errors == []


class TestRejectedClaimsHaveReason:
    def test_rejected_with_reason_ok(self):
        claims = [_make_claim("c1", status="rejected", rejection_reason="weak evidence")]
        errors = validate_rejected_claims_have_reason(claims)
        assert errors == []

    def test_rejected_without_reason_fails(self):
        claims = [_make_claim("c1", status="rejected")]
        errors = validate_rejected_claims_have_reason(claims)
        assert len(errors) == 1

    def test_accepted_without_reason_ok(self):
        claims = [_make_claim("c1", status="accepted")]
        errors = validate_rejected_claims_have_reason(claims)
        assert errors == []


class TestRevisionsLinkClaims:
    def test_valid_revision(self):
        revisions = [_make_revision(old_claim_id="c1", new_claim_id="c2")]
        errors = validate_revisions_link_claims(revisions)
        assert errors == []

    def test_missing_old_claim_id(self):
        revisions = [_make_revision(old_claim_id="", new_claim_id="c2")]
        errors = validate_revisions_link_claims(revisions)
        assert len(errors) == 1
        assert "old_claim_id" in errors[0]

    def test_missing_new_claim_id(self):
        revisions = [_make_revision(old_claim_id="c1", new_claim_id="")]
        errors = validate_revisions_link_claims(revisions)
        assert len(errors) == 1
        assert "new_claim_id" in errors[0]

    def test_same_claim_ids(self):
        revisions = [_make_revision(old_claim_id="c1", new_claim_id="c1")]
        errors = validate_revisions_link_claims(revisions)
        assert len(errors) == 1
        assert "same claim" in errors[0]


class TestClaimHasUniqueId:
    def test_unique_ids_ok(self):
        claims = [_make_claim("c1"), _make_claim("c2")]
        errors = validate_claim_has_unique_id(claims)
        assert errors == []

    def test_duplicate_ids_fail(self):
        claims = [_make_claim("c1"), _make_claim("c1")]
        errors = validate_claim_has_unique_id(claims)
        assert len(errors) == 1
        assert "c1" in errors[0]


class TestFinalAnswerDeclaresRisks:
    def test_with_risks_ok(self):
        fa = _make_final_answer(risks=[RiskItem(description="risk1")])
        errors = validate_final_answer_declares_risks(fa)
        assert errors == []

    def test_without_risks_fails(self):
        fa = _make_final_answer(risks=[])
        errors = validate_final_answer_declares_risks(fa)
        assert len(errors) == 1


class TestValidateAllInvariants:
    def test_all_pass(self):
        claims = [_make_claim("c1", status="accepted", confidence=0.8, requires_evidence=True, evidence_status="supported")]
        revisions = [_make_revision(old_claim_id="c0", new_claim_id="c1")]
        fa = _make_final_answer(accepted_claim_ids=["c1"], risks=[RiskItem(description="risk")])
        errors = validate_all_invariants(fa, claims, revisions)
        assert errors == []

    def test_no_final_answer(self):
        claims = [_make_claim("c1")]
        errors = validate_all_invariants(None, claims, [])
        assert errors == []
