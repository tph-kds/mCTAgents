"""Software Architecture Review using mCTAgents."""

from mctagents_sdk import MCTAgentsClient

def main():
    client = MCTAgentsClient(base_url="http://localhost:8080")

    problem = (
        "Should we migrate our monolithic Django application to microservices? "
        "We have 50 engineers, growing to 100. The monolith handles 10K requests/second. "
        "We need faster deployment cycles and independent team scaling."
    )

    print("Starting social reasoning run...")
    run = client.create_run(
        problem=problem,
        mode="deep_social_reasoning",
        evidence_policy="required_for_major_claims",
    )
    print(f"Run ID: {run.run_id}")
    print(f"Stream URL: http://localhost:8080{run.events_url}")
    print()

    for event in client.stream_events(run.run_id):
        agent = f"[{event.agent_id}] " if event.agent_id else ""
        print(f"{agent}{event.type}")

        if event.type == "claim_created":
            text = event.payload.get("text", "")
            confidence = event.payload.get("confidence", 0)
            print(f"  Claim: {text}")
            print(f"  Confidence: {confidence:.0%}")

        if event.type == "objection_created":
            reason = event.payload.get("reason", "")
            severity = event.payload.get("severity", "")
            print(f"  Objection ({severity}): {reason}")

        if event.type == "judge_scored":
            accepted = len(event.payload.get("accepted_claim_ids", []))
            rejected = len(event.payload.get("rejected_claim_ids", []))
            print(f"  Verdict: {accepted} accepted, {rejected} rejected")

        if event.type == "final_answer_created":
            answer = event.payload.get("answer_text", "")
            print(f"\n{'='*60}")
            print("FINAL ANSWER:")
            print(answer)
            print('='*60)

        if event.type == "run_completed":
            break

    print("\nDone!")

if __name__ == "__main__":
    main()
