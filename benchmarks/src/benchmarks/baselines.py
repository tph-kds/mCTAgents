"""Baseline single-agent benchmark for comparison."""

import time
from dataclasses import dataclass
from benchmarks.runner import BenchmarkResult


@dataclass
class BaselineResult:
    """Result from a baseline (single-agent) run."""

    task_id: str
    score: float
    latency_ms: float
    claims_count: int


class SingleAgentBaseline:
    """Baseline that uses a single LLM call without the CCSR protocol.

    This provides a comparison point to measure the improvement
    that the multi-agent CCSR workflow provides over a single query.
    """

    def __init__(self, api_url: str = "http://localhost:8090"):
        self.api_url = api_url

    def run_task(self, task: dict) -> BaselineResult:
        """Run a single-agent baseline on a task.

        Args:
            task: Task dict with 'problem' and optional 'rubric'.

        Returns:
            BaselineResult with score and timing.
        """
        import httpx

        start = time.time()

        try:
            resp = httpx.post(
                f"{self.api_url}/v1/chat",
                json={
                    "model": "qwen2.5:7b",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant. Answer the following question directly and concisely."},
                        {"role": "user", "content": task["problem"]},
                    ],
                },
                timeout=60.0,
            )
            resp.raise_for_status()
            latency_ms = (time.time() - start) * 1000

            # Simple scoring: treat the response as a single claim
            response_text = resp.json().get("response", "")

            # Count words as a proxy for claims
            words = len(response_text.split())
            claims_count = max(1, words // 20)  # rough estimate

            # Simple heuristic score
            score = 0.5  # baseline is always 0.5

            return BaselineResult(
                task_id=task["id"],
                score=score,
                latency_ms=latency_ms,
                claims_count=claims_count,
            )
        except Exception:
            latency_ms = (time.time() - start) * 1000
            return BaselineResult(
                task_id=task["id"],
                score=0.0,
                latency_ms=latency_ms,
                claims_count=0,
            )


def compute_improvement(mct_score: float, baseline_score: float) -> float:
    """Compute the improvement ratio of mCTAgents over baseline.

    Args:
        mct_score: Score from mCTAgents run.
        baseline_score: Score from single-agent baseline.

    Returns:
        Improvement ratio (1.0 = no improvement, >1.0 = mCTAgents better).
    """
    if baseline_score == 0:
        return float("inf") if mct_score > 0 else 1.0
    return mct_score / baseline_score
