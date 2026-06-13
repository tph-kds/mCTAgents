# STEP 6: Frontend (Next.js)

**Timeline:** Days 15-30 | **Complexity:** 4/5 | **Dependencies:** STEPs 0, 1, 4

## Goal

Studio UI that makes users feel like they're watching a society of agents think together.

## Tech Stack
- Next.js 14+ (App Router)
- Tailwind CSS + shadcn/ui
- React Flow (claim graph)
- Zod (validation)

## Components

| Component | Purpose |
|-----------|---------|
| NewSessionForm | Create new reasoning run |
| AgentSocietyBar | Show active agents and status |
| DebateTimeline | Chronological event stream |
| ClaimGraph | Interactive claim visualization |
| EvidenceBoard | Supporting/attacking evidence |
| ObjectionCard | Individual objection display |
| RevisionDiff | Before/after claim comparison |
| JudgeScorePanel | Scoring breakdown |
| FinalAnswerPanel | Synthesized answer |
| RunReplayControls | Playback controls |

## SSE Integration
- Custom `useSSE` hook for real-time events
- Event types map to UI updates
- Automatic reconnection

## Key Design Rules
- **No raw reasoning in UI** - Only structured summaries
- **Show claims, not messages** - Claim-centered display
- **Evidence always cited** - Source and reliability shown
- **Risks declared** - Never hide uncertainties

## Files
```
apps/studio/
├── src/app/            # Next.js pages
├── src/components/     # React components
├── src/hooks/          # useSSE, useRun, useClaimGraph
├── src/lib/            # API client, SSE, types
└── tests/
```

## Success Criteria
- [ ] New session form creates a run
- [ ] SSE connection established
- [ ] Claim graph renders with zoom/pan
- [ ] Evidence board shows support/attack
- [ ] Debate timeline shows events
- [ ] Final answer displays correctly
- [ ] All components responsive
