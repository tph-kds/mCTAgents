/**
 * LangGraph runtime adapter for mCTAgents.
 *
 * Provides two integration patterns:
 * 1. Use mCTAgents as a LangGraph node (run CCSR workflow from LangGraph)
 * 2. Use LangGraph agents inside mCTAgents (wrap LangGraph agents as CCSR agents)
 */

import { MCTAgentsClient, type ReasoningEvent } from "@mctagents/ts-sdk";

export interface MCTAgentsNodeConfig {
  apiUrl: string;
  apiKey?: string;
  mode?: string;
}

/**
 * Creates a LangGraph node that runs the mCTAgents CCSR workflow.
 *
 * Usage in a LangGraph graph:
 * ```ts
 * import { createMCTAgentsNode } from "@mctagents/runtime-langgraph";
 *
 * const mctNode = createMCTAgentsNode({ apiUrl: "http://localhost:8080" });
 * // Add to your LangGraph StateGraph
 * ```
 */
export function createMCTAgentsNode(config: MCTAgentsNodeConfig) {
  const client = new MCTAgentsClient({
    baseUrl: config.apiUrl,
    apiKey: config.apiKey,
  });

  return async function mctAgentsNode(state: Record<string, unknown>) {
    const problem = state.problem as string;
    if (!problem) {
      throw new Error("mCTAgents node requires a 'problem' field in state");
    }

    const run = await client.runs.create({
      problem,
      mode: config.mode || "balanced_reasoning",
    });

    const events: ReasoningEvent[] = [];
    let finalEvent: ReasoningEvent | null = null;

    for await (const event of client.runs.stream(run.run_id)) {
      events.push(event);
      if (event.type === "run_completed" || event.type === "run_failed") {
        finalEvent = event;
        break;
      }
    }

    const claims = await client.runs.getClaims(run.run_id);

    return {
      ...state,
      mctagents_run_id: run.run_id,
      mctagents_events: events,
      mctagents_claims: claims,
      mctagents_status: finalEvent?.type === "run_completed" ? "completed" : "failed",
    };
  };
}

export { MCTAgentsClient, type ReasoningEvent };
