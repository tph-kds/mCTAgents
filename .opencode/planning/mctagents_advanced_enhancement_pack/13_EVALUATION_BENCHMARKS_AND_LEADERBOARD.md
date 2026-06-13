# Evaluation, Benchmarks, and Leaderboard

## 1. Why evaluation is essential

mCTAgents must prove that social reasoning improves answer quality. Without evaluation, the project risks becoming an impressive UI with unverified reasoning.

## 2. Evaluation tracks

### Track A: Single-agent vs Social-agent

Compare a strong single-agent baseline against mCTAgents on the same problems.

Metrics:

```text
correctness
completeness
logical consistency
actionability
risk awareness
clarity
```

### Track B: Evidence grounding

Metrics:

```text
unsupported claim rate
evidence relevance
citation precision
source diversity
source reliability
claim-evidence alignment
```

### Track C: Debate quality

Metrics:

```text
useful objection rate
claim revision improvement
repeated argument rate
problem drift score
consensus quality
critic impact score
```

### Track D: Production efficiency

Metrics:

```text
latency
tokens
model calls
tool calls
retry count
failure rate
cost per useful answer
```

## 3. Evaluation pipeline

```text
Run task with single agent
Run task with mCTAgents
Collect final answers and claim graph
Score with rule-based validators
Score with LLM judge
Optional human review
Compare metrics
Store results
Show leaderboard
```

## 4. Judge calibration

Use multiple evaluation methods:

```text
- deterministic checks
- rubric-based LLM judge
- pairwise comparison
- human feedback
- regression tests
```

## 5. Benchmark dataset structure

```yaml
id: software_architecture_001
problem: "Design a scalable private document QA system."
expected_dimensions:
  - architecture
  - retrieval
  - security
  - observability
  - deployment
rubric:
  correctness: 0.25
  completeness: 0.25
  feasibility: 0.20
  evidence: 0.15
  risk_awareness: 0.15
```

## 6. Public leaderboard

Leaderboard columns:

```text
runtime
model
policy
score
latency
tokens
cost
unsupported_claim_rate
drift_score
```

## 7. Regression gate

Before merging changes:

```text
- run smoke tasks
- validate schemas
- run benchmark subset
- compare against baseline
- block merge if quality drops too much
```
