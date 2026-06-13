# Evidence Verification and RAG Layer

## 1. Evidence principle

mCTAgents should treat evidence as a first-class object. Evidence is not just text inserted into a prompt. It is a traceable, scoreable, reusable object that supports or attacks claims.

## 2. Evidence source types

```text
uploaded_document
official_documentation
web_source
academic_paper
github_repository
code_execution_result
database_result
internal_memory
human_confirmation
benchmark_result
```

## 3. Retrieval flow

```text
Claim requires evidence
  -> Evidence Agent creates search plan
  -> query rewriting / decomposition
  -> retrieve documents/web/tool outputs
  -> rerank evidence
  -> summarize evidence
  -> attach to claim
  -> score reliability
  -> expose provenance to UI
```

## 4. Evidence reliability scoring

```json
{
  "source_authority": 0.9,
  "recency": 0.8,
  "specificity": 0.85,
  "independence": 0.75,
  "retrieval_confidence": 0.82,
  "overall": 0.83
}
```

## 5. RAG architecture

MVP:

```text
Upload -> Parse -> Chunk -> Embed -> Store in Qdrant -> Retrieve top-k -> Attach evidence
```

Enhanced:

```text
Query planning -> hybrid retrieval -> reranking -> citation extraction -> claim-evidence matching -> provenance graph
```

Advanced:

```text
GraphRAG / entity graph -> support/attack graph -> source reliability memory -> contradiction detection
```

## 6. Document chunking strategy

```yaml
chunking:
  default_chunk_size_tokens: 600
  overlap_tokens: 80
  preserve_headings: true
  preserve_tables: true
  metadata:
    - document_id
    - page
    - section
    - source_type
    - uploaded_by
```

## 7. Evidence policies

```yaml
evidence_policy:
  high_confidence_claims: required
  architecture_decisions: recommended
  factual_current_claims: required
  subjective_opinions: optional
  safety_or_security_claims: required
```

## 8. Anti-hallucination rule

A final answer may include unsupported claims, but they must be labeled:

```text
Supported: backed by evidence
Reasoned: inferred from evidence and logic
Uncertain: plausible but not verified
Rejected: considered but not selected
```
