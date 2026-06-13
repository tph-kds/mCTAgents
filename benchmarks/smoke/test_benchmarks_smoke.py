"""Smoke tests for benchmarks - verify basic functionality without running full benchmarks."""

import pytest
from benchmarks.runner import BenchmarkRunner, BenchmarkResult
from benchmarks.leaderboard import Leaderboard
from benchmarks.scorers.completeness import CompletenessScorer
from benchmarks.scorers.consistency import ConsistencyScorer
from benchmarks.scorers.evidence_quality import EvidenceQualityScorer


class TestBenchmarkRunner:
    def test_load_task(self, tmp_path):
        task_file = tmp_path / "test_task.yaml"
        task_file.write_text("""
id: test-task
problem: "Test problem statement"
policy: balanced_reasoning
rubric:
  completeness: 0.33
  consistency: 0.33
  evidence: 0.34
""")
        runner = BenchmarkRunner(api_url="http://localhost:9999")
        task = runner.load_task(str(task_file))
        assert task["id"] == "test-task"
        assert task["problem"] == "Test problem statement"

    def test_benchmark_result_defaults(self):
        result = BenchmarkResult(task_id="t1", problem="test")
        assert result.mct_score == 0.0
        assert result.claims_count == 0


class TestLeaderboard:
    def test_leaderboard_initialization(self, tmp_path):
        lb = Leaderboard(results_dir=str(tmp_path / "results"))
        assert lb.get_top() == []

    def test_add_result(self, tmp_path):
        lb = Leaderboard(results_dir=str(tmp_path / "results"))
        result = BenchmarkResult(task_id="t1", problem="test", mct_score=0.85)
        lb.add_result(result)
        assert len(lb.get_top()) == 1

    def test_leaderboard_sorting(self, tmp_path):
        lb = Leaderboard(results_dir=str(tmp_path / "results"))
        lb.add_result(BenchmarkResult(task_id="t1", problem="test1", mct_score=0.7))
        lb.add_result(BenchmarkResult(task_id="t2", problem="test2", mct_score=0.9))
        lb.add_result(BenchmarkResult(task_id="t3", problem="test3", mct_score=0.8))
        results = lb.get_top()
        assert results[0]["mct_score"] == 0.9
        assert results[-1]["mct_score"] == 0.7

    def test_export_markdown(self, tmp_path):
        lb = Leaderboard(results_dir=str(tmp_path / "results"))
        lb.add_result(BenchmarkResult(task_id="t1", problem="test", mct_score=0.85, latency_ms=1200, claims_count=5))
        md = lb.export_markdown()
        assert "| Rank |" in md
        assert "t1" in md
