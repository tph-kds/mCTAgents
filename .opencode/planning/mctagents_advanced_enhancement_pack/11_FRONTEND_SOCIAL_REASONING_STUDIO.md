# Frontend Social Reasoning Studio

## 1. Product goal

The frontend should make users feel that they are watching a society of agents think together. But it must not expose hidden chain-of-thought. It should show structured summaries, claims, objections, evidence, decisions, and final outputs.

## 2. Main screens

```text
Home Dashboard
New Reasoning Session
Live Social Reasoning Workspace
Claim Graph View
Evidence Board
Debate Timeline
Judge Decision Panel
Final Answer Page
Evaluation Dashboard
Agent Society Builder
Developer Integration Playground
```

## 3. Live workspace layout

```text
┌─────────────────────────────────────────────┐
│ Problem Frame                               │
├─────────────────────────────────────────────┤
│ Agent Society                               │
│ Framer | Architect | Evidence | Critic | Judge│
├───────────────────────┬─────────────────────┤
│ Claim Graph            │ Evidence Board      │
├───────────────────────┴─────────────────────┤
│ Debate Timeline                              │
├─────────────────────────────────────────────┤
│ Final Answer / Judge Decision                │
└─────────────────────────────────────────────┘
```

## 4. Core components

```text
AgentCard
AgentSocietyMap
ClaimNode
EvidenceCard
ObjectionCard
RevisionDiff
JudgeScorePanel
DebateTimeline
RunReplayControls
FinalAnswerPanel
EvaluationRadar
```

## 5. User experience principle

Show what matters:

```text
- what was claimed
- why it was supported
- who challenged it
- how it changed
- why the final decision was chosen
```

Do not show raw chain-of-thought. Show safe, structured reasoning artifacts.

## 6. Developer UI

Developers need:

```text
- API key page
- SDK snippets
- event inspector
- policy editor
- agent configuration editor
- model provider settings
- tool permission settings
- run trace viewer
```

## 7. Future 3D UI

A 3D agent workspace can become a later “wow” feature, but the first impressive UI should be a **claim graph + evidence board + debate replay**. This is more useful and easier to build.
