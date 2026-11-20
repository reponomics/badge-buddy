"""Enforce separate statement and branch floors from coverage.py's JSON report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

MINIMUM = 80


def _percentage(totals: dict[str, Any], covered: str, count: str) -> float:
    numerator, denominator = totals[covered], totals[count]
    if (
        type(numerator) is not int
        or type(denominator) is not int
        or not 0 <= numerator <= denominator
    ):
        raise ValueError(f"Invalid coverage counts for {count}.")
    return 100 * numerator / denominator if denominator else 100.0


def percentages(report: dict[str, Any]) -> dict[str, float]:
    """Reject missing measurements rather than treating them as full coverage."""
    if report["meta"].get("branch_coverage") is not True:
        raise ValueError("Branch coverage was not measured.")
    totals = report["totals"]
    statements = _percentage(totals, "covered_lines", "num_statements")
    branches = _percentage(totals, "covered_branches", "num_branches")
    if totals["num_statements"] == 0:
        raise ValueError("No statements were measured.")
    return {"Statement": statements, "Branch": branches}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="coverage.py JSON report")
    args = parser.parse_args(argv)
    try:
        measured = percentages(json.loads(args.report.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"Could not check coverage: {exc}", file=sys.stderr)
        return 1
    for metric, percent in measured.items():
        outcome = "PASS" if percent >= MINIMUM else "FAIL"
        print(f"{metric} coverage: {percent:.2f}% (minimum {MINIMUM}%) — {outcome}")
    return int(any(percent < MINIMUM for percent in measured.values()))


if __name__ == "__main__":
    raise SystemExit(main())
