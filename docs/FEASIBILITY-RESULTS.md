# Feasibility spike results

Status as of 2026-09-15. Produced by `spikes/feasibility` (ROADMAP task 1 / [SOL-HANDOFF](SOL-HANDOFF.md)). This is a harness status report, not a claim that any real Cape Town journey has been validated. No OTP graph has been built.

## Separate statuses

| Status | Value | Meaning |
|---|---|---|
| `software_status` | **blocked** | Synthetic GTFS export succeeded; validator/OTP build did not run because Java and the pinned jars are not present on this machine. |
| `real_data_status` | **data_blocked** | No `local/real-manifest.json` exists yet; nothing to evaluate. |
| `rights_status` | **data_blocked** | Reproduction/transmission permission for the City ArcGIS source has not been confirmed (see [DATA-SOURCES](DATA-SOURCES.md)). No alternative clearly licensed source has been selected either. |
| `journey_validation_status` | **not_run** | No OTP instance has run, so none of the 12 required corpus cases have been evaluated. |

Raw reports: `spikes/feasibility/out/report.json` (smoke), `spikes/feasibility/out/real-report.json` (real). Both are gitignored (local artifacts); regenerate with the commands below.

## What was built

A Python 3.13 package at `spikes/feasibility/` implementing, per SOL-HANDOFF's ordered list:

1. Prerequisite/manifest validation (`prerequisites.py`): Java version check, pinned-artifact presence + checksum check against `tools-manifest.json`.
2. A synthetic smoke fixture (`fixtures/synthetic/network.json`): two directed transit patterns (north-south, east-west), one pedestrian transfer at a shared corner, and four negative controls (unsupported reverse direction, false transfer across a barrier, outside verified service window, outside coverage). Explicitly marked `"kind": "synthetic"`; the loader refuses to treat anything else as a smoke fixture.
3. The minimal real-input contract (`real_manifest.py`): required rights reference, 3-5 directed variants, boarding/service-window/headway evidence, dataset version, and a 12-case evaluation corpus covering all four negative categories. An incomplete manifest returns `data_blocked` listing exactly which fields are missing; a bare public-URL rights reference is explicitly rejected.
4. A narrow GTFS projection (`gtfs_export.py`): stdlib csv/zip only, `exact_times=0`, finite calendar dates, an ID map, and no fare tables (fares are unknown for the synthetic fixture and must never be exported as zero).
5. Validator/OTP orchestration (`validator_runner.py`, `otp_runner.py`): wraps the pinned CLIs, reports `missing_prerequisite` instead of crashing when a jar isn't present, uses hidden background processes on Windows, and copies only the intended GTFS/PBF into the OTP build directory.
6. A GraphQL evaluation harness (`graphql_client.py`, `evaluation.py`): posts to OTP's `/otp/gtfs/v1`. Deliberately refuses to guess the plan-query schema — it requires a saved, manually verified query file before evaluating any case, per SOL-HANDOFF's instruction to introspect rather than assume.
7. Real-mode gating (`cli.py: run_real`): validates the manifest contract before anything else; only attempts real export/evaluation once the contract is satisfied, and that pipeline is intentionally not yet implemented (it's ROADMAP task 3+ work).

`python -m taxigraph_spike check --mode smoke|real` exists, exits 0/1/2 per the SOL-HANDOFF contract, and writes a structured report. 36 unit tests pass (`python -m pytest`), covering prerequisite failures, the fixture's own guardrails, GTFS output correctness (table contents, non-exact frequencies, finite calendar, ID map, no fare tables), manifest contract validation, evaluation-harness pass/fail/error paths, and the CLI's exit codes for both blocked-smoke and blocked-real paths.

## Exact versions / checksums

| Item | Pin | Status |
|---|---|---|
| Python | 3.13 | 3.13.5 installed and used |
| Java | 25 | **not installed** on this machine |
| OTP | 2.9.0, commit `9babe45ffc9327933129f705c648137ecd96cdbe` | jar not downloaded; `sha256` unset in `tools-manifest.json` |
| GTFS validator | unselected release | jar not downloaded; `sha256` unset |
| OSM extract | unselected | not obtained |

`tools-manifest.json` pins Java's minimum major version and each jar's intended local path; `sha256` fields stay `null` until the exact artifact is downloaded and verified, which fails the prerequisite check on purpose.

## Commands run

```powershell
cd spikes/feasibility
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest                                  # 36 passed
.venv\Scripts\python.exe -m taxigraph_spike check --mode smoke      # exit 2, software_status=blocked
.venv\Scripts\python.exe -m taxigraph_spike check --mode real       # exit 2, real_data_status=rights_status=data_blocked
```

## Exclusions, corpus outcomes, resource measurements, timing sensitivity

Not applicable yet: the validator and OTP have not run, so there is nothing to report for exclusion counts, MobilityData notices, corpus pass/fail outcomes, memory/latency measurements, or headway timing-sensitivity behavior. These require Java 25 plus the pinned OTP/validator jars at minimum, and the 12-case real corpus additionally requires resolved source-use rights and field-verified evidence, neither of which exist yet.

## Rights blocker detail

The City ArcGIS source's `/iteminfo?f=json` states reproduction/transmission needs City permission (see [DATA-SOURCES](DATA-SOURCES.md)). No permission reference has been supplied, and no clearly licensed replacement source has been selected. `real_manifest.py` enforces this at the code level: a manifest whose `source_rights_reference` is empty, or is just a public URL, is rejected as `data_blocked` rather than silently accepted.

## Recommended next bounded task

**ROADMAP task 1, finish the software half first:** install Java 25, download and checksum-pin the OTP 2.9.0 jar, the MobilityData GTFS validator CLI, and a small licensed OSM extract into `spikes/feasibility/local/tools/`, then rerun `check --mode smoke` until `software_status` reaches `pass`. This is a local setup step, not a code change, so it's a reasonable one to hand back to whoever runs this environment rather than something to script blindly (downloading a JDK and unverified jars unattended isn't appropriate to do without confirmation).

Only after that should work move to **ROADMAP task 2** (acquire evidence and close the real feasibility gate): resolve source-use rights and gather the field-verified 12-case corpus with the maintainer/local verifier. Do not start ROADMAP task 3 (production data package) before both gates pass.
