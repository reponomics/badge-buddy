"""Render a draft as a passive, self-refreshing review board."""

from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Mapping
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from .criteria import CriteriaCatalog, Criterion

REFRESH_SECONDS = 5
_ASSET_DIR = Path(__file__).resolve().parents[2] / "assets" / "review"
_VALID_STATUSES = {"Met", "Unmet", "N/A", "?"}
_BUCKETS = (
    (
        "needs_input",
        "Not yet answered",
        "Read the criteria that do not have an answer yet.",
    ),
    (
        "unmet",
        "Unmet",
        "Criteria marked Unmet. Explore what would help meet them.",
    ),
    (
        "na",
        "N/A answers",
        "Criteria marked as not applicable to this project.",
    ),
    (
        "met",
        "Met answers",
        "Criteria marked Met. Review the answers and supporting information.",
    ),
)


def build_board_payload(
    document: Mapping[str, Any],
    *,
    project_id: str,
    section: str,
    catalog: CriteriaCatalog,
) -> dict[str, Any]:
    """Project one flat draft into display-only browser data."""

    responses = catalog.classify_flat(document)[section]
    criteria = catalog.section(section)
    answers = {
        criterion.id: _answer(responses.get(criterion.id, {})) for criterion in criteria
    }
    bucket_ids = {key: [] for key, _label, _description in _BUCKETS}
    for criterion in criteria:
        bucket_ids[_bucket_key(answers[criterion.id]["status"])].append(criterion.id)

    normalized_criteria = [_criterion_payload(criterion) for criterion in criteria]
    payload: dict[str, Any] = {
        "projectId": project_id,
        "section": section,
        "generatedAt": datetime.now(UTC).isoformat(),
        "refreshSeconds": REFRESH_SECONDS,
        "criteria": normalized_criteria,
        "answers": answers,
        "buckets": [
            {
                "key": key,
                "label": label,
                "description": description,
                "count": len(bucket_ids[key]),
                "criterionIds": bucket_ids[key],
            }
            for key, label, description in _BUCKETS
        ],
        "total": len(criteria),
    }
    return payload


def render_board(payload: Mapping[str, Any]) -> str:
    """Embed assets and assessment data in one local, self-contained document."""

    template = (_ASSET_DIR / "index.html").read_text(encoding="utf-8")
    stylesheet = (_ASSET_DIR / "review.css").read_text(encoding="utf-8")
    script = (_ASSET_DIR / "review.js").read_text(encoding="utf-8")
    serialized = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
    serialized = serialized.replace("<", "\\u003c").replace(">", "\\u003e")
    replacements = {
        "REVIEW_CSS": stylesheet,
        "ASSESSMENT_JSON": serialized,
        "REVIEW_SCRIPT": script,
    }
    # Substitute only the original template; inserted data is never template syntax.
    return re.sub(
        r"\{\{(REVIEW_CSS|ASSESSMENT_JSON|REVIEW_SCRIPT)\}\}",
        lambda match: replacements[match[1]],
        template,
    )


def write_board(
    document: Mapping[str, Any],
    output_path: str | Path,
    *,
    project_id: str,
    section: str,
    catalog: CriteriaCatalog,
) -> Path:
    """Atomically replace a passive review document at an explicit path."""

    destination = Path(output_path)
    payload = build_board_payload(
        document,
        project_id=project_id,
        section=section,
        catalog=catalog,
    )
    markup = render_board(payload)
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(markup)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return destination


def _answer(response: Mapping[str, Any]) -> dict[str, str]:
    raw_status = response.get("status", "?")
    status = str(raw_status).strip() if raw_status is not None else "?"
    if status not in _VALID_STATUSES:
        status = "?"
    raw_justification = response.get("justification", "")
    justification = "" if raw_justification is None else str(raw_justification)
    return {"status": status, "justification": justification}


def _bucket_key(status: str) -> str:
    return {"Met": "met", "Unmet": "unmet", "N/A": "na"}.get(status, "needs_input")


def _criterion_payload(criterion: Criterion) -> dict[str, Any]:
    return {
        "id": criterion.id,
        "displayId": criterion.display_id,
        "category": criterion.requirement,
        "description": plain_text(criterion.description),
        "details": plain_text(criterion.details or ""),
        "naAllowed": criterion.na_allowed,
        "naJustificationRequired": criterion.na_justification_required,
        "metJustificationRequired": criterion.met_justification_required,
        "metUrlRequired": criterion.met_url_required,
    }


class _TextExtractor(HTMLParser):
    _BREAK_TAGS = frozenset(
        {
            "br",
            "dd",
            "div",
            "dt",
            "li",
            "ol",
            "p",
            "tr",
            "ul",
        }
    )

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag in self._BREAK_TAGS:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._BREAK_TAGS:
            self.parts.append(" ")


def plain_text(value: str) -> str:
    """Return readable text from the small HTML fragments in upstream criteria."""

    parser = _TextExtractor()
    parser.feed(value)
    parser.close()
    return re.sub(r"\s+", " ", "".join(parser.parts)).strip()
