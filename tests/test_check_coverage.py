"""A high combined percentage must not hide weak statement or branch coverage."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from check_coverage import main


class CoverageFloorTest(unittest.TestCase):
    def run_report(self, statements, branches, *, measured=True):
        report = {
            "meta": {"branch_coverage": measured},
            "totals": {
                "covered_lines": statements[0],
                "num_statements": statements[1],
                "covered_branches": branches[0],
                "num_branches": branches[1],
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "coverage.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                code = main([str(path)])
        return code, output.getvalue()

    def test_high_combined_coverage_does_not_hide_either_failing_metric(self):
        # Both examples exceed an 80% combined floor.
        for statements, branches, failed in (
            ((100, 100), (7, 10), "Branch"),
            ((7, 10), (100, 100), "Statement"),
        ):
            with self.subTest(failed=failed):
                code, output = self.run_report(statements, branches)
                self.assertEqual(1, code)
                self.assertIn(f"{failed} coverage: 70.00% (minimum 80%) — FAIL", output)

    def test_boundary_is_checked_without_rounding(self):
        self.assertEqual(0, self.run_report((80, 100), (80, 100))[0])
        self.assertEqual(1, self.run_report((79999, 100000), (100, 100))[0])

    def test_absent_measurements_fail_but_branchless_source_is_valid(self):
        self.assertEqual(1, self.run_report((100, 100), (0, 0), measured=False)[0])
        self.assertEqual(1, self.run_report((0, 0), (0, 0))[0])
        self.assertEqual(0, self.run_report((100, 100), (0, 0))[0])

    def test_invalid_report_fails_closed(self):
        self.assertEqual(1, self.run_report((101, 100), (80, 100))[0])
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(1, main(["/nonexistent/badge-buddy-coverage.json"]))


if __name__ == "__main__":
    unittest.main()
