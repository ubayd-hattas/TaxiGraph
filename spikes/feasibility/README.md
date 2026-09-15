# TaxiGraph feasibility spike

Bounded ROADMAP task 1 (see [docs/SOL-HANDOFF.md](../../docs/SOL-HANDOFF.md)). This package is deliberately small and disposable: it exists to answer one question, not to become the production data pipeline.

## What this proves, and what it doesn't

- **Software smoke:** an explicitly artificial GTFS network exercises the validator, OTP graph build, and GraphQL query path. It never claims anything about real Cape Town service.
- **Real-service feasibility:** gated behind a manifest contract (rights, directed variants, boarding/timing evidence, a 12-case corpus). An incomplete manifest fails closed as `data_blocked`, not as an empty "success".

See [docs/FEASIBILITY-RESULTS.md](../../docs/FEASIBILITY-RESULTS.md) for the current run's actual status.

## Setup

```powershell
cd spikes/feasibility
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Java 25 and the pinned OTP/GTFS-validator jars are **not installed by this package**. Download them yourself, place them at the paths in [tools-manifest.json](tools-manifest.json), and fill in each `sha256` once you've verified the download. `check` refuses to run against an unpinned or unverified jar.

## Commands

Run from `spikes/feasibility`, inside the venv:

```powershell
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m taxigraph_spike check --mode smoke
.venv\Scripts\python.exe -m taxigraph_spike check --mode real --manifest local/real-manifest.json
```

`check` writes a structured report to `out/report.json` (smoke) or `out/real-report.json` (real) with four independent statuses: `software_status`, `real_data_status`, `rights_status`, `journey_validation_status`. Exit code is 0 for an actual pass, 1 for a validation failure, 2 for missing prerequisites/evidence/rights.

## Layout

```text
src/taxigraph_spike/   package code
tests/                 pytest suite (mocks external binaries; no Java required to run)
fixtures/synthetic/    hand-written, explicitly artificial smoke network
local/                 ignored: real inputs, downloaded jars, private evidence
out/                   ignored: generated GTFS, graph, logs, reports
tools-manifest.json    pins for Java/OTP/validator/OSM extract (checksums start null)
```

## Current blocker

No Java runtime is installed in this environment, so `check --mode smoke` currently reports `software_status: blocked` (exit 2) after exporting the synthetic GTFS feed but before reaching the validator/OTP steps. Real mode is separately blocked: no source-use rights or field evidence have been supplied yet, so no `local/real-manifest.json` exists. Both are expected, reported states, not failures of the harness itself.
