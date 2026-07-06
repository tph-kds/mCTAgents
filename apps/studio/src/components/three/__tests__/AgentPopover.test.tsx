import { render, screen, fireEvent } from "@testing-library/react";
import { AgentPopover } from "../AgentPopover";
import type { Claim, Objection, SSEEvent } from "@/lib/types";

const mockAgent = {
  id: "architect_agent",
  name: "Architect",
  description: "Proposes architectural decisions",
  role: "architect",
};

const mockClaims: Claim[] = [
  {
    id: "c1",
    run_id: "run-1",
    author_agent_id: "architect_agent",
    text: "We should adopt microservices",
    claim_type: "architecture_decision",
    confidence: 0.85,
    status: "accepted",
    evidence_status: "attached",
  },
];

const mockObjections: Objection[] = [
  {
    id: "o1",
    run_id: "run-1",
    target_claim_id: "c1",
    author_agent_id: "architect_agent",
    reason: "Adds deployment complexity",
    severity: "high",
    requested_fix: null,
  },
];

const mockEvents: SSEEvent[] = [
  {
    event_id: "e1",
    run_id: "run-1",
    type: "claim_proposed",
    sequence: 1,
    agent_id: "architect_agent",
    payload: {},
    created_at: "2025-01-01T00:00:00Z",
  },
];

describe("AgentPopover", () => {
  it("renders agent name and description", () => {
    render(
      <AgentPopover
        agent={mockAgent}
        claims={mockClaims}
        objections={[]}
        events={[]}
        onClose={() => {}}
      />
    );
    expect(screen.getByText("Architect")).toBeInTheDocument();
    expect(screen.getByText("Proposes architectural decisions")).toBeInTheDocument();
  });

  it("shows claims count in tab", () => {
    render(
      <AgentPopover
        agent={mockAgent}
        claims={mockClaims}
        objections={[]}
        events={[]}
        onClose={() => {}}
      />
    );
    expect(screen.getByText(/claims/i)).toBeInTheDocument();
  });

  it("displays claim text in claims tab", () => {
    render(
      <AgentPopover
        agent={mockAgent}
        claims={mockClaims}
        objections={[]}
        events={[]}
        onClose={() => {}}
      />
    );
    expect(screen.getByText("We should adopt microservices")).toBeInTheDocument();
  });

  it("shows empty state when no claims", () => {
    render(
      <AgentPopover
        agent={mockAgent}
        claims={[]}
        objections={[]}
        events={[]}
        onClose={() => {}}
      />
    );
    expect(screen.getByText(/no claims yet/i)).toBeInTheDocument();
  });

  it("calls onClose when close button clicked", () => {
    const onClose = vi.fn();
    render(
      <AgentPopover
        agent={mockAgent}
        claims={[]}
        objections={[]}
        events={[]}
        onClose={onClose}
      />
    );
    fireEvent.click(screen.getByText("x"));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("switches to objections tab", () => {
    render(
      <AgentPopover
        agent={mockAgent}
        claims={[]}
        objections={mockObjections}
        events={[]}
        onClose={() => {}}
      />
    );
    fireEvent.click(screen.getByText(/objections/i));
    expect(screen.getByText("Adds deployment complexity")).toBeInTheDocument();
  });

  it("switches to activity tab", () => {
    render(
      <AgentPopover
        agent={mockAgent}
        claims={[]}
        objections={[]}
        events={mockEvents}
        onClose={() => {}}
      />
    );
    fireEvent.click(screen.getByText(/activity/i));
    expect(screen.getByText("claim proposed")).toBeInTheDocument();
  });

  it("filters data by agent id", () => {
    const otherAgentClaims: Claim[] = [
      {
        id: "c2",
        run_id: "run-1",
        author_agent_id: "other_agent",
        text: "Other agent claim",
        claim_type: "general",
        confidence: 0.5,
        status: "proposed",
        evidence_status: "none",
      },
    ];
    render(
      <AgentPopover
        agent={mockAgent}
        claims={otherAgentClaims}
        objections={[]}
        events={[]}
        onClose={() => {}}
      />
    );
    expect(screen.getByText(/no claims yet/i)).toBeInTheDocument();
  });
});
