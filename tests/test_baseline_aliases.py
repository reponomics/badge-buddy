"""Keep Baseline display-ID fields compatible with the passive preview board."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "support"))
from criteria_records import RECORDS
from ossf_review.board import build_board_payload
from ossf_review.criteria import CriteriaCatalog
from ossf_review.fields import normalize_assessment_fields


class BaselineAliasesTest(unittest.TestCase):
    def test_display_and_canonical_fields_render_identically(self):
        catalog = CriteriaCatalog(RECORDS)
        for level in ("baseline-1", "baseline-2", "baseline-3"):
            criterion = catalog.section(level)[0]
            canonical = {
                f"{criterion.id}_status": "Met",
                f"{criterion.id}_justification": "Project explanation",
            }
            display = {
                f"{criterion.display_id}_status": "Met",
                f"{criterion.display_id}_justification": "Project explanation",
            }
            with self.subTest(level=level):
                self.assertNotEqual(criterion.id, criterion.display_id)
                self.assertEqual(canonical, normalize_assessment_fields(display))
                board = build_board_payload(
                    display, project_id="31", section=level, catalog=catalog
                )
                self.assertEqual(
                    {"status": "Met", "justification": "Project explanation"},
                    board["answers"][criterion.id],
                )

    def test_conflicting_aliases_are_not_silently_chosen(self):
        with self.assertRaises(ValueError):
            normalize_assessment_fields(
                {"OSPS-AC-01.01_status": "Met", "osps_ac_01_01_status": "?"}
            )
