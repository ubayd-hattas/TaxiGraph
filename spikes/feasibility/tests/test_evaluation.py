from pathlib import Path

from taxigraph_spike import evaluation


def test_query_not_verified_when_no_saved_query(tmp_path: Path):
    result = evaluation.evaluate_cases(tmp_path / "missing.graphql", lambda q, v: {}, [])
    assert result.status == "query_not_verified"


def test_evaluate_cases_pass(tmp_path: Path):
    query_path = tmp_path / "plan-query.graphql"
    query_path.write_text("query Plan { itineraries { legs { mode } } }")

    def fake_post(query: str, variables: dict) -> dict:
        if variables.get("originStopId") == "SYN_STOP_1":
            return {"itineraries": [{"legs": []}]}
        return {"itineraries": []}

    cases = [
        {"id": "positive", "origin_stop_id": "SYN_STOP_1", "expected_result": "journey_found"},
        {"id": "negative", "origin_stop_id": "SYN_STOP_3", "expected_result": "no_journey"},
    ]

    result = evaluation.evaluate_cases(query_path, fake_post, cases)
    assert result.status == "ok"
    assert result.all_passed


def test_evaluate_cases_fail(tmp_path: Path):
    query_path = tmp_path / "plan-query.graphql"
    query_path.write_text("query Plan { itineraries { legs { mode } } }")

    def fake_post(query: str, variables: dict) -> dict:
        return {"itineraries": [{"legs": []}]}

    cases = [{"id": "should-be-blocked", "origin_stop_id": "SYN_STOP_3", "expected_result": "no_journey"}]

    result = evaluation.evaluate_cases(query_path, fake_post, cases)
    assert result.status == "fail"
    assert result.outcomes[0].passed is False


def test_evaluate_cases_handles_post_exception(tmp_path: Path):
    query_path = tmp_path / "plan-query.graphql"
    query_path.write_text("query Plan { itineraries { legs { mode } } }")

    def fake_post(query: str, variables: dict) -> dict:
        raise RuntimeError("connection reset")

    cases = [{"id": "errors-out", "origin_stop_id": "SYN_STOP_1", "expected_result": "journey_found"}]
    result = evaluation.evaluate_cases(query_path, fake_post, cases)
    assert result.outcomes[0].actual_result == "error"
    assert result.outcomes[0].passed is False
