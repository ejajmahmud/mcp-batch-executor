"""Command-line interface for MCP Batch Executor."""
import argparse
from .executor import BatchExecutor

def main():
    parser = argparse.ArgumentParser(description="MCP Batch Executor CLI")
    parser.add_argument("--demo", action="store_true", help="Demonstrate dependency graph batch execution")
    args = parser.parse_args()

    executor = BatchExecutor()
    executor.add_step("fetch_user", "get_user", {"id": 101})
    executor.add_step("fetch_orders", "get_orders", {"user_id": 101})
    executor.add_step("summarize", "summarize_account", {"orders": "$fetch_orders"}, depends_on=["fetch_orders", "fetch_user"])

    stages = executor.resolve_stages()
    print("Resolved execution stages:", stages)

    def mock_runner(tool, args):
        return f"Result of {tool}({args})"

    results = executor.execute(mock_runner)
    print("Batch execution finished. Results:")
    for k, v in results.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
