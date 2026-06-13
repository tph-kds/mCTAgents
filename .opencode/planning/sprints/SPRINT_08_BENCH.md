# Sprint 08: Evaluation & Benchmarks

**Duration:** Days 25-35 | **Goal:** Benchmark suite, scoring pipeline, leaderboard

## Tasks

### Day 25-27: Benchmark Infrastructure
- [ ] Initialize `benchmarks/` package
- [ ] Define benchmark task YAML schema
- [ ] Create 5 benchmark tasks:
  - [ ] Software architecture review
  - [ ] Research debate
  - [ ] Security review
  - [ ] Product decision
  - [ ] Legal analysis
- [ ] Implement `BenchmarkRunner` class

### Day 28-30: Scoring Pipeline
- [ ] Implement `CorrectnessScorer`
- [ ] Implement `CompletenessScorer`
- [ ] Implement `ConsistencyScorer`
- [ ] Implement `EvidenceQualityScorer`
- [ ] Implement `DebateQualityScorer`
- [ ] Implement `LLMJudgeScorer` (optional)
- [ ] Write scorer unit tests

### Day 31-32: Baselines + Comparison
- [ ] Implement single-agent baseline
- [ ] Implement comparison logic
- [ ] Calculate improvement metrics
- [ ] Track latency, tokens, cost

### Day 33-34: Leaderboard
- [ ] Implement `Leaderboard` class
- [ ] Implement sorting by multiple criteria
- [ ] Implement Markdown export
- [ ] Implement JSON export
- [ ] Create `make benchmark-smoke` command

### Day 35: Run Benchmarks + Report
- [ ] Run full benchmark suite
- [ ] Analyze results
- [ ] Publish leaderboard
- [ ] Document benchmark methodology

## Definition of Done
- [ ] At least 5 benchmark tasks defined
- [ ] Single-agent baseline implemented
- [ ] All scorers produce reasonable scores
- [ ] Leaderboard generates correctly
- [ ] Benchmark run completes end-to-end

## Risks
- **Model quality affects scores:** Use consistent model versions
- **Benchmark bias:** Include diverse problem types

## Retro Notes
- _To be filled after sprint completion_
