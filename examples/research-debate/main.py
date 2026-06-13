"""Research Debate using mCTAgents."""

from mctagents_sdk import MCTAgentsClient

def main():
    client = MCTAgentsClient(base_url="http://localhost:8080")

    problem = (
        "Evaluate the evidence for and against using transformer-based models "
        "for code generation. Consider accuracy, safety, and productivity impacts."
    )

    print("Starting research debate...")
    run = client.create_run(problem=problem, mode="deep_social_reasoning")

    for event in client.stream_events(run.run_id):
        if event.type == "run_completed":
            break
        agent = f"[{event.agent_id}] " if event.agent_id else ""
        print(f"{agent}{event.type}")

    # Get final claims
    claims = client.get_claims(run.run_id)
    print(f"\nTotal claims: {len(claims)}")
    for claim in claims:
        print(f"  [{claim['status']}] {claim['text'][:80]}...")

if __name__ == "__main__":
    main()
