# Architecture decisions

Date: 2026-09-15. These are design decisions; implementation and real-world feasibility remain unproven. Evidence is in [RESEARCH](RESEARCH.md) and [DATA-SOURCES](DATA-SOURCES.md).

## ADR-001 — Reuse OTP for routing

**Accepted.** Select option A: custom TaxiGraph data/API/client with OTP, GTFS and OSM. Initial engine pin is OTP 2.9.0 with Java 25; record checksums at implementation.

OTP owns generic transit routing, pedestrian access and transfers. TaxiGraph owns evidence, identity, normalization, eligibility and presentation. Reject C/pgRouting as the MVP router because it would require original transit-state and walking integration without supplying missing transport facts. Reject the full B/Trufi app stack because it does not simplify the Cape Town data problem enough to justify framework/default assumptions.

Consequence: memory-heavy graph builds and time-dependent modelling must be measured. Reconsider only if a reproducible fixture exposes a relevant unsupported capability that cannot be handled honestly through standard inputs/configuration. Missing data alone is not a reason to write a router.

## ADR-002 — Operational evidence is a hard gate

**Accepted.** Route geometry alone remains candidate data. Real GTFS export requires evidence for the directed boarding pattern, service interval and temporal representation. Missing optional fares remain unknown.

Reject guessed daily calendars, constant headways/speeds, automatic reverse services and generated stops presented as surveyed. A syntactically valid feed does not establish a real taxi service. Artificial test fixtures are allowed only as clearly separate software tests, never as Cape Town observations.

Consequence: feasibility may end with a precise data acquisition blocker. That is a valid research result; it is not a passed real-journey milestone.

## ADR-003 — Non-exact frequency first; defer Flex

**Accepted conditionally on evidence.** Test ordinary GTFS with `exact_times=0` for a small, observed frequency-service subset. OTP's full-headway allowance requires sensitivity testing; do not promise timetable precision.

Reject `exact_times=1` as a convenience for taxis without fixed departures. Reject a citywide GTFS-Flex zone made from buffered route lines: availability/boarding semantics are not established. Continuous boarding and Flex remain possible future representations after specific evidence and tests. If frequency is unsuitable for departure-when-full operation, report that failure before changing the model.

## ADR-004 — Canonical model independent of GTFS

**Accepted.** Store source records, variants, claim provenance, uncertainty, verification and dataset versions independently. GTFS is a reproducible export with an ID map. JSON files first, PostGIS after feasibility.

Reject GTFS as the master database because it cannot naturally preserve contradictory GIS records, field-level confidence, or review history. Reject immediate database/migration work because the initial subset does not need it.

## ADR-005 — Selective Trufi reuse, no wholesale adoption

**Accepted.** Reference the builder's geometry/stop/fare workflows and server recipes. Do not make `trufi-gtfs-builder` the first exporter dependency: its OSM-centric input, non-exported root GeoJSON conversion, exact-frequency default, endpoint fallback and century-long calendar need substantial guarding.

A small canonical-to-GTFS table mapping using existing CSV/ZIP utilities is justified; mature GTFS validation remains external. A later OSM adapter may adopt the builder if a supported API, rights, stable IDs and semantic conformance tests are established. Do not copy large source blocks or maintain an avoidable fork. Archived resources and unclear-licence server modules are not deployment dependencies.

## ADR-006 — Custom client later

**Accepted.** Next.js/TypeScript PWA and MapLibre GL JS follow real feasibility. The public API shields clients from OTP's schema and returns TaxiGraph evidence. Reject frontend scaffolding as the first milestone and reject a Trufi Core branding-only MVP.

Consequence: more deliberate UI work later, but original taxi-specific presentation and a smaller mobile flow. Keep text itineraries usable without WebGL. Offline V1 scope is saved information/app shell, not fresh route computation.

## ADR-007 — City adapter seam, not a framework

**Accepted.** Carry city/source IDs, timezone and raw source extension data now. Implement one Cape Town adapter; extract a formal adapter protocol when a second source adapter is actually needed. OSMCommunityAdapter and GTFSAdapter are future directions, not empty classes to scaffold.

Consequence: international expansion is possible without prematurely forcing very different source capabilities into one lowest-common-denominator interface.

## ADR-008 — Restrictive source terms block publication

**Accepted.** The City's layer iteminfo requires permission for reproduction/transmission. General open-data branding is insufficient to ignore the specific notice. Resolve scope or use a clearly licensed source before retaining/distributing derivatives for that use.

Reject rehosting data/GTFS/graphs under the application's source-code licence. Keep OSM ODbL, upstream software licences and City rights distinct. Preserve evidence of permissions in the source manifest. No blanket legal clearance is claimed by this research.

## ADR-009 — Versioned graph promotion

**Accepted.** Canonical versions, GTFS exports, OSM extracts and OTP configs form a manifest-bound artifact bundle. Promote only after feed and journey checks; roll back the full bundle. Keep OTP private and expose a bounded TaxiGraph API.

Reject building/replacing a graph in the serving process on every user request, mutable `latest` dependencies, and a database change that silently leaves the active graph inconsistent. Start with one host plus an offline build job, not distributed infrastructure.

## ADR-010 — Data jobs in Python, product/API in TypeScript

**Accepted.** Use Python's established GIS tooling for normalization/QA and TypeScript for the eventual web/API. Share a versioned schema and artifact contracts. OTP Java remains an external runtime.

Reject choosing one language at the cost of rebuilding spatial primitives, and reject a separate Python web API solely because Python performs ingestion. Revisit this boundary only if implementation evidence demonstrates material duplication or deployment cost.
