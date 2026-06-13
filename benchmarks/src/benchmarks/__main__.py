"""CLI entry point for mCTAgents benchmarks."""

import argparse
import sys
from pathlib import Path

from benchmarks.runner import BenchmarkRunner
from benchmarks.leaderboard import Leaderboard


def main():
    parser = argparse.ArgumentParser(description="mCTAgents Benchmark Suite")
    sub = parser.add_subparsers(dest="command")

    # run command
    run_parser = sub.add_parser("run", help="Run a specific task or all tasks")
    run_parser.add_argument("--task", type=str, help="Task file path (YAML)")
    run_parser.add_argument("--tasks-dir", type=str, default="tasks", help="Directory with task files")
    run_parser.add_argument("--api-url", type=str, default="http://localhost:8080", help="API URL")
    run_parser.add_argument("--all", action="store_true", help="Run all tasks")

    # leaderboard command
    lb_parser = sub.add_parser("leaderboard", help="Show leaderboard")
    lb_parser.add_argument("--results-dir", type=str, default="results", help="Results directory")
    lb_parser.add_argument("--top", type=int, default=10, help="Number of entries to show")
    lb_parser.add_argument("--export", type=str, help="Export to markdown file")

    args = parser.parse_args()

    if args.command == "run":
        runner = BenchmarkRunner(api_url=args.api_url)

        if args.all:
            tasks = runner.load_tasks(args.tasks_dir)
            print(f"Running {len(tasks)} tasks...")
            for task in tasks:
                print(f"\n--- {task['id']} ---")
                result = runner.run_task(task)
                print(f"  Score: {result.mct_score:.3f}")
                print(f"  Latency: {result.latency_ms:.0f}ms")
                print(f"  Claims: {result.claims_count}")

                lb = Leaderboard(results_dir="results")
                lb.add_result(result)
            print("\nAll tasks completed. Run 'benchmark leaderboard' to see results.")
        elif args.task:
            task = runner.load_task(args.task)
            result = runner.run_task(task)
            print(f"Task: {result.task_id}")
            print(f"Score: {result.mct_score:.3f}")
            print(f"Latency: {result.latency_ms:.0f}ms")
            print(f"Claims: {result.claims_count}")

            lb = Leaderboard(results_dir="results")
            lb.add_result(result)
        else:
            run_parser.print_help()

    elif args.command == "leaderboard":
        lb = Leaderboard(results_dir=args.results_dir)
        entries = lb.get_top(args.top)

        if not entries:
            print("No results found. Run 'benchmark run --all' first.")
            sys.exit(0)

        print(f"{'Rank':<6}{'Task':<30}{'Score':<10}{'Latency':<12}{'Claims':<8}")
        print("-" * 66)
        for i, e in enumerate(entries, 1):
            print(f"{i:<6}{e['task_id']:<30}{e['mct_score']:<10.3f}{e['latency_ms']:<12.0f}{e['claims']:<8}")

        if args.export:
            md = lb.export_markdown()
            Path(args.export).write_text(md)
            print(f"\nExported to {args.export}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
