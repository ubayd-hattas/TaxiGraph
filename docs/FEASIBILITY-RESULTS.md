# Feasibility spike results

Status as of 2026-09-16. Produced by `spikes/feasibility` (ROADMAP task 1 / [SOL-HANDOFF](SOL-HANDOFF.md)). This is a harness status report. **The software smoke gate now passes; no real Cape Town journey has been validated, and none of the real-mode gates (rights, evidence, corpus) have been touched.**

## Separate statuses

| Status | Value | Meaning |
|---|---|---|
| `software_status` | **pass** | Synthetic GTFS exports, validates (0 errors), builds an OTP 2.9.0 graph, serves it, and all 6 fixture cases (2 positive, 4 negative) return the expected result over a manually verified GraphQL query. |
| `real_data_status` | **data_blocked** | No `local/real-manifest.json` exists; nothing to evaluate. |
| `rights_status` | **data_blocked** | Reproduction/transmission permission for the City ArcGIS source has not been confirmed (see [DATA-SOURCES](DATA-SOURCES.md)). No alternative clearly licensed source has been selected either. |
| `journey_validation_status` | **pass (synthetic only)** | All 6 synthetic cases pass. None of the 12 required real-corpus cases have been evaluated — that's gated on `real_data_status`/`rights_status` above. |

Raw report: `spikes/feasibility/out/report.json`. Gitignored (local artifact); regenerate with the commands below.

## What changed since the last entry (2026-09-15)

The previous entry recorded `software_status: blocked` because no JDK or pinned jars were present. Since then:

- Downloaded and checksum-pinned Java 25 (Eclipse Temurin 25.0.4.1+1), OTP 2.9.0, and MobilityData gtfs-validator 8.0.1 into `spikes/feasibility/local/tools/` (gitignored; pins recorded in `tools-manifest.json`).
- Fixed real bugs the first live run surfaced (not hypothetical — each was caught by actually running the tools, not by reasoning about them):
  - The fixture's coordinates (near `(0,0)`) failed the validator's `point_near_origin` check; moved the whole synthetic network to a clearly fictional location far from the origin.
  - `agency_url`/`feed_publisher_url` used `.invalid`, which the validator's URL check rejects as malformed; switched to `example.com` (RFC 2606 reserved-for-documentation domain).
  - OTP's build-input type sniffing keys off the substring `"gtfs"` appearing in the filename; a bare `feed.zip` was silently skipped as an unrecognized file. `otp_runner.py` now always stages the copy as `gtfs.zip`.
  - Subprocess output decoding used the Windows console's default codepage (cp1252), which crashed on a UTF-8 byte in OTP's log output; both `run_hidden`/`popen_hidden` now decode as UTF-8 with `errors="replace"`.
  - `wait_for_ready` treated any HTTP error status (e.g. a 405 on `GET /`) as "server not up yet" and polled until timeout even though the server was already listening; fixed to treat `HTTPError` as proof of readiness.
  - `report.write_report` crashed serializing `Path` values inside `details`; added `default=str`.
- Introspected the live OTP GraphQL schema (`planConnection`, `PlanLabeledLocationInput`, `PlanDateTimeInput`, `Itinerary`, `Leg`, `RoutingError`) and hand-built `queries/plan-query.graphql` from those confirmed fields, not guessed. Manually tested it against the running instance for all 6 fixture cases before wiring it into the harness.

## Real, observed OTP behavior worth recording

- **Non-exact frequencies**: for the direct case (`SYN_STOP_1` → `SYN_STOP_3`, headway 1200s from 06:00), requesting an earliest departure of 07:00 returned itineraries starting at 07:31 and 07:47 — not aligned to the 06:00-based 20-minute grid. This is consistent with GTFS's definition of non-exact frequencies (no promised departure time) but is a concrete, observed behavior rather than an assumption; worth re-checking against real evidence-backed headways in task 2.
- **Straight-line fallback transfers**: without any OSM/street data, OTP's `DirectTransferGenerator` still created 6 straight-line ("as the crow flies") walk transfers between stops that are part of a transit pattern — ignoring the fact that no real path was verified. This is exactly the failure mode MVP-SPEC warns about ("no prohibited taxi journey... broad unsafe stop snapping"). It did **not** extend to the two deliberately unserved barrier stops (`SYN_STOP_7`/`SYN_STOP_8`, no `stop_times` at all), so `false_transfer_across_barrier` currently passes — but only because *no* walk-only path can be computed anywhere in a graph with zero street data, not because OTP proved a barrier. This case must be re-run once a real OSM extract is in place before it means anything.
- **OTP's feed-scoped stop ID prefix** (`1:SYN_STOP_1`) comes from the positional index of the GTFS input on the build command line, not from `feed_info.txt`'s `feed_id` column (confirmed: setting `feed_id: SYN` did not change the prefix). Would need re-verifying if a second GTFS feed is ever combined into one graph.

## What was built

A Python 3.13 package at `spikes/feasibility/` implementing, per SOL-HANDOFF's ordered list:

