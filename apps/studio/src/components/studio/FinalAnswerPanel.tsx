"use client";

interface RiskItem {
  description: string;
  severity: string;
  mitigation?: string;
}

interface FinalAnswerData {
  text: string;
  confidence: number;
  risks: RiskItem[];
  accepted_claim_ids?: string[];
  next_steps?: string[];
}

export function FinalAnswerPanel({ answer }: { answer: FinalAnswerData | null }) {
  if (!answer) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-2">Final Answer</h3>
        <p className="text-gray-500 text-sm">No final answer yet.</p>
      </div>
    );
  }

  const severityColor: Record<string, string> = {
    high: "text-red-400",
    medium: "text-yellow-400",
    low: "text-green-400",
  };

  return (
    <div className="bg-gray-900 border border-green-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-2">Final Answer</h3>
      <p className="text-sm mb-4 whitespace-pre-wrap">{answer.text}</p>

      <div className="flex items-center gap-2 mb-4">
        <span className="text-xs text-gray-400">Confidence:</span>
        <div className="w-24 bg-gray-800 rounded-full h-2">
          <div
            className="bg-green-500 h-2 rounded-full"
            style={{ width: `${answer.confidence * 100}%` }}
          />
        </div>
        <span className="text-xs text-gray-400">
          {(answer.confidence * 100).toFixed(0)}%
        </span>
      </div>

      {answer.accepted_claim_ids && answer.accepted_claim_ids.length > 0 && (
        <div className="mb-4">
          <span className="text-xs text-gray-400 font-medium">Based on {answer.accepted_claim_ids.length} accepted claims</span>
        </div>
      )}

      {answer.risks && answer.risks.length > 0 && (
        <div className="mt-4">
          <span className="text-xs text-yellow-500 font-medium">Remaining Risks:</span>
          <ul className="mt-1 space-y-2">
            {answer.risks.map((risk, i) => (
              <li key={i} className="text-xs">
                <span className={`font-medium ${severityColor[risk.severity] || "text-gray-400"}`}>
                  [{risk.severity}]
                </span>{" "}
                <span className="text-gray-300">{risk.description}</span>
                {risk.mitigation && (
                  <span className="text-gray-500 block ml-4">Mitigation: {risk.mitigation}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {answer.next_steps && answer.next_steps.length > 0 && (
        <div className="mt-4">
          <span className="text-xs text-blue-400 font-medium">Next Steps:</span>
          <ul className="mt-1 space-y-1">
            {answer.next_steps.map((step, i) => (
              <li key={i} className="text-xs text-gray-400">- {step}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
