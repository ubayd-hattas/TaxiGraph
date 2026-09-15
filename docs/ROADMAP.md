# Sequential implementation roadmap

Run one bounded task per agent prompt. Read [AGENTS](../AGENTS.md) and the referenced documents first. **Tasks 1–2 are feasibility work. No production packages, database or UI before task 2 passes.** A missing rights/evidence gate pauses dependent work; it does not authorize guessed transport facts.

Paths below are intended locations, not files that already exist. GPT-5.6 Sol is the intended implementation agent. “Medium/high” are suggested reasoning effort for the task, not claims about model benchmarks; high suits semantic/geospatial integration, medium suits established contracts. A more capable architecture reviewer is useful only for unresolved counterexamples, not routine scaffolding.

## 1 — Build the bounded feasibility harness

- **Objective:** implement [SOL-HANDOFF](SOL-HANDOFF.md): environment checks, clearly synthetic smoke corpus, pinned validator/OTP orchestration, GraphQL response capture, missing-real-evidence checks and a result report. Attempt real evaluation only with eligible inputs; otherwise name the blockers.
- **Dependencies:** current docs; Java 25 or an approved pinned container; permitted test inputs. No prior application code.
- **Expected files:** `spikes/feasibility/{README.md,pyproject.toml,src/taxigraph_spike/,tests/,fixtures/synthetic/}`; ignored `local/` and `out/`; `docs/FEASIBILITY-RESULTS.md`. Do not commit downloaded runtimes/graphs.
- **Acceptance:** one reproducible smoke command exercises validator -> OTP -> GraphQL -> assertions. Real mode fails clearly on missing rights, direction, boarding, calendar, headway or travel-time evidence. Report smoke and real status separately.
- **Tests:** artificial direct/transfer/walking graph; invalid feed; API schema mismatch; missing inputs; forbidden promotion of synthetic artifacts. No real Cape Town defaults.
- **Reasoning/model:** Sol, high.

## 2 — Acquire evidence and close the real feasibility gate

- **Objective:** with the maintainer/local verifier, select 3–5 directed variants and the 12-case corpus; complete permitted real inputs and the low/central/high timing evaluation. Resolve the representation before production work.
- **Dependencies:** task 1; applicable source-use rights and independently verified observations. The agent may prepare blank collection forms/checklists; it cannot supply field observations itself.
- **Expected files:** versioned evidence/manifest schema and shareable examples under the spike; actual restricted records in ignored storage; updated `docs/FEASIBILITY-RESULTS.md` and source rights references.
- **Acceptance:** every criterion in MVP-SPEC's real feasibility section passes, or a concrete blocked/no-go report names the missing observations/rights or failing counterexample. Freeze corpus before tuning and archive signed/reviewed evidence scope privately where appropriate.
- **Tests:** 12 categorical cases; temporal boundaries, reversed direction, false transfer; timing sensitivity; reproducibility; memory/latency measurements. A smoke-only pass does not complete this task.
- **Reasoning/model:** Sol, high; human/local evidence review required.

## 3 — Establish the production data contract and checks

- **Objective:** promote only useful spike lessons into a minimal typed Python data package and versioned JSON Schema. Establish provenance, unknown/conflict states and deterministic fixture checks.
- **Dependencies:** task 2 pass.
- **Expected files:** `packages/data/{pyproject.toml,src/taxigraph_data/,tests/}`, `schemas/`, lock/pin files, minimal CI and contribution commands. No web package yet.
- **Acceptance:** source/canonical/export/graph manifests validate; IDs and units are explicit; synthetic fixtures and restricted data are kept separate. AGENTS command contracts exist for this package.
- **Tests:** schema rejection, round-trip unknowns, coordinate order, temporal types, ID stability/collisions, source lineage. `pytest`, Ruff, mypy.
- **Reasoning/model:** Sol, medium.

## 4 — Implement the Cape Town source adapter

