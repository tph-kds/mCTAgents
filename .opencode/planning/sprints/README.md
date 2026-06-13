# Sprints

This folder contains sprint planning, tracking, and retrospective notes.

## Structure

```
sprints/
├── README.md              # This file
├── SPRINT_00_SETUP.md     # Sprint 0: Project setup
├── SPRINT_01_PROTOCOL.md  # Sprint 1: Core protocol
├── SPRINT_02_GATEWAY.md   # Sprint 2: Model gateway
├── SPRINT_03_ENGINE.md    # Sprint 3: Reasoning engine
├── SPRINT_04_API.md       # Sprint 4: API gateway
├── SPRINT_05_EVIDENCE.md  # Sprint 5: Evidence service
├── SPRINT_06_UI.md        # Sprint 6: Frontend
├── SPRINT_07_SDK.md       # Sprint 7: SDKs
├── SPRINT_08_BENCH.md     # Sprint 8: Benchmarks
├── SPRINT_09_PROD.md      # Sprint 9: Production
├── SPRINT_10_LAUNCH.md    # Sprint 10: Community launch
└── retrospective/         # Sprint retrospectives
```

## Sprint Cadence

- **Duration:** 1 week (5 working days)
- **Planning:** Monday morning
- **Daily standup:** Async via PR comments
- **Review:** Friday afternoon
- **Retrospective:** Friday afternoon

## Sprint Template

Use `SPRINT_XX_NAME.md` template for each sprint:

```markdown
# Sprint XX: Name

**Duration:** Day X-Y | **Goal:** ...

## Tasks
- [ ] Task 1
- [ ] Task 2

## Definition of Done
- [ ] All tests pass
- [ ] Lint passes
- [ ] Code reviewed
- [ ] Documentation updated

## Risks
- Risk 1: Mitigation

## Retro Notes
- What went well
- What to improve
```
