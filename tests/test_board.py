from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from typing import ClassVar

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = REPOSITORY_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent / "support"))

from criteria_records import RECORDS  # noqa: E402
from ossf_review.board import (  # noqa: E402
    build_board_payload,
    plain_text,
    render_board,
    write_board,
)
from ossf_review.criteria import CriteriaCatalog  # noqa: E402


class PassiveBoardTests(unittest.TestCase):
    catalog: ClassVar[CriteriaCatalog]

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = CriteriaCatalog(RECORDS)

    def test_payload_groups_canonical_statuses_into_buckets(self) -> None:
        payload = build_board_payload(
            {
                "description_good_status": "Met",
                "description_good_justification": "Repository evidence.",
                "interact_status": "Unmet",
                "sites_https_status": "N/A",
                "sites_https_justification": "No project website exists.",
            },
            project_id="31",
            section="passing",
            catalog=self.catalog,
        )

        counts = {bucket["key"]: bucket["count"] for bucket in payload["buckets"]}
        ordered_ids = [criterion.id for criterion in self.catalog.section("passing")]
        self.assertEqual(
            ordered_ids, [criterion["id"] for criterion in payload["criteria"]]
        )
        self.assertEqual(len(ordered_ids), payload["total"])
        self.assertEqual({"needs_input", "unmet", "na", "met"}, set(counts))
        classified_ids = [
            identifier
            for bucket in payload["buckets"]
            for identifier in bucket["criterionIds"]
        ]
        self.assertCountEqual(ordered_ids, classified_ids)
        self.assertEqual(payload["total"], sum(counts.values()))
        self.assertEqual(1, counts["met"])
        self.assertEqual(1, counts["unmet"])
        self.assertEqual(1, counts["na"])
        self.assertEqual(payload["total"] - 3, counts["needs_input"])
        self.assertEqual("Met", payload["answers"]["description_good"]["status"])

    def test_criterion_html_preserves_readable_text(self) -> None:
        cases = (
            ("", ""),
            ("  Plain\n text\t here  ", "Plain text here"),
            ("<p>A &amp; B</p><p>Next<br>line</p>", "A & B Next line"),
            (
                'Use <a href="https://example.com">public</a> evidence.',
                "Use public evidence.",
            ),
            ("<ul><li>One</li><li><em>Two</em></li></ul>", "One Two"),
        )
        for markup, expected in cases:
            with self.subTest(markup=markup):
                self.assertEqual(expected, plain_text(markup))

    def test_payload_shows_criterion_text_without_markup(self) -> None:
        payload = build_board_payload(
            {}, project_id="31", section="silver", catalog=self.catalog
        )
        criterion = next(row for row in payload["criteria"] if row["id"] == "dco")
        self.assertEqual(
            "The project SHOULD do what dco describes.", criterion["description"]
        )
        self.assertEqual("Details for dco.", criterion["details"])
        self.assertEqual("SHOULD", criterion["category"])
        self.assertTrue(criterion["metJustificationRequired"])

    def test_board_embeds_bundled_styles_and_script(self) -> None:
        payload = build_board_payload(
            {"description_good_status": "Met"},
            project_id="31",
            section="passing",
            catalog=self.catalog,
        )
        markup = render_board(payload)
        for filename in ("review.css", "review.js"):
            with self.subTest(asset=filename):
                asset = REPOSITORY_ROOT / "assets" / "review" / filename
                self.assertIn(asset.read_text(encoding="utf-8"), markup)

    def test_embedded_json_cannot_close_its_script_element(self) -> None:
        payload = build_board_payload(
            {
                "description_good_status": "Met",
                "description_good_justification": "</script><script>alert(1)</script>",
            },
            project_id="31",
            section="passing",
            catalog=self.catalog,
        )
        markup = render_board(payload)

        self.assertNotIn("</script><script>alert(1)</script>", markup)
        self.assertIn("\\u003c/script\\u003e", markup)

    def test_draft_text_round_trips_without_template_substitution(self) -> None:
        justification = (
            "{{REVIEW_SCRIPT}} {{REVIEW_CSS}} {{ASSESSMENT_JSON}} "
            '</script><script>alert("quoted text")</script> & café'
        )
        payload = build_board_payload(
            {"description_good_justification": justification},
            project_id="31",
            section="passing",
            catalog=self.catalog,
        )
        markup = render_board(payload)
        embedded = re.search(
            r'<script id="assessment-data" type="application/json">(.*?)</script>',
            markup,
            re.S,
        )
        self.assertIsNotNone(embedded)
        self.assertEqual(payload, json.loads(embedded.group(1)))

    def test_write_replaces_only_the_explicit_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "board.html"
            returned = write_board(
                {"description_good_status": "Unmet"},
                destination,
                project_id="31",
                section="passing",
                catalog=self.catalog,
            )
            self.assertEqual(destination, returned)
            self.assertEqual(
                ["board.html"], [item.name for item in destination.parent.iterdir()]
            )
            self.assertIn(
                '"description_good":{"status":"Unmet"',
                destination.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
