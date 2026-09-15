"""Evaluate the synthetic (or real) cases against a running OTP instance.

Deliberately refuses to guess OTP's GraphQL plan-query shape. SOL-HANDOFF is
explicit: introspect the running runtime and save one tested query rather
than assuming a schema. Until `plan-query.graphql` exists (written after a
human/agent has actually run introspection against a live OTP and confirmed
the query works), this reports `query_not_verified` instead of sending a
guessed query and calling a coincidental success meaningful.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

PlanQueryFn = Callable[[str, dict[str, Any]], dict[str, Any]]


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


def case_to_variables(case: dict[str, Any]) -> dict[str, Any]:
    """Best-effort mapping from a fixture case to plan-query variables.

    Field names here are provisional; confirm/adjust them against the saved,
    introspected schema before trusting evaluation results.
    """

    variables: dict[str, Any] = {}
    if "origin_stop_id" in case:
        variables["originStopId"] = case["origin_stop_id"]
    if "origin_lat" in case:
        variables["originLat"] = case["origin_lat"]
        variables["originLon"] = case["origin_lon"]
    if "destination_stop_id" in case:
        variables["destinationStopId"] = case["destination_stop_id"]
    if "requested_departure" in case:
        variables["time"] = case["requested_departure"]
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
        variables = case_to_variables(case)
        try:
            data = post_query(query, variables)
        except Exception as exc:  # noqa: BLE001 - surfaced as a failed case, not a crash
            outcomes.append(
                CaseOutcome(case["id"], case["expected_result"], "error", False, str(exc))
            )
            continue

        itineraries = data.get("itineraries", []) if data else []
        actual_result = "journey_found" if itineraries else "no_journey"
        expected_result = case["expected_result"]
        passed = actual_result == expected_result
        outcomes.append(CaseOutcome(case["id"], expected_result, actual_result, passed))

    status = "ok" if all(o.passed for o in outcomes) else "fail"
    detail = f"{sum(o.passed for o in outcomes)}/{len(outcomes)} cases passed"
    return EvaluationResult(status, detail, outcomes)
