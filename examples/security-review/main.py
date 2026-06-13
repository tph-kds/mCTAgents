"""Security Review using mCTAgents."""

from mctagents_sdk import MCTAgentsClient

def main():
    client = MCTAgentsClient(base_url="http://localhost:8080")

    problem = (
        "Conduct a security review of our authentication system. "
        "We use JWT tokens with RSA-256 signing. Sessions last 24 hours. "
        "We have 500K active users. Previous audit found no critical issues."
    )

    print("Starting security review...")
    run = client.create_run(problem=problem, mode="deep_social_reasoning")

    for event in client.stream_events(run.run_id):
        if event.type == "run_completed":
            break
        agent = f"[{event.agent_id}] " if event.agent_id else ""
        print(f"{agent}{event.type}")

if __name__ == "__main__":
    main()
