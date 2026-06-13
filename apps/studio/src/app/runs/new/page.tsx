"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createRun } from "@/lib/api";

const REASONING_MODES = [
  {
    id: "balanced_reasoning",
    label: "Balanced",
    description: "Standard multi-agent deliberation with all 6 agents",
    icon: "⚖",
    color: "blue",
  },
  {
    id: "fast_consensus",
    label: "Fast",
    description: "Accelerated consensus with minimal debate rounds",
    icon: "⚡",
    color: "cyan",
  },
  {
    id: "deep_deliberation",
    label: "Deep",
    description: "Extended critique and revision cycles for complex problems",
    icon: "🔬",
    color: "purple",
  },
];

const EXAMPLE_PROMPTS = [
  "Should our startup adopt microservices or a monolith for a 5-person team?",
  "What are the tradeoffs of using Rust vs Go for a high-throughput API gateway?",
  "Is zero-knowledge proof ready for mainstream authentication systems?",
];

export default function NewRunPage() {
  const router = useRouter();
  const [problem, setProblem] = useState("");
  const [mode, setMode] = useState("balanced_reasoning");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!problem.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const run = await createRun(problem.trim(), mode);
      router.push(`/runs/${run.run_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create run");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center px-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-[10px] font-mono text-blue-400 mb-4">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
            NEW SESSION
          </div>
          <h1 className="text-2xl font-bold text-glow-blue mb-2">Initialize Agent Society</h1>
          <p className="text-sm text-slate-400">
            Describe a problem and deploy 6 specialized agents to reason through it
          </p>
        </div>

        {/* Main form card */}
        <div className="glass-panel-solid p-6 hud-border">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Problem statement input */}
            <div>
              <label className="block text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-2">
                Problem Statement
              </label>
              <textarea
                value={problem}
                onChange={(e) => setProblem(e.target.value)}
                rows={5}
                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 resize-none font-mono transition-colors"
                placeholder="Describe the problem you want the agent society to reason about..."
              />
              <div className="flex justify-between mt-1.5">
                <span className="text-[9px] text-slate-600">
                  {problem.length > 0 ? `${problem.length} chars` : ""}
                </span>
                {problem.length > 0 && problem.length < 20 && (
                  <span className="text-[9px] text-yellow-500/70">More detail improves reasoning</span>
                )}
              </div>
            </div>

            {/* Mode selector */}
            <div>
              <label className="block text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-2">
                Reasoning Mode
              </label>
              <div className="grid grid-cols-3 gap-2">
                {REASONING_MODES.map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => setMode(m.id)}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      mode === m.id
                        ? "border-blue-500/50 bg-blue-500/10"
                        : "border-white/5 bg-white/5 hover:bg-white/10"
                    }`}
                  >
                    <div className="text-lg mb-1">{m.icon}</div>
                    <div className={`text-xs font-medium ${mode === m.id ? "text-blue-400" : "text-slate-300"}`}>
                      {m.label}
                    </div>
                    <div className="text-[10px] text-slate-500 mt-0.5 leading-tight">{m.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Example prompts */}
            <div>
              <label className="block text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-2">
                Example Prompts
              </label>
              <div className="space-y-1.5">
                {EXAMPLE_PROMPTS.map((prompt, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setProblem(prompt)}
                    className="w-full text-left px-3 py-2 text-[11px] text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-lg transition-colors leading-relaxed"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-400">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading || !problem.trim()}
              className="w-full relative overflow-hidden px-4 py-3 rounded-lg font-medium text-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white shadow-lg shadow-blue-500/20"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Initializing Agents...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  Deploy Agent Society
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              )}
            </button>
          </form>
        </div>

        {/* Footer hint */}
        <div className="text-center mt-6">
          <p className="text-[10px] text-slate-600">
            6 agents will collaborate: ProblemFramer → Architect → Evidence → Critic → Judge → Synthesizer
          </p>
        </div>
      </div>
    </div>
  );
}