- **Objective:** reliable snapshot acquisition and schema mapping, with rights scope and completeness checks.
- **Dependencies:** tasks 2–3; permitted access/use scope.
- **Expected files:** `packages/data/src/taxigraph_data/adapters/cape_town_arcgis.py`, HTTP client wrapper, snapshot manifest/report, small permitted or synthetic response fixtures.
- **Acceptance:** metadata/count/IDs/records agree; bounded batches/retries; HTTP-200 ArcGIS errors fail; changed schema or concurrent source changes become explicit failures; no silent truncation. Counts are observations, not hardcoded 1,466 forever.
- **Tests:** missing/repeated IDs, transfer limit, schema drift, 429/timeout, interrupted run, source-ID reuse and unknown fields. Live read probe separate from CI.
- **Reasoning/model:** Sol, high.

## 5 — Normalize geometry and review route identity

- **Objective:** produce canonical candidates and explainable QA/duplicate proposals without deleting source truth.
- **Dependencies:** task 4.
- **Expected files:** normalization/geometry/identity modules, reviewed alias/merge decisions, QA report format and fixtures.
- **Acceptance:** correct CRS and metric checks; original geometry preserved; blanks become unknown; exact/reverse/near matches remain review candidates. Same geometry with conflicting names is flagged. Loops retain ordered semantics.
- **Tests:** analogue of City 20/127 contradiction; spelling variants; reversed lines; multipart lines; retracing; ID stability after source reordering; merge/rejection lineage.
- **Reasoning/model:** Sol, high.

## 6 — Add evidence-backed boarding and service review

- **Objective:** ingest curated observations and decisions for directions, rank entrances, ordered boarding points and temporal profiles. No contributor accounts/UI.
- **Dependencies:** task 5; task 2 evidence protocol.
- **Expected files:** review/evidence modules, JSON/CSV collection template, eligibility policy and exclusions report.
- **Acceptance:** route-specific boarding permissions and pedestrian entrances are distinguished from rank footprints. Missing service claims stay unknown; contradictory/expired required evidence blocks routing. Personal contacts are not public fields.
- **Tests:** wrong-side/remote boarding, repeated loop stop, unsupported reverse trip, unknown versus zero fare, observed-date scope, conflicting claims, expiration.
- **Reasoning/model:** Sol, high.

## 7 — Build the production GTFS export adapter

- **Objective:** deterministic canonical-to-GTFS projection and a provenance ID map for eligible records only. Reuse CSV/ZIP tooling and the mature validator.
- **Dependencies:** task 6.
- **Expected files:** export mapping/eligibility modules, manifest/ID map schemas, GTFS golden fixtures and validator wrapper.
- **Acceptance:** bounded dates, non-exact frequency only where evidenced, stable IDs, ordered shapes/stops and evidence-derived timing; no unsupported fare rows or invented operators. All exclusions carry reasons. Review any proposed Trufi adoption against RESEARCH before adding it.
- **Tests:** table/reference validity; exact/non-exact behavior; no 2000–2100 or implicit daily calendar; no endpoint fallback; timing/shape order; synthetic feed cannot promote; validator errors/warnings inspected.
- **Reasoning/model:** Sol, high.

## 8 — Add PostGIS persistence and versioned releases

- **Objective:** persist canonical history, evidence, review and dataset versions when repeated imports need it.
- **Dependencies:** tasks 3–7; file contract already proven.
- **Expected files:** database schema/migrations, repository layer, local Compose config, backup/restore runbook. Migrations begin in this future task only.
- **Acceptance:** canonical file and database representations preserve the same meaning; immutable released versions and review history; transactionally consistent exports; spatial indexes for lookup/QA. No pgRouting extension.
- **Tests:** fixture round trip, rollback, referential integrity, conflicting concurrent edits, snapshot isolation, backup restore; compare file-export and DB-export tables.
- **Reasoning/model:** Sol, high.

## 9 — Automate graph builds and regression promotion

- **Objective:** reproducible OTP build, evaluation and atomic promotion tied to dataset/OSM/tool versions.
- **Dependencies:** tasks 7–8.
- **Expected files:** `ops/otp/`, build/promote scripts, artifact manifests, corpus runner and resource report.
- **Acceptance:** pinned OTP 2.9.0/Java 25 baseline or explicitly reviewed upgrade; no build in the request path; feed validation plus real journey checks gate promotion. Rollback restores graph and metadata together. A dataset withdrawal can suppress stale results immediately.
- **Tests:** 12-case corpus and timing scenarios; corrupt input, mismatched map/graph ID, failed build, rollback and restart; measure memory and queries on the proposed host.
- **Reasoning/model:** Sol, high.

