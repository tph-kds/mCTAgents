from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class LeaderboardEntry:
    task_id: str
    score: float
    latency_ms: float
    claims: int
    policy: str

class Leaderboard:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
    
    def add_result(self, result):
        entry = {"task_id": result.task_id, "mct_score": result.mct_score,
                 "latency_ms": result.latency_ms, "claims": result.claims_count}
        path = self.results_dir / f"{result.task_id}.json"
        path.write_text(json.dumps(entry, indent=2))
    
    def get_top(self, n: int = 10) -> list[dict]:
        results = []
        for f in self.results_dir.glob("*.json"):
            results.append(json.loads(f.read_text()))
        results.sort(key=lambda x: x.get("mct_score", 0), reverse=True)
        return results[:n]
    
    def export_markdown(self) -> str:
        entries = self.get_top(20)
        lines = ["| Rank | Task | Score | Latency | Claims |",
                 "|------|------|-------|---------|--------|"]
        for i, e in enumerate(entries, 1):
            lines.append(f"| {i} | {e['task_id']} | {e['mct_score']:.3f} | {e['latency_ms']:.0f}ms | {e['claims']} |")
        return "\n".join(lines)
