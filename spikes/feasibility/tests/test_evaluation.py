from pathlib import Path

from taxigraph_spike import evaluation


def test_query_not_verified_when_no_saved_query(tmp_path: Path):
    result = evaluation.evaluate_cases(tmp_path / "missing.graphql", lambda q, v: {}, [])
    assert result.status == "query_not_verified"


def test_case_to_variables_stop_based():
    case = {
        "origin_stop_id": "SYN_STOP_1",
        "destination_stop_id": "SYN_STOP_3",
        "requested_departure": "07:00:00",
    }
    variables = evaluation.case_to_variables(case)
    assert variables["origin"]["location"]["stopLocation"]["stopLocationId"] == "1:SYN_STOP_1"
    assert variables["destination"]["location"]["stopLocation"]["stopLocationId"] == "1:SYN_STOP_3"
    assert variables["earliestDeparture"] == "2026-09-16T07:00:00+02:00"


def test_case_to_variables_coordinate_based():
    case = {"origin_lat": 30.0, "origin_lon": 30.0, "destination_stop_id": "SYN_STOP_1"}
    variables = evaluation.case_to_variables(case)
    assert variables["origin"]["location"]["coordinate"] == {"latitude": 30.0, "longitude": 30.0}


def test_evaluate_cases_pass(tmp_path: Path):
    query_path = tmp_path / "plan-query.graphql"
    query_path.write_text("query Plan { planConnection { edges { node { start } } } }")

    def fake_post(query: str, variables: dict) -> dict:
        origin = variables["origin"]["location"].get("stopLocation", {}).get("stopLocationId")
        if origin == "1:SYN_STOP_1":
            return {"planConnection": {"edges": [{"node": {}}], "routingErrors": []}}
        return {"planConnection": {"edges": [], "routingErrors": [{"code": "NO_TRANSIT_CONNECTION"}]}}

    cases = [
        {"id": "positive", "origin_stop_id": "SYN_STOP_1", "destination_stop_id": "SYN_STOP_3", "expected_result": "journey_found"},
        {"id": "negative", "origin_stop_id": "SYN_STOP_3", "destination_stop_id": "SYN_STOP_1", "expected_result": "no_journey"},
    ]

    result = evaluation.evaluate_cases(query_path, fake_post, cases)
    assert result.status == "ok"
    assert result.all_passed


def test_evaluate_cases_fail(tmp_path: Path):
    query_path = tmp_path / "plan-query.graphql"
    query_path.write_text("query Plan { planConnection { edges { node { start } } } }")

    def fake_post(query: str, variables: dict) -> dict:
        return {"planConnection": {"edges": [{"node": {}}], "routingErrors": []}}

    cases = [
        {
            "id": "should-be-blocked",
            "origin_stop_id": "SYN_STOP_3",
            "destination_stop_id": "SYN_STOP_1",
            "expected_result": "no_journey",
        }
    ]

    result = evaluation.evaluate_cases(query_path, fake_post, cases)
    assert result.status == "fail"
    assert result.outcomes[0].passed is False


def test_evaluate_cases_handles_post_exception(tmp_path: Path):
    query_path = tmp_path / "plan-query.graphql"
    query_path.write_text("query Plan { planConnection { edges { node { start } } } }")

    def fake_post(query: str, variables: dict) -> dict:
        raise RuntimeError("connection reset")

    cases = [
        {
            "id": "errors-out",
            "origin_stop_id": "SYN_STOP_1",
            "destination_stop_id": "SYN_STOP_3",
            "expected_result": "journey_found",
        }
    ]
    result = evaluation.evaluate_cases(query_path, fake_post, cases)
    assert result.outcomes[0].actual_result == "error"
    assert result.outcomes[0].passed is False


def test_evaluate_cases_handles_malformed_case(tmp_path: Path):
    query_path = tmp_path / "plan-query.graphql"
    query_path.write_text("query Plan { planConnection { edges { node { start } } } }")

    cases = [{"id": "no-destination", "origin_stop_id": "SYN_STOP_1", "expected_result": "journey_found"}]
    result = evaluation.evaluate_cases(query_path, lambda q, v: {}, cases)
    assert result.outcomes[0].actual_result == "error"
