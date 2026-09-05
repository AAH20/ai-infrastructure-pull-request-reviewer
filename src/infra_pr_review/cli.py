from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import review
from .report import markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Review normalized infrastructure pull-request evidence")
    parser.add_argument("bundle", help="Path to normalized review bundle JSON")
    parser.add_argument("--output", default="infra-pr-review.md")
    parser.add_argument("--json-output")
    parser.add_argument("--fail-on", choices=("block", "review", "never"), default="block")
    args = parser.parse_args()

    with Path(args.bundle).open(encoding="utf-8") as handle:
        result = review(json.load(handle))
    Path(args.output).write_text(markdown(result) + "\n", encoding="utf-8")
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(result.as_dict(), indent=2) + "\n", encoding="utf-8")
    print(f"{result.decision} score={result.score:.1f} receipt={result.receipt}")
    if args.fail_on == "block" and result.decision == "BLOCK":
        return 2
    if args.fail_on == "review" and result.decision != "APPROVE":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