1. Prerequisite/manifest validation (`prerequisites.py`): Java version check (against a pinned local JDK, resolved via `tools-manifest.json`, falling back to `PATH`), pinned-artifact presence + checksum check.
2. A synthetic smoke fixture (`fixtures/synthetic/network.json`): two directed transit patterns (north-south, east-west), one pedestrian transfer at a shared corner, and four negative controls. Explicitly marked `"kind": "synthetic"`; the loader refuses to treat anything else as a smoke fixture.
3. The minimal real-input contract (`real_manifest.py`): fail-closed `data_blocked` gate; unchanged this round.
4. A narrow GTFS projection (`gtfs_export.py`): stdlib csv/zip only, `exact_times=0`, finite calendar dates, an ID map, explicit `feed_id`, no fare tables.
5. Validator/OTP orchestration (`validator_runner.py`, `otp_runner.py`): now actually exercised end-to-end against real pinned binaries, not just against missing-file paths.
6. A GraphQL evaluation harness (`graphql_client.py`, `evaluation.py`): `queries/plan-query.graphql` is now a real, manually verified query (see above), and `case_to_variables`/`evaluate_cases` match its exact shape (`planConnection.edges`/`routingErrors`).
7. Real-mode gating (`cli.py: run_real`): unchanged; still correctly blocked on rights/evidence.

`python -m taxigraph_spike check --mode smoke|real` exits 0/1/2 per the SOL-HANDOFF contract. 40 unit tests pass (`python -m pytest`).

## Exact versions / checksums

| Item | Pin | Status |
|---|---|---|
| Python | 3.13 | 3.13.5, installed and used |
| Java | 25 | Eclipse Temurin 25.0.4.1+1, `sha256=00c847d8...9283` — matches Adoptium API's published checksum exactly. Portable zip extract at `local/tools/jdk-25.0.4.1+1/`, not a system-wide install. |
| OTP | 2.9.0, commit `9babe45ffc9327933129f705c648137ecd96cdbe` | Commit confirmed via GitHub API (tag → annotated tag object → commit). `sha256=11282412...325f6`, self-computed (OTP publishes a GPG `.asc` signature, not a plain checksum file, so this pin guards local corruption only, not a compromised upstream release). |
| GTFS validator | 8.0.1 | `gtfs-validator-8.0.1-cli.jar`, `sha256=19293ddd...000e2`, self-computed (same caveat as above; MobilityData does not publish an independent checksum for this asset). |
| OSM extract | unselected | **still not obtained.** The smoke graph currently builds without OSM (GTFS-only); see the straight-line-transfer finding above for what that costs. |

Full pin details, including source URLs, are in `spikes/feasibility/tools-manifest.json`.

## Commands run

```powershell
cd spikes/feasibility
.venv\Scripts\python.exe -m pytest                              # 40 passed
.venv\Scripts\python.exe -m taxigraph_spike check --mode smoke   # exit 0, software_status=pass
.venv\Scripts\python.exe -m taxigraph_spike check --mode real    # exit 2, real_data_status=rights_status=data_blocked (unchanged)
```

## Resource measurements (this run, this host)

Host: 12 logical processors, ~7.8 GB total physical memory (a personal laptop, not representative of a production target — see MVP-SPEC's later requirement to measure on identified hardware once a real graph exists).

| Measurement | Value |
|---|---|
| Full `check --mode smoke` wall time (export → validate → build → serve → evaluate → teardown) | ~9.6s |
| GTFS feed size | 1.8 KB (`feed.zip`) |
| OTP graph size | 9.7 KB (`graph.obj`) |
| OTP JVM heap cap used | `-Xmx2G` (unmeasured starting cap per SOL-HANDOFF; graph is trivially small, so this number says nothing about a real Cape Town graph's requirement) |

These numbers are meaningless for capacity planning — they describe an 8-stop synthetic graph, not anything resembling a real feed. Recorded only so a future real-graph measurement has something to visibly dwarf.

## Validator disposition

0 errors. 2 warnings, each with an explicit disposition:

- `missing_feed_contact_email_and_url`: optional GTFS field; not applicable to a synthetic fixture with no real operator contact. Accepted as-is.
- `stop_without_stop_time` (×2, for `SYN_STOP_7`/`SYN_STOP_8`): deliberate — these two stops exist only to carry coordinates for the `false_transfer_across_barrier` negative control and are intentionally not served by any trip. Accepted as-is; would need reconsidering if these stops were ever also expected to be reachable by transit.

## Rights blocker detail (unchanged)

The City ArcGIS source's `/iteminfo?f=json` states reproduction/transmission needs City permission (see [DATA-SOURCES](DATA-SOURCES.md)). No permission reference has been supplied, and no clearly licensed replacement source has been selected. `real_manifest.py` enforces this at the code level: a manifest whose `source_rights_reference` is empty, or is just a public URL, is rejected as `data_blocked` rather than silently accepted.

## Recommended next bounded task

The software half of ROADMAP task 1 is done: `check --mode smoke` passes end-to-end against real, checksum-pinned binaries. Two things remain before task 1 can be called fully closed, and both are optional refinements rather than blockers to starting task 2:

1. Obtain a small, appropriately licensed OSM extract (an existing OTP test fixture, per SOL-HANDOFF's preference) and re-run smoke with real street data, specifically to re-check `false_transfer_across_barrier` for the right reason instead of by the accident of having no street graph at all.
2. Consider whether the straight-line-transfer behavior observed above needs an explicit assertion/regression test once street data exists.

Neither blocks starting **ROADMAP task 2** (acquire evidence and close the real feasibility gate): resolve source-use rights and gather the field-verified 12-case corpus with the maintainer/local verifier. That work is not something an agent can do alone — it needs an actual rights determination and actual field observations. Do not start ROADMAP task 3 (production data package) before task 2's real-data gate passes.
