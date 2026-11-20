"""Render a synthetic mixed-answer board without starting an MCP server."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from criteria_records import RECORDS  # noqa: E402
from ossf_review.board import write_board  # noqa: E402
from ossf_review.criteria import CriteriaCatalog  # noqa: E402


def main() -> None:
    document: dict[str, str] = {}
    statuses = ("Met", "Unmet", "N/A", "?")
    for index, record in enumerate(RECORDS["passing"]):
        document[record["status_field"]] = statuses[index % len(statuses)]
        document[record["justification_field"]] = (
            f"Synthetic answer for {record['criterion_id']}. "
            "Evidence: https://example.org/project."
        )
    write_board(
        document,
        Path(sys.argv[1]),
        project_id="browser-fixture",
        section="passing",
        catalog=CriteriaCatalog(RECORDS),
    )


if __name__ == "__main__":
    main()
