import { render, screen } from "@testing-library/react";
import { ThinkingTracesPanel } from "../ThinkingTracesPanel";

const mockSteps = [
  {
    step_type: "reasoning",
    content: "Analyzing the claim structure...",
    agent_id: "architect_agent",
    sequence: 0,
  },
  {
    step_type: "tool_call",
    content: "Searching for evidence...",
    agent_id: "evidence_agent",
    tool_name: "vector_search",
    sequence: 1,
  },
];

describe("ThinkingTracesPanel", () => {
  it("renders thinking steps", () => {
    render(<ThinkingTracesPanel steps={mockSteps} />);
    expect(screen.getByText("Analyzing the claim structure...")).toBeInTheDocument();
    expect(screen.getByText("Searching for evidence...")).toBeInTheDocument();
  });

  it("shows agent names", () => {
    render(<ThinkingTracesPanel steps={mockSteps} />);
    expect(screen.getByText("architect")).toBeInTheDocument();
    expect(screen.getByText("evidence")).toBeInTheDocument();
  });

  it("renders empty state when no steps", () => {
    render(<ThinkingTracesPanel steps={[]} />);
    expect(screen.getByText("Waiting for agent activity...")).toBeInTheDocument();
  });
});
