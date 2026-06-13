# STEP 8: Evaluation & Benchmarks

**Timeline:** Days 25-35 | **Complexity:** 4/5 | **Dependencies:** STEPs 1, 3

## Goal

Prove that social reasoning improves answer quality vs single-agent baselines.

## Evaluation Tracks

### Track A: Quality
- Correctness, completeness, logical consistency
- Actionability, risk awareness, clarity

### Track B: Evidence Grounding
- Unsupported claim rate, evidence relevance
- Citation precision, source diversity

### Track C: Debate Quality
- Useful objection rate, revision improvement
- Repeated argument rate, drift score

### Track D: Efficiency
- Latency, tokens, model calls
- Cost per useful answer

## Benchmark Tasks
1. Software architecture review
2. Research debate
3. Security review
4. Product decision
5. Legal analysis

## Scoring Pipeline
```
Task → Run (single-agent) → Score
Task → Run (mCTAgents) → Score
Compare → Improvement metrics
```

## Leaderboard
| Rank | Runtime | Model | Score | Latency | Tokens |
|------|---------|-------|-------|---------|--------|

## Files
```
benchmarks/
├── src/benchmarks/    # Runner, scorers
├── tasks/             # Benchmark definitions
├── results/           # Run results
└── baselines/         # Single-agent baseline
```

## Success Criteria
- [ ] 5+ benchmark tasks defined
- [ ] Single-agent baseline implemented
- [ ] All scorers produce reasonable scores
- [ ] Leaderboard generates correctly
- [ ] End-to-end benchmark run completes
