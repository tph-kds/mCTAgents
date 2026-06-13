# Observability, SRE, and Cost Control

## 1. Observability principle

Every reasoning run should be traceable from user request to final answer.

## 2. Trace hierarchy

```text
run_trace
  ├── problem_framing_span
  ├── society_selection_span
  ├── agent_step_span
  │     ├── model_call_span
  │     ├── tool_call_span
  │     └── validation_span
  ├── evidence_retrieval_span
  ├── debate_round_span
  ├── judge_span
  └── final_synthesis_span
```

## 3. Metrics

### System metrics

```text
request_rate
error_rate
p50/p95/p99_latency
queue_depth
worker_utilization
memory_usage
GPU/CPU usage
```

### AI metrics

```text
tokens_in
tokens_out
model_call_count
tool_call_count
retrieval_count
claim_count
objection_count
revision_count
judge_confidence
unsupported_claim_rate
```

### Product metrics

```text
run_completion_rate
user_export_rate
thumbs_up_rate
repeat_usage
sdk_integration_count
time_to_first_event
```

## 4. Cost controls

```yaml
budgets:
  default:
    max_total_tokens: 12000
    max_model_calls: 12
    max_tool_calls: 6
    max_runtime_seconds: 120
  deep:
    max_total_tokens: 40000
    max_model_calls: 32
    max_tool_calls: 16
    max_runtime_seconds: 600
```

## 5. Failure visibility

Every failure should answer:

```text
What failed?
Which agent/tool/model failed?
Was it retried?
Was the output partially recoverable?
What should the user or developer do next?
```

## 6. Operational dashboards

```text
Run health dashboard
Model provider dashboard
Tool failure dashboard
Evidence quality dashboard
Cost dashboard
Benchmark trend dashboard
Security audit dashboard
```

## 7. SLO examples

```text
MVP local: 95% of balanced runs complete under 90 seconds
Production: 99% API availability
Streaming: first event under 2 seconds
Evaluation: benchmark regression under 5% per release
```
