from .claim import Claim
from .final_answer import FinalAnswer
from .revision import Revision


def validate_final_answer_references_accepted_claims(
    final_answer: FinalAnswer, claims: list[Claim],
) -> list[str]:
    """Invariant 1: Final answers must reference accepted claims."""
    errors: list[str] = []
    accepted_ids = {c.id for c in claims if c.status == "accepted"}
    for claim_id in final_answer.accepted_claim_ids:
        if claim_id not in accepted_ids:
            errors.append(
                f"Final answer references non-accepted claim {claim_id}",
            )
    return errors


def validate_high_confidence_claims_have_evidence(
    claims: list[Claim],
) -> list[str]:
    """Invariant 2: High-confidence claims need evidence or explicit uncertainty."""
    errors: list[str] = []
    for claim in claims:
        if (
            claim.confidence >= 0.7
            and claim.requires_evidence
            and claim.evidence_status == "unsupported"
            and claim.status != "uncertain"
        ):
            errors.append(
                f"High-confidence claim {claim.id} lacks evidence support "
                f"(confidence={claim.confidence}, evidence_status={claim.evidence_status})",
            )
    return errors


def validate_rejected_claims_have_reason(
    claims: list[Claim],
) -> list[str]:
    """Invariant 3: Every rejected claim needs a rejection reason."""
    errors: list[str] = []
    for claim in claims:
        if claim.status == "rejected" and not claim.rejection_reason:
            errors.append(f"Rejected claim {claim.id} has no rejection_reason")
    return errors


def validate_revisions_link_claims(revisions: list[Revision]) -> list[str]:
    """Invariant 4: Every revision must link old claim and new claim."""
    errors: list[str] = []
    for revision in revisions:
        if not revision.old_claim_id:
            errors.append(f"Revision {revision.id} missing old_claim_id")
        if not revision.new_claim_id:
            errors.append(f"Revision {revision.id} missing new_claim_id")
        if revision.old_claim_id == revision.new_claim_id:
            errors.append(
                f"Revision {revision.id} links old and new to same claim "
                f"({revision.old_claim_id})",
            )
    return errors


def validate_claim_has_unique_id(claims: list[Claim]) -> list[str]:
    """Invariant 5: Every claim must have a unique identifier."""
    errors: list[str] = []
    seen: set[str] = set()
    for claim in claims:
        if claim.id in seen:
            errors.append(f"Duplicate claim ID: {claim.id}")
        seen.add(claim.id)
    return errors


def validate_final_answer_declares_risks(
    final_answer: FinalAnswer,
) -> list[str]:
    """Invariant 6: Every final answer must declare remaining risks."""
    errors: list[str] = []
    if not final_answer.risks:
        errors.append(
            f"Final answer {final_answer.id} has no declared risks",
        )
    return errors


def validate_all_invariants(
    final_answer: FinalAnswer | None,
    claims: list[Claim],
    revisions: list[Revision],
) -> list[str]:
    """Run all invariant checks and return collected errors."""
    errors: list[str] = []
    errors.extend(validate_high_confidence_claims_have_evidence(claims))
    errors.extend(validate_rejected_claims_have_reason(claims))
    errors.extend(validate_revisions_link_claims(revisions))
    errors.extend(validate_claim_has_unique_id(claims))
    if final_answer is not None:
        errors.extend(
            validate_final_answer_references_accepted_claims(
                final_answer, claims,
            ),
        )
        errors.extend(validate_final_answer_declares_risks(final_answer))
    return errors
