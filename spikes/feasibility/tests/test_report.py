from pathlib import Path

from taxigraph_spike import report


def test_decide_exit_code_pass():
    r = report.CheckReport(
        mode="smoke",
        software_status=report.STATUS_PASS,
        real_data_status=report.STATUS_NOT_APPLICABLE,
        rights_status=report.STATUS_NOT_APPLICABLE,
        journey_validation_status=report.STATUS_PASS,
    )
    assert report.decide_exit_code(r) == 0


def test_decide_exit_code_blocked_wins_over_fail():
    r = report.CheckReport(
        mode="real",
        software_status=report.STATUS_FAIL,
        real_data_status=report.STATUS_DATA_BLOCKED,
        rights_status=report.STATUS_NOT_APPLICABLE,
        journey_validation_status=report.STATUS_NOT_RUN,
    )
    assert report.decide_exit_code(r) == 2


def test_decide_exit_code_fail():
    r = report.CheckReport(
        mode="smoke",
        software_status=report.STATUS_FAIL,
        real_data_status=report.STATUS_NOT_APPLICABLE,
        rights_status=report.STATUS_NOT_APPLICABLE,
        journey_validation_status=report.STATUS_FAIL,
    )
    assert report.decide_exit_code(r) == 1


def test_write_report_round_trips(tmp_path: Path):
    r = report.CheckReport(
        mode="smoke",
        software_status=report.STATUS_PASS,
        real_data_status=report.STATUS_NOT_APPLICABLE,
        rights_status=report.STATUS_NOT_APPLICABLE,
        journey_validation_status=report.STATUS_PASS,
        details={"foo": "bar"},
    )
    out_path = tmp_path / "out" / "report.json"
    report.write_report(r, out_path)
    assert out_path.is_file()
    assert "foo" in out_path.read_text(encoding="utf-8")
