import yaml
import httpx
import time
from pathlib import Path
from dataclasses import dataclass, field
from mctagents_sdk import MCTAgentsClient
from benchmarks.scorers.completeness import CompletenessScorer
from benchmarks.scorers.consistency import ConsistencyScorer
from benchmarks.scorers.evidence_quality import EvidenceQualityScorer

@dataclass
class BenchmarkResult:
    task_id: str
    problem: str
    mct_score: float = 0.0
    single_score: float = 0.0
    improvement: float = 0.0
    latency_ms: float = 0.0
    total_tokens: int = 0
    claims_count: int = 0
    evidence_count: int = 0
    objections_count: int = 0

class BenchmarkRunner:
    def __init__(self, api_url: str = "http://localhost:8080"):
        self.client = MCTAgentsClient(base_url=api_url)
        self.scorers = [
            CompletenessScorer(),
            ConsistencyScorer(),
            EvidenceQualityScorer(),
        ]
    
    def load_task(self, task_path: str) -> dict:
        with open(task_path) as f:
            return yaml.safe_load(f)
    
    def load_tasks(self, tasks_dir: str = "tasks") -> list[dict]:
        tasks = []
        for p in Path(tasks_dir).glob("*.yaml"):
            tasks.append(self.load_task(str(p)))
        return tasks
    
    def run_task(self, task: dict) -> BenchmarkResult:
        result = BenchmarkResult(task_id=task["id"], problem=task["problem"])
        
        # Run mCTAgents
        start = time.time()
        run = self.client.create_run(
            problem=task["problem"],
            mode=task.get("policy", "balanced_reasoning"),
        )
        
        events = list(self.client.stream_events(run.run_id))
        result.latency_ms = (time.time() - start) * 1000
        
        # Collect objects
        claims = self.client.get_claims(run.run_id)
        result.claims_count = len(claims)
        
        # Score
        result.mct_score = self._score(claims, task.get("rubric", {}))
        
        return result
    
    def _score(self, claims: list[dict], rubric: dict) -> float:
        scores = {}
        for scorer in self.scorers:
            scores[scorer.name] = scorer.score(claims)
        # Weighted average
        weights = rubric or {"completeness": 0.33, "consistency": 0.33, "evidence": 0.34}
        total = sum(scores.get(k, 0.5) * v for k, v in weights.items())
        return round(total, 3)
