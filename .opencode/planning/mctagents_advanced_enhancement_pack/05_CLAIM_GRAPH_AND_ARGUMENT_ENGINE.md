# Claim Graph and Argument Engine

## 1. Purpose

The claim graph is the visual and data backbone of mCTAgents. It turns agent reasoning into a structured graph that users and developers can inspect.

## 2. Graph nodes

```text
ProblemFrame
Claim
Evidence
Objection
Revision
Decision
FinalAnswer
ToolCall
Source
Agent
```

## 3. Graph edges

```text
Agent PROPOSED Claim
Evidence SUPPORTS Claim
Objection ATTACKS Claim
Claim REVISED_INTO Claim
Judge ACCEPTED Claim
Judge REJECTED Claim
FinalAnswer USES Claim
ToolCall PRODUCED Evidence
Source BACKS Evidence
```

## 4. Example graph

```text
Problem: Build mCTAgents
  └── Claim A: Protocol-first architecture
        ├── supported_by Evidence 1: MCP shows need for standardized integration
        ├── attacked_by Objection 1: protocol-first can slow MVP
        └── revised_into Claim B: minimal protocol first, adapters later
              └── accepted_by Judge
```

## 5. Storage approach

For MVP, store graph entities in PostgreSQL tables and reconstruct graph views by joins. Do not start with Neo4j unless graph traversal becomes central.

Recommended MVP tables:

```sql
claim_nodes
argument_edges
evidence_nodes
objection_nodes
revision_nodes
decision_nodes
```

## 6. Graph API

```http
GET /v1/runs/{run_id}/claim-graph
GET /v1/claims/{claim_id}/lineage
GET /v1/claims/{claim_id}/support
GET /v1/claims/{claim_id}/objections
```

## 7. UI behaviors

The frontend should support:

```text
- zoomable graph
- filter by accepted/rejected/challenged claims
- click claim to see evidence and objections
- replay graph changes over time
- compare original vs revised claims
- export reasoning graph as JSON/Markdown
```

## 8. Quality value

The claim graph makes mCTAgents different from chat UIs. Users can see not only the final answer, but also the social reasoning path that produced it.
