"""Loader for the explicitly artificial smoke-test network.

fixtures/synthetic/network.json is hand-written software-test data. It must
never be treated as, or merged with, real Cape Town evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL_KEYS = {
    "provenance",
    "agency",
    "service",
    "stops",
    "routes",
    "trips",
    "transfers",
    "negative_controls",
    "positive_cases",
}


class SyntheticFixtureError(ValueError):
    pass


def load_synthetic_network(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        network = json.load(handle)

    missing_keys = REQUIRED_TOP_LEVEL_KEYS - network.keys()
    if missing_keys:
        raise SyntheticFixtureError(f"synthetic fixture missing keys: {sorted(missing_keys)}")

    provenance = network["provenance"]
    if provenance.get("kind") != "synthetic":
        raise SyntheticFixtureError(
            "fixture at "
            f"{path} does not declare provenance.kind == 'synthetic'; "
            "refusing to load as a smoke fixture"
        )

    if len(network["trips"]) < 2:
        raise SyntheticFixtureError("smoke fixture needs at least two directed transit patterns")

    if not network["transfers"]:
        raise SyntheticFixtureError("smoke fixture needs at least one pedestrian transfer")

    if not network["negative_controls"]:
        raise SyntheticFixtureError("smoke fixture needs at least one negative control")

    return network


def default_fixture_path() -> Path:
    return Path(__file__).resolve().parents[2] / "fixtures" / "synthetic" / "network.json"
