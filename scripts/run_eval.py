import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluation.harness import EvalHarness
from src.models.llm_client import build_client


def main() -> int:
    parser = argparse.ArgumentParser(description="Run models on the benchmark")
    parser.add_argument("--questions", default="data/gold/questions.json")
    parser.add_argument("--models", required=True,
                        help="comma-separated model ids, e.g. gpt-4o-2024-08-06,claude-sonnet-4-20250514")
    parser.add_argument("--out", default="data/results/records.jsonl")
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--max-tokens", type=int, default=1024)
    args = parser.parse_args()

    models = {}
    for spec in [m.strip() for m in args.models.split(",") if m.strip()]:
        client = build_client(spec, max_tokens=args.max_tokens)
        models[spec] = client

    harness = EvalHarness(models, args.out, delay_s=args.delay)
    summary = harness.run(args.questions)
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
