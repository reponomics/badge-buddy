"""Criterion records in the shape of the MCP server's ``get_criteria`` full detail.

The texts are synthetic. Each level has a few records, returned in ID order as
the server returns them.
"""

from __future__ import annotations

from typing import Any


def _record(
    level: str,
    criterion_id: str,
    category: str,
    requirement: str = "MUST",
    **flags: bool,
) -> dict[str, Any]:
    alias = []
    if criterion_id.startswith("osps_"):
        family, control, item = criterion_id.removeprefix("osps_").split("_")
        alias = [f"OSPS-{family.upper()}-{control}.{item}"]
    return {
        "criterion_id": criterion_id,
        "level": level,
        "description": f"The project {requirement} do what <em>{criterion_id}</em> describes.",
        "details": None
        if requirement == "SUGGESTED"
        else f"<p>Details for {criterion_id}.</p>",
        "category": category,
        "requirement": requirement,
        "status_field": f"{criterion_id}_status",
        "justification_field": f"{criterion_id}_justification",
        "aliases": alias,
        "na_allowed": flags.get("na_allowed", False),
        "na_justification_required": flags.get("na_justification_required", False),
        "met_justification_required": flags.get("met_justification_required", False),
        "met_url_required": flags.get("met_url_required", False),
    }


RECORDS: dict[str, list[dict[str, Any]]] = {
    "passing": [
        _record("passing", "build", "Quality", na_allowed=True),
        _record(
            "passing",
            "contribution",
            "Basics",
            met_justification_required=True,
            met_url_required=True,
        ),
        _record("passing", "description_good", "Basics"),
        _record("passing", "dynamic_analysis", "Analysis", "SUGGESTED"),
        _record("passing", "interact", "Basics"),
        _record(
            "passing",
            "report_process",
            "Reporting",
            met_justification_required=True,
            met_url_required=True,
        ),
        _record(
            "passing",
            "repo_public",
            "Change Control",
            met_justification_required=True,
            met_url_required=True,
        ),
        _record("passing", "sites_https", "Basics"),
        _record(
            "passing", "vulnerabilities_fixed_60_days", "Security", na_allowed=True
        ),
    ],
    "silver": [
        _record("silver", "achieve_passing", "Basics"),
        _record("silver", "dco", "Basics", "SHOULD", met_justification_required=True),
        _record("silver", "test_statement_coverage80", "Quality", na_allowed=True),
    ],
    "gold": [
        _record("gold", "achieve_silver", "Basics"),
        _record(
            "gold", "two_person_review", "Quality", met_justification_required=True
        ),
    ],
    "baseline-1": [
        _record(
            "baseline-1",
            "osps_ac_01_01",
            "Access Control",
            na_allowed=True,
            na_justification_required=True,
        ),
        _record(
            "baseline-1",
            "osps_do_01_01",
            "Documentation",
            na_allowed=True,
            na_justification_required=True,
        ),
    ],
    "baseline-2": [
        _record(
            "baseline-2",
            "osps_ac_04_01",
            "Access Control",
            na_allowed=True,
            na_justification_required=True,
        ),
        _record(
            "baseline-2",
            "osps_do_06_01",
            "Documentation",
            na_allowed=True,
            na_justification_required=True,
        ),
    ],
    "baseline-3": [
        _record(
            "baseline-3",
            "osps_ac_04_02",
            "Access Control",
            na_allowed=True,
            na_justification_required=True,
        ),
        _record(
            "baseline-3",
            "osps_vm_04_02",
            "Vulnerability Management",
            na_allowed=True,
            na_justification_required=True,
        ),
    ],
}
