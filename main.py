"""CLI entry point for the systems-theory-task pipeline.

Minimal runner that will be extended as pipeline components are implemented.
"""
import argparse


def main():
    parser = argparse.ArgumentParser(description="Run systems theory pipeline")
    parser.add_argument("--action", choices=["run", "status"], default="status")
    args = parser.parse_args()
    if args.action == "status":
        print("Pipeline scaffold is ready. Use --action run when pipeline components are implemented.")
    else:
        print("Running pipeline (not yet implemented).")


if __name__ == "__main__":
    main()
