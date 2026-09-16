"""Evaluate the synthetic (or real) cases against a running OTP instance.

Deliberately refuses to guess OTP's GraphQL plan-query shape. SOL-HANDOFF is
explicit: introspect the running runtime and save one tested query rather
than assuming a schema. Until `plan-query.graphql` exists (written after a
human/agent has actually run introspection against a live OTP and confirmed
the query works), this reports `query_not_verified` instead of sending a
guessed query and calling a coincidental success meaningful.

`case_to_variables` and the itinerary-extraction in `evaluate_cases` match
the exact shape of queries/plan-query.graphql, confirmed against a live
OTP 2.9.0 instance on 2026-09-16 (see docs/FEASIBILITY-RESULTS.md). OTP
assigns feed-scoped stop IDs by the positional index of the GTFS input on
the build command line ("1:" for a single feed), not from feed_info.txt's
feed_id column -- that prefix would need re-verifying if a second feed is
ever combined into the same graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

PlanQueryFn = Callable[[str, dict[str, Any]], dict[str, Any]]

FEED_ID_PREFIX = "1:"  # OTP's default for a single positionally-first GTFS input.
REFERENCE_DATE = "2026-09-16"  # A Wednesday within the synthetic fixture's Mon-Fri service.
TIMEZONE_OFFSET = "+02:00"  # Africa/Johannesburg has no DST.


@dataclass(frozen=True)
class CaseOutcome:
    case_id: str
    expected_result: str
    actual_result: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class EvaluationResult:
    status: str  # "ok" | "fail" | "query_not_verified" | "otp_unavailable"
    detail: str
    outcomes: list[CaseOutcome] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return bool(self.outcomes) and all(o.passed for o in self.outcomes)


def _plan_location(case: dict[str, Any], prefix: str) -> dict[str, Any]:
    stop_key = f"{prefix}_stop_id"
    lat_key = f"{prefix}_lat"
    lon_key = f"{prefix}_lon"

    if stop_key in case:
        return {"location": {"stopLocation": {"stopLocationId": f"{FEED_ID_PREFIX}{case[stop_key]}"}}}
    if lat_key in case:
        return {"location": {"coordinate": {"latitude": case[lat_key], "longitude": case[lon_key]}}}
    raise ValueError(f"case has neither {stop_key} nor {lat_key}/{lon_key}: {case}")


def case_to_variables(case: dict[str, Any]) -> dict[str, Any]:
    """Map a fixture case to queries/plan-query.graphql's exact variables.

    Matches PlanLabeledLocationInput / PlanDateTimeInput as confirmed by
    introspection and a live test run (see module docstring).
    """

    variables: dict[str, Any] = {
        "origin": _plan_location(case, "origin"),
        "destination": _plan_location(case, "destination"),
    }
    if "requested_departure" in case:
        variables["earliestDeparture"] = f"{REFERENCE_DATE}T{case['requested_departure']}{TIMEZONE_OFFSET}"
    return variables


def evaluate_cases(
    plan_query_path: Path,
    post_query: PlanQueryFn,
    cases: list[dict[str, Any]],
) -> EvaluationResult:
    if not plan_query_path.is_file():
        return EvaluationResult(
            "query_not_verified",
            f"no verified plan query at {plan_query_path}; run OTP, introspect, "
            "and save a manually confirmed query before evaluating cases",
        )

    query = plan_query_path.read_text(encoding="utf-8")
    outcomes: list[CaseOutcome] = []

    for case in cases:
        try:
            variables = case_to_variables(case)
            data = post_query(query, variables)
        except Exception as exc:  # noqa: BLE001 - surfaced as a failed case, not a crash
            outcomes.append(
                CaseOutcome(case["id"], case["expected_result"], "error", False, str(exc))
            )
            continue

        plan_connection = (data or {}).get("planConnection") or {}
        edges = plan_connection.get("edges") or []
        routing_errors = plan_connection.get("routingErrors") or []
        actual_result = "journey_found" if edges else "no_journey"
        expected_result = case["expected_result"]
        passed = actual_result == expected_result
        error_codes = [e.get("code") for e in routing_errors]
        detail = f"routingErrors={error_codes}" if routing_errors else f"{len(edges)} itinerary option(s)"
        outcomes.append(CaseOutcome(case["id"], expected_result, actual_result, passed, detail))

    status = "ok" if all(o.passed for o in outcomes) else "fail"
    detail = f"{sum(o.passed for o in outcomes)}/{len(outcomes)} cases passed"
    return EvaluationResult(status, detail, outcomes)
