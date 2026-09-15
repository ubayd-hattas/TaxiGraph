# Exact handoff to GPT-5.6 Sol

Start with **ROADMAP task 1: a technical feasibility spike**. Do not build a frontend, production importer, database migrations, or custom routing. Read [AGENTS](../AGENTS.md), [RESEARCH](RESEARCH.md), [DATA-SOURCES](DATA-SOURCES.md), [ARCHITECTURE](ARCHITECTURE.md), [DATA-MODEL](DATA-MODEL.md) and [MVP-SPEC](MVP-SPEC.md).

## Context you should not need to rediscover

- TaxiGraph is an original data/provenance/API layer for South African minibus taxis, beginning with a small Cape Town subset. Selected routing architecture: canonical data -> gated GTFS -> OTP/OSM -> TaxiGraph API -> eventual custom PWA/MapLibre.
- The workspace currently contains planning documents only and was not initialized as Git during architecture work. Inspect its current state before setup; do not assume package scripts or fixtures exist.
- Primary data: `https://citymaps.capetown.gov.za/agsext/rest/services/Theme_Based/ODP_SPLIT_6/FeatureServer/11`. On 2026-09-15 it returned 1,466 single-path polylines with only OBJECTID, ORGN, DSTN and length. No stops, service days, schedules, headways or fares. Nineteen rows have blank endpoint labels. Exact geometry can have conflicting destination names (20/127). See DATA-SOURCES for the full profile and query recipe.
- **Rights blocker:** `/iteminfo?f=json` says reproduction/transmission needs City permission. Do not fetch and commit a real fixture assuming “open portal” means open licence. First inspect metadata and any maintainer-supplied permission; keep real-use status blocked until its scope is clear. A replacement clearly licensed source is acceptable if provenance is preserved.
- No real operating observations, route directions, boarding points, independently verified journeys, or data-use permissions were supplied in this architecture task. Request these when needed for real mode; continue the independent software harness meanwhile. Do not ask the maintainer to rediscover the architecture.
- OTP baseline: **2.9.0, Java 25**, release commit `9babe45ffc9327933129f705c648137ecd96cdbe`. Use the release JAR/official container and pin checksum/digest. Published docs/examples can lag; tagged pom/tutorial support Java 25. Never silently downgrade to OTP1 or the Trufi wrapper's 2.8.1.
- GraphQL endpoint: `http://localhost:8080/otp/gtfs/v1`. The old REST planner is removed. Introspect the selected runtime and save one tested query rather than guessing its schema.
- Non-exact frequencies are implemented; OTP applies a full-headway allowance. Cape Town suitability is **not runtime-tested**. Validate actual behavior, boundaries and sensitivity.
- Trufi builder inspected at `0cc5b226078448a9533113e596acdc933528f056` (package.json 2.16.0): OSM-style inputs, root entry does not export `geojsonToGtfs`; frequency builder hardcodes `exact_times=1`; default long-lived calendars and endpoint generation are unsuitable. Do not begin by piping City GeoJSON into it.

## Implement first

Create a small Python package only under `spikes/feasibility/`:

```text
spikes/feasibility/
  README.md
  pyproject.toml
  src/taxigraph_spike/
  tests/
  fixtures/synthetic/       # shareable, unmistakably artificial software tests
  local/                   # ignored permitted real inputs, tools and evidence
  out/                     # ignored GTFS, graph, logs, reports
docs/FEASIBILITY-RESULTS.md
```

Keep the package small enough to replace after the experiment. Implement the following, in order:

