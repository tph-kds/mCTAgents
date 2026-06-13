"""mCTAgents SDK - Python client for the mCTAgents social reasoning API."""

import json
import httpx
from dataclasses import dataclass, field
from typing import Generator, AsyncGenerator

__version__ = "0.1.0"

@dataclass
class Run:
    run_id: str
    status: str
    events_url: str

@dataclass
class ReasoningEvent:
    event_id: str
    run_id: str
    type: str
    sequence: int
    payload: dict
    created_at: str
    agent_id: str | None = None

class MCTAgentsClient:
    """Client for the mCTAgents API.
    
    Usage:
        client = MCTAgentsClient(base_url="http://localhost:8080")
        run = client.create_run(problem="Should we use microservices?")
        for event in client.stream_events(run.run_id):
            print(f"[{event.type}] {event.payload}")
    """
    
    def __init__(self, base_url: str, api_key: str | None = None, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.Client(timeout=timeout)
    
    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    def create_run(self, problem: str, mode: str = "balanced_reasoning", 
                   evidence_policy: str = "required_for_major_claims",
                   budget: dict | None = None) -> Run:
        """Create a new reasoning run."""
        body = {"problem": problem, "mode": mode, "evidence_policy": evidence_policy}
        if budget:
            body["budget"] = budget
        resp = self.client.post(f"{self.base_url}/v1/runs", json=body, headers=self._headers())
        resp.raise_for_status()
        data = resp.json()
        return Run(run_id=data["run_id"], status=data["status"], events_url=data["events_url"])
    
    def get_run(self, run_id: str) -> dict:
        """Get run status and metadata."""
        resp = self.client.get(f"{self.base_url}/v1/runs/{run_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()
    
    def stream_events(self, run_id: str) -> Generator[ReasoningEvent, None, None]:
        """Stream events from a run using SSE.
        
        Usage:
            for event in client.stream_events(run_id):
                print(f"[{event.type}] {event.payload}")
                if event.type == "run_completed":
                    break
        """
        with self.client.stream("GET", f"{self.base_url}/v1/runs/{run_id}/events",
                                headers=self._headers()) as resp:
            event_type = None
            data_lines: list[str] = []
            
            for line in resp.iter_lines():
                if line.startswith("event: "):
                    event_type = line[7:]
                elif line.startswith("data: "):
                    data_lines.append(line[6:])
                elif line.startswith(":"):
                    continue  # keepalive
                elif line == "":
                    if data_lines:
                        try:
                            payload = json.loads("\n".join(data_lines))
                            yield ReasoningEvent(
                                event_id=payload.get("event_id", ""),
                                run_id=payload.get("run_id", run_id),
                                type=event_type or payload.get("type", "unknown"),
                                sequence=payload.get("sequence", 0),
                                payload=payload.get("payload", payload),
                                created_at=payload.get("created_at", ""),
                                agent_id=payload.get("agent_id"),
                            )
                        except json.JSONDecodeError:
                            pass
                        event_type = None
                        data_lines = []
            # Flush remaining data (stream ended without trailing blank line)
            if data_lines:
                try:
                    payload = json.loads("\n".join(data_lines))
                    yield ReasoningEvent(
                        event_id=payload.get("event_id", ""),
                        run_id=payload.get("run_id", run_id),
                        type=event_type or payload.get("type", "unknown"),
                        sequence=payload.get("sequence", 0),
                        payload=payload.get("payload", payload),
                        created_at=payload.get("created_at", ""),
                        agent_id=payload.get("agent_id"),
                    )
                except json.JSONDecodeError:
                    pass
    
    def cancel_run(self, run_id: str) -> None:
        """Cancel a running reasoning session."""
        resp = self.client.post(f"{self.base_url}/v1/runs/{run_id}/cancel",
                                headers=self._headers())
        resp.raise_for_status()
    
    def get_claims(self, run_id: str) -> list[dict]:
        """Get all claims for a run."""
        resp = self.client.get(f"{self.base_url}/v1/runs/{run_id}/claims",
                               headers=self._headers())
        resp.raise_for_status()
        return resp.json().get("claims", [])
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
