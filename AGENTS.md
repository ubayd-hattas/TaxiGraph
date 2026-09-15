# TaxiGraph agent instructions

## Start here

Read [architecture](docs/ARCHITECTURE.md), [MVP gates](docs/MVP-SPEC.md), and the relevant [roadmap task](docs/ROADMAP.md) before changing code. The next implementation task is the bounded feasibility spike in [SOL-HANDOFF](docs/SOL-HANDOFF.md). Inspect existing files, tests, dependencies, and upstream components before writing replacements.

This workspace was empty and was not a Git repository when the architecture work began on 2026-09-15. The current deliverable is documentation only. Commands and component paths described as future contracts are not implemented yet. Do not claim that an OTP graph or real journey has been validated.

## Architecture boundaries

- Use OpenTripPlanner (OTP) for transit routing, transfers, and OSM walking. Initial research pin: OTP 2.9.0, Java 25. Recheck release advisories before installing; change pins explicitly.
- Use MapLibre GL JS for the eventual map. No frontend until the feasibility gate passes.
- TaxiGraph owns source adapters, canonical data, identity resolution, provenance, verification, freshness, export eligibility, and the public API/presentation.
- GTFS is a derived interoperability artifact, not the canonical database. PostGIS is storage and spatial validation, not a second router.
- Start the spike with files. Add PostGIS after feasibility. No pgRouting, custom pathfinder, OSM road-graph builder, homegrown GTFS parser, or generalized plugin framework.
- Reuse geospatial libraries and MobilityData's GTFS validator. Python handles data jobs; TypeScript handles the later API/client. Share a versioned schema, not duplicated domain logic.
- Trufi is an inspected source of reusable parts, not an approved turnkey stack. Its builder has unsuitable defaults; read RESEARCH before adopting it.

## Transport truth and provenance

- Never invent schedules, headways, fares, operating days, operator identities, boarding permissions, or reverse services. Unknown is null/unknown, not zero, daily, free, or bidirectional.
- Geometry endpoints and intersections are candidates, not verified stops or transfers. Nearby routes do not establish a usable interchange. Left-side boarding and actual pedestrian access need evidence.
- Preserve raw values separately from normalization. Every imported assertion needs source, source record ID, retrieval time, dataset version, transformation version, and evidence status.
- Distinguish source publication time, retrieval time, and field verification time. A fresh download does not refresh an old route.
- Keep conflicting claims and merge history. Never merge solely on matching names or line similarity. OBJECTID is source-local, not a permanent global route ID.
- Artificial software-test fixtures must be clearly synthetic, separate from real Cape Town datasets, and impossible to publish as real service. They cannot satisfy the real-journey gate. Do not fill missing Cape Town values with test constants.
- Export real service only when required claims and the stated validity window have evidence. Estimates need an explicit method and observations; engine times must not become advertised departure times.
- **City layer metadata requires reproduction/transmission permission.** Record permission covering the intended use or select a clearly licensed replacement before retaining/distributing real fixtures, GTFS, tiles, or graphs for that use. See DATA-SOURCES. A public URL is not an open licence.

## Implementation conventions

- Keep changes limited to the active task. Prefer small typed functions, explicit units (`*_seconds`, `*_meters`), and boundary validation.
- Store coordinates as WGS84 longitude/latitude; transform to a suitable metric CRS for geometric comparisons. Cape Town research used EPSG:32734. Do not measure meters in degrees or treat Web Mercator lengths as ground truth.
- Store timestamps in UTC and service dates/times with `Africa/Johannesburg`. Preserve GTFS times after 24:00 and service-date semantics.
- Pin dependencies, Java/OTP artifacts, OSM extracts, and validator versions; retain checksums and build manifests. Do not use mutable `latest` in reproducible builds.
- Keep raw data, generated graphs, downloaded JARs, large extracts, secrets, and personal verification contacts out of Git. Do not log precise journey coordinates by default.
- Use existing serializers/parsers for CSV, ZIP, GTFS, and geometry. A narrow canonical-to-GTFS mapping is TaxiGraph work; a generic GTFS framework is not.

## Validation commands

These are the required **future command contracts**, introduced by the task that owns them. Missing commands are not passing checks. Read SOL-HANDOFF for arguments and setup.

| Stage | Commands |
|---|---|
| Documentation only, now | `rg --files -g '*.md'`; verify relative links, fenced blocks, and internal consistency; `git diff --check` only once Git exists |
| Spike, from `spikes/feasibility` | `python -m pytest`; `python -m taxigraph_spike check --mode smoke`; `python -m taxigraph_spike check --mode real --manifest <path>` |
| Data package, when introduced | `python -m pytest`; `python -m ruff check .`; `python -m mypy src` from `packages/data` |
| API/web, when introduced | `npm ci`; `npm run lint`; `npm run typecheck`; `npm test`; `npm run build` from its package/workspace root |
| Graph/release changes | Run the real journey evaluation against the exact candidate graph and inspect MobilityData JSON/HTML reports and OTP build issues; do not rely on process exit status alone |

Tests must cover relevant failure modes: truncation/schema drift; missing evidence; stable IDs and collisions; coordinate order; ambiguous direction; loops; false transfers across barriers; service dates; fare unknown versus zero; frequency sensitivity; stale/withdrawn data; graph/API manifest mismatch. Network-dependent tests must be separate from deterministic fixture tests. Do not add tests that merely repeat implementation.

## Definition of done

1. Acceptance criteria for the active task are met, or the exact missing external evidence is documented without claiming success.
2. Appropriate checks ran; report commands, results, and any checks that could not run.
3. Provenance and uncertainty survive every changed boundary; real-data release eligibility is enforced.
4. No unrelated scaffolding, generated data, or third-party source was added.
5. Update affected docs and ADR when architecture, schema, dependency assumptions, or gates change. Preserve historical research dates rather than rewriting old measurements as current.
6. Summarize behavior, validation, limitations, and the next bounded task. A smoke-test pass alone does not authorize a UI-first implementation or a public launch.
