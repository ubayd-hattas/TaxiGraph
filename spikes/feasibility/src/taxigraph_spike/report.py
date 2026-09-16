"""Structured `check` report: the four statuses the CLI contract requires.

Exit codes (per docs/SOL-HANDOFF.md): 0 = the selected mode's actual pass,
1 = a validation failure, 2 = missing prerequisites/evidence/rights.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS_PASS = "pass"
STATUS_FAIL = "fail"
STATUS_BLOCKED = "blocked"
STATUS_DATA_BLOCKED = "data_blocked"
STATUS_NOT_APPLICABLE = "not_applicable"
STATUS_NOT_RUN = "not_run"


@dataclass
class CheckReport:
    mode: str
    software_status: str
    real_data_status: str
    rights_status: str
    journey_validation_status: str
    details: dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def write_report(report: CheckReport, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(report.to_dict(), handle, indent=2, sort_keys=True, default=str)


def decide_exit_code(report: CheckReport) -> int:
    blocked_statuses = {STATUS_BLOCKED, STATUS_DATA_BLOCKED}
    fail_statuses = {STATUS_FAIL}

    statuses = (
        report.software_status,
        report.real_data_status,
        report.rights_status,
        report.journey_validation_status,
    )

    if any(status in blocked_statuses for status in statuses):
        return 2
    if any(status in fail_statuses for status in statuses):
        return 1
    return 0
