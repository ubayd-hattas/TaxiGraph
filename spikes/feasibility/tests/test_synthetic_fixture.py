import json
from pathlib import Path

import pytest

from taxigraph_spike import synthetic_fixture


def test_default_fixture_loads():
    network = synthetic_fixture.load_synthetic_network(synthetic_fixture.default_fixture_path())
    assert network["provenance"]["kind"] == "synthetic"
    assert len(network["trips"]) >= 2
    assert network["transfers"]
    assert network["negative_controls"]


def test_rejects_non_synthetic_provenance(tmp_path: Path):
    bad = {
        "provenance": {"kind": "real"},
        "agency": {},
        "service": {},
        "stops": [],
        "routes": [],
        "trips": [{}, {}],
        "transfers": [{}],
        "negative_controls": [{}],
        "positive_cases": [],
    }
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(synthetic_fixture.SyntheticFixtureError, match="synthetic"):
        synthetic_fixture.load_synthetic_network(path)


def test_rejects_missing_transfer(tmp_path: Path):
    bad = {
        "provenance": {"kind": "synthetic"},
        "agency": {},
        "service": {},
        "stops": [],
        "routes": [],
        "trips": [{}, {}],
        "transfers": [],
        "negative_controls": [{}],
        "positive_cases": [],
    }
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(synthetic_fixture.SyntheticFixtureError, match="pedestrian transfer"):
        synthetic_fixture.load_synthetic_network(path)


def test_rejects_missing_negative_control(tmp_path: Path):
    bad = {
        "provenance": {"kind": "synthetic"},
        "agency": {},
        "service": {},
        "stops": [],
        "routes": [],
        "trips": [{}, {}],
        "transfers": [{}],
        "negative_controls": [],
        "positive_cases": [],
    }
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(synthetic_fixture.SyntheticFixtureError, match="negative control"):
        synthetic_fixture.load_synthetic_network(path)
