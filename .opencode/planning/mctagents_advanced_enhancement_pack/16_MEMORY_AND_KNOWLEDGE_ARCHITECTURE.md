# Memory and Knowledge Architecture

## 1. Memory types

mCTAgents needs several memory scopes.

```text
Run memory: temporary state for a single run
Project memory: documents, decisions, previous claim graphs
Agent memory: performance and prompt improvement data
User preference memory: optional, explicit, minimal
Global community memory: reusable public examples and benchmarks
```

## 2. Memory storage

```text
Postgres: structured objects, claims, decisions, metadata
Qdrant/pgvector: semantic document chunks and memory retrieval
Object storage: uploaded files, exports, logs
Redis: short-lived cache and stream state
```

## 3. Project memory examples

```text
architecture decisions
accepted claims from previous runs
rejected alternatives
known constraints
uploaded documents
team style preferences
benchmark results
```

## 4. Memory retrieval policy

```yaml
memory_policy:
  retrieve_project_memory: true
  retrieve_user_memory: false_by_default
  retrieve_global_examples: true
  max_memory_items: 8
  require_source_labels: true
```

## 5. Claim graph memory

Accepted decisions from previous runs can become reusable knowledge:

```text
Decision -> ProjectMemoryItem -> future EvidenceCandidate
```

But old decisions must include timestamps and context because they may become outdated.

## 6. Forgetting and pruning

```text
expire low-value run memories
archive old traces
deduplicate similar claims
prune unsupported memories
allow project-level deletion
```

## 7. Memory safety

```text
- never mix tenant memory
- cite memory source
- label memory as historical, not absolute truth
- avoid storing sensitive data unless required
- allow export and deletion
```
