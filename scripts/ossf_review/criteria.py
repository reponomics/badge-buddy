"""Criteria of the badge levels being displayed, from MCP ``get_criteria`` records."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from .fields import normalize_assessment_fields

SECTION_NAMES = (
    "passing",
    "silver",
    "gold",
    "baseline-1",
    "baseline-2",
    "baseline-3",
)

# The Metal edit form presents its sections in this order. Baseline records
# already arrive in form order.
_METAL_FORM_SECTIONS = (
    "Basics",
    "Change Control",
    "Reporting",
    "Quality",
    "Security",
    "Analysis",
)
_METAL_LEVELS = ("passing", "silver", "gold")


@dataclass(frozen=True, slots=True)
class Criterion:
    """One criterion of a badge level."""

    id: str
    display_id: str
    requirement: str
    form_section: str
    description: str
    details: str | None
    na_allowed: bool
    na_justification_required: bool
    met_justification_required: bool
    met_url_required: bool

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> Criterion:
        criterion_id = _required_text(record, "criterion_id")
        # The board uses the ID as a URL fragment and element key.
        if not re.fullmatch(r"[A-Za-z0-9_-]+", criterion_id):
            raise ValueError(
                f"criterion ID {criterion_id!r} has unsupported characters"
            )
        requirement = _required_text(record, "requirement")
        if requirement not in {"MUST", "SHOULD", "SUGGESTED"}:
            raise ValueError(
                f"criterion {criterion_id!r} has invalid requirement {requirement!r}"
            )

        details = record.get("details")
        if details is not None and not isinstance(details, str):
            raise ValueError(f"criterion {criterion_id!r} has non-text details")

        aliases = record.get("aliases", [])
        if not isinstance(aliases, list) or not all(
            isinstance(alias, str) and alias for alias in aliases
        ):
            raise ValueError(f"criterion {criterion_id!r} has invalid aliases")

        return cls(
            id=criterion_id,
            display_id=aliases[0] if aliases else criterion_id,
            requirement=requirement,
            form_section=_required_text(record, "category"),
            description=_required_text(record, "description"),
            details=details,
            na_allowed=_boolean(record, "na_allowed"),
            na_justification_required=_boolean(record, "na_justification_required"),
            met_justification_required=_boolean(record, "met_justification_required"),
            met_url_required=_boolean(record, "met_url_required"),
        )


class CriteriaCatalog:
    """Ordered criteria of the loaded levels, with helpers for flat draft data."""

    def __init__(self, levels: Mapping[str, Iterable[Mapping[str, Any]]]) -> None:
        self._sections: dict[str, tuple[Criterion, ...]] = {}
        self._field_index: dict[str, list[tuple[str, str, str]]] = {}

        for level, records in levels.items():
            if level not in SECTION_NAMES:
                raise ValueError(f"unknown criteria section {level!r}")
            criteria = [Criterion.from_record(record) for record in records]
            if level in _METAL_LEVELS:
                criteria.sort(key=_form_section_rank)
            self._sections[level] = tuple(criteria)
            for criterion in criteria:
                self._register(level, criterion)

    @property
    def section_names(self) -> tuple[str, ...]:
        return tuple(self._sections)

    def _register(self, section: str, criterion: Criterion) -> None:
        for alias in {criterion.id, criterion.display_id}:
            self._field_index.setdefault(f"{alias}_status", []).append(
                (section, criterion.id, "status")
            )
            self._field_index.setdefault(f"{alias}_justification", []).append(
                (section, criterion.id, "justification")
            )

    def section(self, name: str) -> tuple[Criterion, ...]:
        """Return a loaded level's criteria in display order."""

        try:
            return self._sections[name]
        except KeyError as exc:
            raise KeyError(f"criteria for section {name!r} are not loaded") from exc

    def classify_flat(
        self, document: Mapping[str, Any]
    ) -> dict[str, dict[str, dict[str, Any]]]:
        """Bucket recognized flat response fields by loaded section.

        Unrelated project metadata is ignored. Only criteria represented in the
        input are added to a section bucket; callers that need a complete review
        can iterate :meth:`section` and treat missing answers as unresolved.
        Baseline fields are accepted in either internal underscore form or their
        public ``OSPS-XX-00.00`` display form.
        """

        if not isinstance(document, Mapping):
            raise TypeError("flat criteria data must be a mapping")

        buckets: dict[str, dict[str, dict[str, Any]]] = {
            name: {} for name in self._sections
        }
        for field_name, value in normalize_assessment_fields(document).items():
            for section, criterion_id, response_field in self._field_index.get(
                field_name, ()
            ):
                answer = buckets[section].setdefault(criterion_id, {})
                answer[response_field] = value
        return buckets


def _form_section_rank(criterion: Criterion) -> int:
    try:
        return _METAL_FORM_SECTIONS.index(criterion.form_section)
    except ValueError:
        return len(_METAL_FORM_SECTIONS)


def _required_text(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"criterion record has invalid {field!r}")
    return value


def _boolean(record: Mapping[str, Any], field: str) -> bool:
    value = record.get(field, False)
    if not isinstance(value, bool):
        raise ValueError(f"criterion record has non-boolean {field!r}")
    return value
