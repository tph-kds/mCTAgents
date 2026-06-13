"use client";
import type { Evidence } from "@/lib/types";

export function EvidenceBoard({ evidence }: { evidence: Evidence[] }) {
  if (evidence.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-2">Evidence</h3>
        <p className="text-gray-500 text-sm">No evidence attached yet.</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Evidence ({evidence.length})</h3>
      <div className="space-y-3">
        {evidence.map((e) => (
          <div key={e.id} className="border border-gray-700 rounded-lg p-3">
            <div className="flex justify-between items-start mb-1">
              <span className="text-xs bg-gray-800 px-2 py-0.5 rounded">{e.source_type}</span>
              <span className="text-xs text-gray-500">{(e.reliability_score * 100).toFixed(0)}% reliable</span>
            </div>
            <p className="text-sm text-gray-300">{e.summary}</p>
            <div className="mt-2 flex gap-4 text-xs text-gray-500">
              <span>Supports: {e.supports_claim_ids.length} claims</span>
              <span>Attacks: {e.attacks_claim_ids.length} claims</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}