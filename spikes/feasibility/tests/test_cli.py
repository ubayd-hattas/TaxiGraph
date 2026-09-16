import json
from pathlib import Path

from taxigraph_spike import cli, prerequisites


def test_smoke_reports_blocked_when_java_missing(monkeypatch):
    monkeypatch.setattr(
        prerequisites,
        "check_java_version",
        lambda *args, **kwargs: prerequisites.CheckResult("java_version", False, "java not found on PATH"),
    )

    exit_code = cli.main(["check", "--mode", "smoke"])

    assert exit_code == 2
    report_path = cli.OUT_DIR / "report.json"
    assert report_path.is_file()
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["software_status"] == "blocked"
    assert data["journey_validation_status"] == "not_run"
    # GTFS export still ran even though OTP/validator steps were skipped.
    assert Path(data["details"]["gtfs_export"]["zip_path"]).is_file()


def test_real_mode_blocked_without_manifest(tmp_path: Path):
    missing_manifest = tmp_path / "does-not-exist.json"

    exit_code = cli.main(["check", "--mode", "real", "--manifest", str(missing_manifest)])

    assert exit_code == 2
    report_path = cli.OUT_DIR / "real-report.json"
    assert report_path.is_file()
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["real_data_status"] == "data_blocked"
    assert data["rights_status"] == "data_blocked"


def test_real_mode_blocked_with_incomplete_manifest(tmp_path: Path):
    manifest_path = tmp_path / "real-manifest.json"
    manifest_path.write_text(json.dumps({"dataset_version": "2026-09-01"}))

    exit_code = cli.main(["check", "--mode", "real", "--manifest", str(manifest_path)])

    assert exit_code == 2
    data = json.loads((cli.OUT_DIR / "real-report.json").read_text(encoding="utf-8"))
    assert data["real_data_status"] == "data_blocked"
    assert data["details"]["manifest_validation"]["status"] == "data_blocked"
    assert "source_rights_reference" in data["details"]["manifest_validation"]["missing"]
