"use client";
import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

interface RunResult {
  run_id: string;
  status: string;
  events: { type: string; agent_id?: string }[];
  claims_count: number;
}

export default function ComparePage() {
  const [problems, setProblems] = useState(["", ""]);
  const [results, setResults] = useState<(RunResult | null)[]>([null, null]);
  const [loading, setLoading] = useState(false);

  async function runComparison() {
    setLoading(true);
    const newResults: (RunResult | null)[] = [];

    for (let i = 0; i < problems.length; i++) {
      if (!problems[i].trim()) {
        newResults.push(null);
        continue;
      }
      try {
        const resp = await fetch(`${API_URL}/v1/runs`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ problem: problems[i] }),
        });
        const run = await resp.json();

        // Collect events
        const events: { type: string; agent_id?: string }[] = [];
        const es = new EventSource(`${API_URL}/v1/runs/${run.run_id}/events`);
        await new Promise<void>((resolve) => {
          const handler = (e: MessageEvent) => {
            try {
              const event = JSON.parse(e.data);
              events.push(event);
              if (event.type === "run_completed" || event.type === "run_failed") {
                es.close();
                resolve();
              }
            } catch {}
          };
          es.addEventListener("message", handler);
          es.onerror = () => { es.close(); resolve(); };
        });

        newResults.push({
          run_id: run.run_id,
          status: "completed",
          events,
          claims_count: events.filter((e) => e.type === "claim_created").length,
        });
      } catch {
        newResults.push(null);
      }
    }

    setResults(newResults);
    setLoading(false);
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Compare Problems</h1>
      <p className="text-gray-400">Run multiple problems side-by-side to compare agent reasoning.</p>

      <div className="grid grid-cols-2 gap-4">
        {problems.map((p, i) => (
          <div key={i}>
            <label className="block text-sm text-gray-400 mb-1">Problem {i + 1}</label>
            <textarea
              value={p}
              onChange={(e) => {
                const next = [...problems];
                next[i] = e.target.value;
                setProblems(next);
              }}
              rows={4}
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              placeholder="Enter problem statement..."
            />
          </div>
        ))}
      </div>

      <button
        onClick={runComparison}
        disabled={loading || problems.every((p) => !p.trim())}
        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 px-6 py-3 rounded-lg font-medium"
      >
        {loading ? "Running..." : "Compare"}
      </button>

      {results.some((r) => r !== null) && (
        <div className="grid grid-cols-2 gap-4">
          {results.map((result, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-lg p-4">
              <h3 className="font-semibold mb-2">Result {i + 1}</h3>
              {result ? (
                <div className="space-y-1 text-sm text-gray-400">
                  <p>Status: {result.status}</p>
                  <p>Claims: {result.claims_count}</p>
                  <p>Events: {result.events.length}</p>
                  <p>Run ID: {result.run_id}</p>
                </div>
              ) : (
                <p className="text-gray-600 text-sm">No result</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
