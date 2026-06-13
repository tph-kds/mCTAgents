# Sprint 06: Frontend

**Duration:** Days 15-30 | **Goal:** Studio UI with real-time debate visualization

## Tasks

### Day 15-17: Project Setup + Core Components
- [ ] Initialize Next.js with App Router
- [ ] Configure Tailwind CSS + shadcn/ui
- [ ] Create `layout.tsx` with navigation
- [ ] Create `NewSessionForm` component
- [ ] Create `AgentSocietyBar` component
- [ ] Create API client (`lib/api.ts`)
- [ ] Create TypeScript types (`lib/types.ts`)

### Day 18-20: SSE Integration + Timeline
- [ ] Implement `useSSE` hook for real-time events
- [ ] Implement `useRun` hook for run state
- [ ] Create `DebateTimeline` component
- [ ] Create `ObjectionCard` component
- [ ] Create `RevisionDiff` component
- [ ] Connect SSE events to UI updates

### Day 21-23: Claim Graph + Evidence
- [ ] Install React Flow
- [ ] Create `ClaimGraph` component with nodes/edges
- [ ] Create `ClaimNode` component
- [ ] Create `EvidenceBoard` component
- [ ] Create `EvidenceCard` component
- [ ] Implement claim graph layout algorithm

### Day 24-26: Judge + Final Answer
- [ ] Create `JudgeScorePanel` component
- [ ] Create `FinalAnswerPanel` component
- [ ] Create `RunReplayControls` component
- [ ] Implement run detail page (`/runs/[runId]`)
- [ ] Implement run list page (`/runs`)

### Day 27-28: Dev Tools + Polish
- [ ] Create `EventInspector` component (dev mode)
- [ ] Create `TraceViewer` component (dev mode)
- [ ] Add loading states and error handling
- [ ] Make all components responsive
- [ ] Add keyboard shortcuts

### Day 29-30: Testing + Polish
- [ ] Write component tests with React Testing Library
- [ ] Write hook tests with mock EventSource
- [ ] Test full page render with mock API
- [ ] Performance optimization (memoization, lazy loading)
- [ ] Accessibility audit

## Definition of Done
- [ ] New session form creates a run
- [ ] SSE connection established and events displayed
- [ ] Claim graph renders with zoom/pan
- [ ] Evidence board shows supporting/attacking evidence
- [ ] Debate timeline shows chronological events
- [ ] Final answer panel displays synthesized answer
- [ ] All components responsive

## Risks
- **React Flow complexity:** Start with simple layout, optimize later
- **SSE reconnection:** Implement automatic reconnection

## Retro Notes
- _To be filled after sprint completion_
