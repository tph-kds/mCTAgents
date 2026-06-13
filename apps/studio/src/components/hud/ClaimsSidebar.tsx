"use client";

import type { Claim } from "@/lib/types";

const STATUS_STYLES: Record<string, { bg: string; text: string; dot: string }> = {
  proposed: { bg: "bg-gray-500/10", text: "text-gray-400", dot: "bg-gray-500" },
  evidence_requested: { bg: "bg-yellow-500/10", text: "text-yellow-400", dot: "bg-yellow-500" },
  supported: { bg: "bg-cyan-500/10", text: "text-cyan-400", dot: "bg-cyan-500" },
  challenged: { bg: "bg-orange-500/10", text: "text-orange-400", dot: "bg-orange-500" },
  revision_required: { bg: "bg-pink-500/10", text: "text-pink-400", dot: "bg-pink-500" },
  revised: { bg: "bg-blue-500/10", text: "text-blue-400", dot: "bg-blue-500" },
  accepted: { bg: "bg-green-500/10", text: "text-green-400", dot: "bg-green-500" },
  rejected: { bg: "bg-red-500/10", text: "text-red-400", dot: "bg-red-500" },
  uncertain: { bg: "bg-yellow-500/10", text: "text-yellow-300", dot: "bg-yellow-300" },
};

interface ClaimsSidebarProps {
  claims: Claim[];
}

export function ClaimsSidebar({ claims }: ClaimsSidebarProps) {
  if (claims.length === 0) {
    return (
      <div className="glass-panel p-3">
        <div className="text-[10px] font-mono text-slate-500 mb-2 uppercase tracking-wider">Claims</div>
        <div className="text-xs text-slate-600 italic">No claims yet</div>
      </div>
    );
  }

  const sorted = [...claims].sort((a, b) => {
    const order = { accepted: 0, supported: 1, revised: 2, proposed: 3, challenged: 4, rejected: 5, uncertain: 6, evidence_requested: 7, revision_required: 8 };
    return (order[a.status as keyof typeof order] ?? 9) - (order[b.status as keyof typeof order] ?? 9);
  });

  return (
    <div className="glass-panel p-3">
      <div className="text-[10px] font-mono text-slate-500 mb-2 uppercase tracking-wider">
        Claims <span className="text-slate-600">({claims.length})</span>
      </div>
      <div className="space-y-2 max-h-[40vh] overflow-y-auto">
        {sorted.map((claim) => {
          const style = STATUS_STYLES[claim.status] || STATUS_STYLES.proposed;
          return (
            <div
              key={claim.id}
              className={`p-2 rounded-lg ${style.bg} border border-white/5`}
            >
              <div className="flex items-center gap-2 mb-1">
                <div className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
                <span className={`text-[10px] font-medium ${style.text}`}>
                  {claim.status.replace(/_/g, " ")}
                </span>
                <span className="text-[9px] text-slate-500 ml-auto font-mono">
                  {(claim.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-[11px] text-slate-300 line-clamp-2 leading-relaxed">
                {claim.text}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[9px] text-slate-500">{claim.claim_type.replace(/_/g, " ")}</span>
                {claim.evidence_status && claim.evidence_status !== "none" && (
                  <span className="text-[9px] text-yellow-500/70">evidence</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