1. **Prerequisites/manifest validation.** Check Java version, pinned OTP/validator artifacts and local input checksums. Use Python 3.13 as the research-compatible baseline unless a documented dependency requires otherwise. Pin dependency versions/lock resolution. A local venv is sufficient; Docker/WSL is optional, not assumed installed.
2. **Synthetic smoke fixture.** Prefer a small, appropriately licensed upstream OTP test fixture with recorded provenance, or construct an explicitly artificial network. Do not attach artificial operating values to real Cape Town routes. Include two directed transit patterns with a pedestrian transfer and negative controls. Reuse OSM tooling/fixtures for streets; do not implement a road graph.
3. **Minimal real-input contract.** Define required source/use-rights, directed variant, ordered boarding, service window, headway/timing evidence, dataset version and evaluation-case fields. Missing or contradictory required evidence yields `data_blocked`, listing fields/records. Empty inputs must not yield a misleading valid “real” feed.
4. **Narrow GTFS projection.** Map complete test/curated records to required tables using standard CSV/ZIP libraries. All output values must trace to fixture fields or an explicitly documented derivation. Write `exact_times=0` for an evidenced non-exact profile, no fare tables when unknown, finite calendar dates and an ID map. Reuse the external validator; no generic GTFS parser/graph algorithms.
5. **Validator and OTP orchestration.** Run the validator locally, inspect JSON notices/system errors, build/save/load OTP on loopback, capture build issues and graph manifest. Use a small overlapping OSM extract/fixture. Spawn/clean up only processes owned by the spike. On Windows, use hidden background processes and literal absolute paths.
6. **Query/evaluation harness.** Capture introspected schema and a working GraphQL query; evaluate mode/route/stop/transfer semantics, not just HTTP success. Capture time estimates separately from evidence claims. Report memory, startup/build times and query latency with hardware details.
7. **Real mode and report.** If eligible inputs are available, run the 12-case corpus and timing scenarios defined in MVP-SPEC. Otherwise demonstrate a clear blocked-real result and provide the exact missing evidence template. Do not proceed to a production/UI task on smoke success.

## Required command contract

Introduce and document these commands; they do not exist yet. Run from `spikes/feasibility` inside its virtual environment:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m taxigraph_spike check --mode smoke
python -m taxigraph_spike check --mode real --manifest local/real-manifest.json
```

`check` should execute the eligible chain and write a structured report with separate `software_status`, `real_data_status`, `rights_status`, and `journey_validation_status`. Use exit 0 for the selected mode's actual pass, 1 for a validation failure, 2 for missing prerequisites/evidence/rights. A blocked real run is not a test-suite failure if a unit test deliberately asserts this behavior, but it is not a successful real evaluation.

Pin the external binaries before execution. Under the wrapper, the intended command shapes are:

```powershell
java -jar local/tools/gtfs-validator-cli.jar -i out/feed.zip -o out/validator
java -Xmx2G -jar local/tools/otp-shaded-2.9.0.jar --build --save out/otp
java -Xmx2G -jar local/tools/otp-shaded-2.9.0.jar --load out/otp
```

These are setup targets, not commands run by the architecture agent. Resolve the validator's actual release filename into the manifest/local path and verify its runtime requirements. Put only the intended GTFS/PBF inputs in the OTP directory. The 2 GB heap is a starting cap for a tiny fixture, **not** a measured Cape Town requirement. Check pinned CLI help; report memory failure before raising the cap. Parse validator notices even when its process exits successfully. Keep the graph and its metadata/ID map inseparable.

## Evidence request when real mode needs input

Ask the maintainer for a permitted source or City permission reference; which small corridor they can verify; and dated evidence for actual directions, boarding/alighting places and rank entrances, recurring days/hours if known, observed departures/headways, and travel durations. Provide a compact blank record template and explain unknowns can remain blank, but will block real export. No invented sample values for real routes.

For each proposed journey record the independent expected route/boarding/transfer sequence, observation context and reviewer. At least the 12 cases specified in MVP-SPEC must be reviewed before tuning. Observations and a source licence can require time and human work; the agent must not pretend to finish those through code.

## How to decide viability

**Software viable:** a clean smoke run builds and queries OTP through the pinned interface; all smoke assertions pass. This only establishes integration.

**Real-data viable:** the complete MVP-SPEC gate passes: rights scope, required operational evidence, validator/build review, 12 independent categorical journey cases, evidence-backed timing sensitivity and reproducibility. Review walking across barriers and rank entrances explicitly. A hidden approximate engine timetable still affects chosen journeys, so suppressing UI times alone is insufficient.

**Blocked:** source rights, operational evidence or ground truth are missing. Record each missing field and who can obtain it; stop dependent work, keeping the useful harness complete.

**Representation no-go:** frequency modelling fails the observed service/corpus or results depend on unsupported assumptions. Save the minimal counterexample and update ADR. Do not respond by writing custom pathfinding or enabling unrestricted Flex automatically.

## Finish with

`docs/FEASIBILITY-RESULTS.md` containing exact versions/checksums, input provenance, commands/results, exclusion counts, corpus outcomes, resource measurements, timing-sensitivity changes and separate software/real/rights status. Include links to shareable reports and clearly identify local-only evidence. Recommend only the next bounded roadmap task. Do not claim a production app or a validated public route network exists.
