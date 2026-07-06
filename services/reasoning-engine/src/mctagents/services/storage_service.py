import json
import logging

import asyncpg

from mctagents.core.protocol import (
    Claim,
    Decision,
    Event,
    Evidence,
    FinalAnswer,
    Objection,
    ProblemFrame,
    Revision,
)

logger = logging.getLogger(__name__)


class StorageService:
    """Stores and retrieves CCSR protocol objects from PostgreSQL."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Create the connection pool."""
        self._pool = await asyncpg.create_pool(
            self.database_url, min_size=2, max_size=10,
        )
        logger.info("StorageService connected to %s", self.database_url)

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("StorageService connection pool closed")

    # ── Runs ──────────────────────────────────────────────────────────

    async def save_run(
        self, run_id: str, status: str, mode: str = "balanced_reasoning",
    ) -> None:
        """Create or update a run record."""
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                """
                INSERT INTO runs (id, status, mode)
                VALUES ($1, $2, $3)
                ON CONFLICT (id) DO UPDATE SET status = $2, updated_at = NOW()
                """,
                run_id,
                status,
                mode,
            )

    async def update_run_status(self, run_id: str, status: str) -> None:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                "UPDATE runs SET status = $2, updated_at = NOW() WHERE id = $1",
                run_id,
                status,
            )

    async def get_run(self, run_id: str) -> dict | None:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            row = await conn.fetchrow(
                "SELECT * FROM runs WHERE id = $1", run_id,
            )
            return dict(row) if row else None

    # ── Problem Frames ────────────────────────────────────────────────

    async def save_problem_frame(self, frame: ProblemFrame) -> None:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                """
                INSERT INTO problem_frames
                    (id, run_id, original_input, normalized_problem,
                     constraints, success_criteria, risk_level, domain,
                     requires_business_decision, requires_research, requires_code)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
                """,
                frame.id,
                frame.run_id,
                frame.original_input,
                frame.normalized_problem,
                json.dumps(frame.constraints),
                json.dumps(frame.success_criteria),
                frame.risk_level,
                frame.domain,
                frame.requires_business_decision,
                frame.requires_research,
                frame.requires_code,
            )

    # ── Claims ────────────────────────────────────────────────────────

    async def save_claim(self, claim: Claim) -> None:
        scores = claim.scores
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                """
                INSERT INTO claims
                    (id, run_id, author_agent_id, text, claim_type,
                     confidence, status, requires_evidence, evidence_status,
                     parent_claim_id, rejection_reason,
                     score_logic, score_evidence, score_feasibility,
                     score_critic_resistance, score_risk_adjusted, score_final)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17)
                """,
                claim.id,
                claim.run_id,
                claim.author_agent_id,
                claim.text,
                claim.claim_type,
                claim.confidence,
                claim.status,
                claim.requires_evidence,
                claim.evidence_status,
                claim.parent_claim_id,
                claim.rejection_reason,
                scores.logic if scores else 0.0,
                scores.evidence if scores else 0.0,
                scores.feasibility if scores else 0.0,
                scores.critic_resistance if scores else 0.0,
                scores.risk_adjusted if scores else 0.0,
                scores.final if scores else 0.0,
            )

    async def get_claims(self, run_id: str) -> list[dict]:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            rows = await conn.fetch(
                "SELECT * FROM claims WHERE run_id = $1", run_id,
            )
            return [dict(r) for r in rows]

    # ── Evidence ──────────────────────────────────────────────────────

    async def save_evidence(self, ev: Evidence) -> None:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                """
                INSERT INTO evidence
                    (id, run_id, source_type, source_ref, summary,
                     reliability_score, supports_claim_ids, attacks_claim_ids)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                """,
                ev.id,
                ev.run_id,
                ev.source_type,
                ev.source_ref,
                ev.summary,
                ev.reliability_score,
                ev.supports_claim_ids,
                ev.attacks_claim_ids,
            )

    async def get_evidence(self, run_id: str) -> list[dict]:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            rows = await conn.fetch(
                "SELECT * FROM evidence WHERE run_id = $1", run_id,
            )
            return [dict(r) for r in rows]

    # ── Objections ────────────────────────────────────────────────────

    async def save_objection(self, obj: Objection) -> None:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                """
                INSERT INTO objections
                    (id, run_id, target_claim_id, author_agent_id,
                     reason, severity, requested_fix)
                VALUES ($1,$2,$3,$4,$5,$6,$7)
                """,
                obj.id,
                obj.run_id,
                obj.target_claim_id,
                obj.author_agent_id,
                obj.reason,
                obj.severity,
                obj.requested_fix,
            )

    async def get_objections(self, run_id: str) -> list[dict]:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            rows = await conn.fetch(
                "SELECT * FROM objections WHERE run_id = $1", run_id,
            )
            return [dict(r) for r in rows]

    # ── Revisions ─────────────────────────────────────────────────────

    async def save_revision(self, rev: Revision) -> None:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                """
                INSERT INTO revisions
                    (id, run_id, old_claim_id, new_claim_id,
                     reason, revision_type, improvement_score)
                VALUES ($1,$2,$3,$4,$5,$6,$7)
                """,
                rev.id,
                rev.run_id,
                rev.old_claim_id,
                rev.new_claim_id,
                rev.reason,
                rev.revision_type,
                rev.improvement_score,
            )

    async def get_revisions(self, run_id: str) -> list[dict]:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            rows = await conn.fetch(
                "SELECT * FROM revisions WHERE run_id = $1", run_id,
            )
            return [dict(r) for r in rows]

    # ── Decisions ─────────────────────────────────────────────────────

    async def save_decision(self, decision: Decision) -> None:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                """
                INSERT INTO decisions
                    (id, run_id, accepted_claim_ids, rejected_claim_ids,
                     uncertain_claim_ids, score_breakdown, confidence,
                     needs_more_debate, extra_debate_reason)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                """,
                decision.id,
                decision.run_id,
                decision.accepted_claim_ids,
                decision.rejected_claim_ids,
                decision.uncertain_claim_ids,
                json.dumps(decision.score_breakdown),
                decision.confidence,
                decision.needs_more_debate,
                decision.extra_debate_reason,
            )

    async def get_decision(self, run_id: str) -> dict | None:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            row = await conn.fetchrow(
                "SELECT * FROM decisions WHERE run_id = $1", run_id,
            )
            return dict(row) if row else None

    # ── Final Answers ─────────────────────────────────────────────────

    async def save_final_answer(self, fa: FinalAnswer) -> None:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                """
                INSERT INTO final_answers
                    (id, run_id, answer_text, accepted_claim_ids,
                     rejected_alternatives, risks, next_steps, confidence)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                """,
                fa.id,
                fa.run_id,
                fa.answer_text,
                fa.accepted_claim_ids,
                json.dumps(fa.rejected_alternatives),
                json.dumps([r.model_dump() for r in fa.risks]),
                json.dumps(fa.next_steps),
                fa.confidence,
            )

    async def get_final_answer(self, run_id: str) -> dict | None:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            row = await conn.fetchrow(
                "SELECT * FROM final_answers WHERE run_id = $1", run_id,
            )
            return dict(row) if row else None

    # ── Events ────────────────────────────────────────────────────────

    async def save_event(self, event: Event) -> None:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                """
                INSERT INTO events (event_id, run_id, sequence, type, agent_id, payload)
                VALUES ($1,$2,$3,$4,$5,$6)
                """,
                event.event_id,
                event.run_id,
                event.sequence,
                event.type,
                event.agent_id,
                json.dumps(event.payload),
            )

    async def get_events(self, run_id: str) -> list[dict]:
        async with self._pool.acquire() as conn:  # type: ignore[union-attr]
            rows = await conn.fetch(
                "SELECT * FROM events WHERE run_id = $1 ORDER BY sequence",
                run_id,
            )
            return [dict(r) for r in rows]