## 10 — Expose the private TaxiGraph API

- **Objective:** bounded versioned journey/route/dataset/coverage API with OTP adaptation and provenance enrichment. This completes the private technical MVP with preceding tasks.
- **Dependencies:** task 9.
- **Expected files:** a minimal TypeScript API package or Next.js server boundary, `schemas/api/`, OTP query/schema snapshots, integration tests. No separate Python web service.
- **Acceptance:** private OTP only; known query shapes; validated coordinates/time; coherent dataset/graph IDs; missing fare remains unknown; clear outside-coverage/window/unavailable reasons. Response times distinguish estimates from promised departures.
- **Tests:** fixed OTP response mapping, ID lookup failure, timeouts, service-window/coverage boundaries, stale/withdrawn variants, malformed inputs, rate/concurrency limits. Run npm lint/typecheck/tests/build.
- **Reasoning/model:** Sol, high.

## 11 — Build the focused browser client

- **Objective:** origin/destination entry, text journey, map legs and explicit boarding/transfer/exit guidance in the verified coverage area.
- **Dependencies:** task 10/private technical MVP.
- **Expected files:** Next.js client views, MapLibre integration, lightweight verified-place search, service worker/app manifest only for the stated PWA scope.
- **Acceptance:** public API only; mobile and keyboard usable; provenance/estimate labels clear; missing WebGL/provider service leaves usable text. Verify MapLibre v6 worker assets in a production build. No full address geocoder or offline router requirement.
- **Tests:** end-to-end covered journey and no-result cases; source labels; worker/tile loading; WebGL failure; stale saved journey; touch/keyboard and ordinary Android measurements.
- **Reasoning/model:** Sol, medium; high for a difficult integration failure.

## 12 — Operate review, freshness and recovery

- **Objective:** make limited public operation maintainable by one person: review pending changes, enforce validity, revoke variants, monitor failures and restore service.
- **Dependencies:** tasks 9–11.
- **Expected files:** admin CLI/manual review process, runbooks, scheduled snapshot checks, expiry policy, bounded observability config, privacy/attribution notices.
- **Acceptance:** repeated import cannot reset operational freshness; submissions require moderation; withdrawal hides affected results then rebuilds; backups and previous artifacts restore; no precise journey logs by default. Basemap/search provider terms and quotas documented.
- **Tests:** stale/expired/withdrawn lifecycle, source outage, OTP/provider outage, restore drill, rollback, moderation rejection, log inspection. No new microservice platform.
- **Reasoning/model:** Sol, medium.

## 13 — Release the limited public MVP

- **Objective:** verify and publish exactly the tested coverage, with an honest engineering record and an operations owner.
- **Dependencies:** tasks 1–12; rights and current evidence rechecked; maintainer's release sign-off.
- **Expected files:** final release manifest, current corpus/benchmark report, user limitations/coverage page, contribution instructions, updated docs and deployment runbook.
- **Acceptance:** all public MVP criteria pass on the exact release; local rider review completed; attribution and derivative rights clear; public uptime/resource plan fits measured host. Portfolio V1 is documentation/demo polish after this, not a new feature set.
- **Tests:** full relevant CI; real corpus on release host; mobile/accessibility checks; declared load targets; restore/rollback; source and graph version displayed correctly.
- **Reasoning/model:** Sol, high for release assessment. Any explicit publication approval belongs to this concrete reviewed release, not to empty scaffolding.

## Reusable prompt shape

> Implement roadmap task N only. Read AGENTS.md and its dependencies, inspect the existing code and upstream component first, and state the task's acceptance criteria. Preserve unknown transport facts and provenance. Run the relevant documented commands, update the task's report/docs, and finish with actual results and remaining blockers. Do not advance through an unpassed feasibility or data-rights gate.
