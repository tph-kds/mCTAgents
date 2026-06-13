"use client";

export function ClaimNode({ claim }: { claim: { id: string; text: string; status: string; confidence: number; claim_type: string } }) {
  const statusColor = {
    proposed: "border-gray-600",
    supported: "border-green-600",
    challenged: "border-yellow-600",
    accepted: "border-green-500 bg-green-950",
    rejected: "border-red-500 bg-red-950",
    uncertain: "border-yellow-500",
  }[claim.status] || "border-gray-600";

  return (
    <div className={`border-2 ${statusColor} rounded-lg p-4 max-w-sm`}>
      <div className="text-xs text-gray-400 mb-1">{claim.claim_type.replace(/_/g, " ")}</div>
      <p className="text-sm">{claim.text}</p>
      <div className="mt-2 flex justify-between text-xs text-gray-500">
        <span className="capitalize">{claim.status}</span>
        <span>{(claim.confidence * 100).toFixed(0)}% confidence</span>
      </div>
    </div>
  );
}