# Agent Skills and Tool Knowledge Base

## 1. Why skills matter

Open-source agent ecosystems increasingly use skills, tools, and reusable workflows. mCTAgents should support skills, but skills should be subordinate to the social reasoning protocol.

## 2. Skill types

```text
reasoning_skill
research_skill
security_review_skill
code_review_skill
architecture_design_skill
document_analysis_skill
benchmark_skill
workflow_skill
```

## 3. Skill contract

```yaml
id: architecture_tradeoff_analysis
name: Architecture Trade-off Analysis
version: 0.1.0
inputs:
  - problem_frame
  - constraints
outputs:
  - claims
  - tradeoffs
  - risks
compatible_agents:
  - architect_agent
  - critic_agent
required_tools:
  - document_search
risk_level: low
```

## 4. Tool knowledge base

When many tools exist, agents should not see all tools directly. Use retrieval over tool descriptions.

```text
User task -> tool query -> retrieve top relevant tools -> policy filter -> agent tool set
```

## 5. Skill marketplace path

```text
v0.1 built-in skills
v0.2 community skills folder
v0.3 validated skills registry
v0.4 signed/plugin metadata
v0.5 skill benchmark badges
```

## 6. Quality criteria for official skills

```text
clear input/output contract
safe permission profile
test cases
example run
benchmark score
maintainer owner
version history
```
