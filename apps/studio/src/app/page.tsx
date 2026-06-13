import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center px-4">
      <div className="w-full max-w-xl text-center">
        {/* Hero logo */}
        <div className="relative w-20 h-20 mx-auto mb-6">
          <div className="absolute inset-0 rounded-2xl bg-blue-500/10 blur-xl" />
          <div className="relative w-full h-full glass-panel-solid rounded-2xl flex items-center justify-center neon-glow-blue">
            <svg viewBox="0 0 24 24" className="w-10 h-10 text-blue-400" fill="none" stroke="currentColor" strokeWidth="1.5">
              <polygon points="12,2 22,8.5 22,15.5 12,22 2,15.5 2,8.5" />
              <line x1="12" y1="22" x2="12" y2="15.5" />
              <polyline points="22,8.5 12,15.5 2,8.5" />
            </svg>
          </div>
        </div>

        <h1 className="text-3xl font-bold text-glow-blue mb-3">mCTAgents</h1>
        <p className="text-sm text-slate-400 mb-2">
          Claim-Centered Social Reasoning Engine
        </p>
        <p className="text-xs text-slate-500 mb-8 max-w-md mx-auto leading-relaxed">
          Deploy a society of 6 AI agents that debate, challenge, and refine claims to produce
          transparent, evidence-backed answers.
        </p>

        {/* Agent preview */}
        <div className="flex justify-center gap-3 mb-8">
          {[
            { name: "Framer", color: "blue" },
            { name: "Architect", color: "cyan" },
            { name: "Evidence", color: "yellow" },
            { name: "Critic", color: "orange" },
            { name: "Judge", color: "green" },
            { name: "Synth", color: "purple" },
          ].map((agent) => (
            <div key={agent.name} className="flex flex-col items-center gap-1">
              <div className={`w-8 h-8 rounded-lg bg-${agent.color}-500/20 border border-${agent.color}-500/30 flex items-center justify-center`}>
                <div className={`w-3 h-3 rounded-sm bg-${agent.color}-500`} />
              </div>
              <span className="text-[9px] text-slate-500">{agent.name}</span>
            </div>
          ))}
        </div>

        {/* CTA */}
        <Link
          href="/runs/new"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium text-sm bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white shadow-lg shadow-blue-500/20 transition-all"
        >
          Start New Session
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Link>

        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          {[
            { label: "6 Agents", desc: "Specialized roles" },
            { label: "Debate", desc: "Adversarial testing" },
            { label: "Evidence", desc: "Source-backed claims" },
          ].map((item) => (
            <div key={item.label} className="glass-panel p-3">
              <div className="text-xs font-medium text-slate-300">{item.label}</div>
              <div className="text-[10px] text-slate-500 mt-0.5">{item.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
