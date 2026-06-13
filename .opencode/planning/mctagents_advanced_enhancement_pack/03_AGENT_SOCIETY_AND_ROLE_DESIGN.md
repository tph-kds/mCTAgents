# Agent Society and Role Design

## 1. Agent society concept

mCTAgents should dynamically form a temporary society of agents around a problem. The society should not be fixed for every request. A software architecture question needs different roles from a research, legal, product, or data science question.

## 2. Base society

The minimum useful society:

```text
Problem Framer
Solution Architect
Evidence Agent
Critic Agent
Judge/Synthesizer
```

This 5-agent setup is enough for MVP.

## 3. Advanced society roles

### Problem Framer
Responsibilities:
- normalize the user problem
- identify assumptions
- detect missing information
- define success criteria
- set risk level and workflow mode

### Society Planner
Responsibilities:
- choose agents based on domain
- set debate policy
- set evidence requirement
- estimate expected latency/cost

### Architect Agent
Responsibilities:
- propose solution structure
- create implementation claims
- compare alternatives
- output explicit trade-offs

### Evidence Agent
Responsibilities:
- retrieve from documents, web, memory, tools, code, or official docs
- attach evidence to claims
- label unsupported claims
- score source reliability

### Critic Agent
Responsibilities:
- attack weak assumptions
- detect contradictions
- identify missing constraints
- request claim revisions

### Security/Risk Agent
Responsibilities:
- identify safety, privacy, prompt-injection, tool, infrastructure, and deployment risks
- classify impact and probability
- propose mitigations

### Judge Agent
Responsibilities:
- score claims
- select accepted/rejected claims
- identify unresolved uncertainty
- decide whether more debate is needed

### Synthesizer Agent
Responsibilities:
- convert accepted claims into a clear final answer
- include rejected alternatives, risks, and next steps

## 4. Society formation algorithm

```python
def choose_society(problem_frame):
    society = ["problem_framer", "evidence_agent", "critic_agent", "judge_agent", "synthesizer"]

    if problem_frame.domain in ["software", "system_architecture", "ai_engineering"]:
        society += ["solution_architect", "backend_agent", "security_agent"]

    if problem_frame.requires_business_decision:
        society += ["product_agent", "cost_agent", "user_value_agent"]

    if problem_frame.requires_research:
        society += ["literature_agent", "methodology_agent", "skeptic_agent"]

    return deduplicate_and_budget(society)
```

## 5. Avoiding agent bloat

More agents do not automatically mean better reasoning. The system should escalate only when needed:

```text
Low complexity -> 1-2 agents
Medium complexity -> 3-5 agents
High complexity -> 5-8 agents
Critical/high-risk -> add verifier, risk, and judge ensemble
```

## 6. Agent contract

Each agent must define:

```yaml
id: security_agent
capabilities:
  - risk_analysis
  - tool_policy_review
  - data_privacy_review
inputs:
  - problem_frame
  - claims
  - evidence
outputs:
  - objections
  - mitigation_claims
  - risk_register
budget:
  max_tokens: 1200
  max_tool_calls: 3
```
