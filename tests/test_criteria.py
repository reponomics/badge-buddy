from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "support"))

from criteria_records import RECORDS  # noqa: E402
from ossf_review.criteria import CriteriaCatalog  # noqa: E402


class CriteriaCatalogTests(unittest.TestCase):
    def test_flat_responses_are_bucketed_and_baseline_aliases_merge(self) -> None:
        result = CriteriaCatalog(RECORDS).classify_flat(
            {
                "name": "Example",
                "description_good_status": "Met",
                "OSPS-AC-01.01_status": "?",
                "osps_ac_01_01_justification": "Needs review",
                "not_a_criterion_status": "Met",
            }
        )
        self.assertEqual(result["passing"]["description_good"], {"status": "Met"})
        self.assertEqual(
            result["baseline-1"]["osps_ac_01_01"],
            {"status": "?", "justification": "Needs review"},
        )
        self.assertNotIn("not_a_criterion", result["passing"])

    def test_metal_criteria_follow_form_sections_and_keep_server_order_within(
        self,
    ) -> None:
        catalog = CriteriaCatalog({"passing": RECORDS["passing"]})
        self.assertEqual(
            [
                ("Basics", "contribution"),
                ("Basics", "description_good"),
                ("Basics", "interact"),
                ("Basics", "sites_https"),
                ("Change Control", "repo_public"),
                ("Reporting", "report_process"),
                ("Quality", "build"),
                ("Security", "vulnerabilities_fixed_60_days"),
                ("Analysis", "dynamic_analysis"),
            ],
            [
                (criterion.form_section, criterion.id)
                for criterion in catalog.section("passing")
            ],
        )

    def test_unrecognized_form_section_sorts_last_and_baseline_order_is_unchanged(
        self,
    ) -> None:
        extra = {
            **RECORDS["passing"][0],
            "criterion_id": "new_one",
            "category": "New Section",
        }
        metal = CriteriaCatalog({"passing": [extra, *RECORDS["passing"]]})
        self.assertEqual("new_one", metal.section("passing")[-1].id)

        baseline = CriteriaCatalog(
            {"baseline-3": list(reversed(RECORDS["baseline-3"]))}
        )
        self.assertEqual(
            ["osps_vm_04_02", "osps_ac_04_02"],
            [criterion.id for criterion in baseline.section("baseline-3")],
        )

    def test_record_fields_map_to_display_names(self) -> None:
        catalog = CriteriaCatalog(RECORDS)
        baseline = catalog.section("baseline-1")[0]
        self.assertEqual(
            ("osps_ac_01_01", "OSPS-AC-01.01"), (baseline.id, baseline.display_id)
        )
        metal = catalog.section("gold")[0]
        self.assertEqual(metal.id, metal.display_id)
        self.assertEqual("MUST", metal.requirement)

    def test_only_loaded_sections_are_available(self) -> None:
        catalog = CriteriaCatalog({"silver": RECORDS["silver"]})
        self.assertEqual(("silver",), catalog.section_names)
        with self.assertRaises(KeyError):
            catalog.section("gold")
        with self.assertRaises(ValueError):
            CriteriaCatalog({"bronze": []})

    def test_malformed_records_are_rejected(self) -> None:
        good = RECORDS["passing"][0]
        for change in (
            {"criterion_id": ""},
            {"criterion_id": "not a fragment"},
            {"requirement": "MAY"},
            {"details": 3},
            {"aliases": "OSPS-AC-01.01"},
            {"na_allowed": "yes"},
            {"category": None},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                CriteriaCatalog({"passing": [{**good, **change}]})


if __name__ == "__main__":
    unittest.main()
