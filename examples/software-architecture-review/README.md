# Software Architecture Review Example

This example shows how to use mCTAgents to review a software architecture decision.

## Setup

1. Start the services: `make docker-up`
2. Run the example: `python main.py`

## What Happens

1. ProblemFramer normalizes the architecture question
2. Architect proposes claims about the architecture
3. EvidenceAgent finds supporting documentation
4. Critic challenges weak claims
5. Judge scores and accepts/rejects claims
6. Synthesizer creates a final recommendation
