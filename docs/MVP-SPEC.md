# MVP scope and gates

The first milestone is **correct routing of a small, manually verified set of real Cape Town journeys**. A map demo, a passing GTFS validator, and a successful OTP startup are not that milestone.

Current status: architecture complete; implementation absent; real operational evidence and source-use rights unresolved. [SOL-HANDOFF](SOL-HANDOFF.md) defines the first task. No existing City row is pre-approved for routing.

## 1. Feasibility spike

Deliver a command-line experiment, an auditable fixture corpus, pinned tool/artifact manifests, and a written go/blocked/no-go report. No database, frontend, public deployment, full importer or generic router.

### Two separate results

- **Software smoke:** a clearly artificial GTFS test network exercises the validator, OTP graph construction, GraphQL and test harness. Its records and values are fictional software inputs with no claim about Cape Town. It may pass while real-data feasibility is blocked.
- **Real-service feasibility:** a small lawful source subset plus dated manual evidence produces an eligible feed and plausible journeys. Incomplete Cape Town records must fail export rather than inherit values from the smoke fixture.

Target 3–5 directed variants in one practical corridor cluster, enough for direct and one-transfer tests; do not force a particular corridor before evidence exists. Begin source investigation with Bellville-linked candidates such as OBJECTIDs 1–4, without asserting that these are correct or sufficient. The maintainer/local verifier supplies and approves the actual journeys and operating facts.

### Corpus and acceptance

Define **12 cases before tuning**:

- 3 direct taxi journeys;
- 3 one-transfer journeys, including a transfer with a real pedestrian walk;
- 2 walking access/egress cases with a meaningful barrier or entrance constraint;
- 4 negative cases: unsupported reverse direction, false transfer across a barrier, outside the verified service window, and outside the verified coverage.

Each case records origin/destination coordinates, service date/time, allowable variants, actual boarding/alighting locations, allowed transfer points, local evidence/reviewer/date, expected result or rejection reason, and tolerances. Freeze the corpus version. Expected journeys come from independent observation/local review, not from OTP's output. Changes to expectations require evidence and a visible revision.

Pass requires all 12 categorical expectations: an acceptable itinerary in the top three for positive cases, all returned top-three taxi legs/boarding/transfers supported by the corpus evidence, and no prohibited taxi journey in negative cases. Alternative walking or supported-direction itineraries may be valid; negatives must assert the prohibited property rather than accidentally forbid all alternatives. Fail if a plausible answer only appears after broad unsafe stop snapping or a made-up return service.

Also require:

1. Required operational claims and rights scope recorded for every real exported record; unresolved optional fare claims omitted.
2. MobilityData report has no errors; every warning has an explicit disposition. Inspect OTP build issues, stop-to-street links, shape/stop alignment and ID mappings.
3. Full-headway behavior and travel-time assumptions tested at low/central/high **evidence-backed** estimates. Record all acceptable-set/rank changes; all categorical journey expectations must still hold. Do not call those ranges calibrated statistical confidence intervals without evidence.
4. Dates at service-window boundaries, overnight semantics when applicable, and departure-minute perturbations produce explainable results. No future “service confirmed” claim from an expired observation window.
5. Rebuild from pinned inputs yields equivalent IDs/feed tables and categorical journey outcomes; record graph checksums without assuming binary graph determinism.
6. Measure build/runtime memory, graph size, startup and query latency on identified hardware. Report whether the measured footprint fits a proposed student-run host; no pretense that a citywide capacity estimate has been tested.

**Go:** all of the above passes and a realistic path exists to maintaining evidence. **Blocked:** smoke can work but rights/observations/ground truth are missing; document exact inputs needed. **No-go for this representation:** observed service cannot be represented usefully or outcomes are unstable; record the counterexample and revise ADR before expanding implementation.

## 2. Private technical MVP

Only after real feasibility passes. Make the validated slice reproducible and maintainable: source snapshot acquisition, canonical schema/PostGIS, reviewed identity/boarding data, gated GTFS export, graph promotion, and a private versioned API. CLI/API results are sufficient; no polished application requirement.

Acceptance: the original corpus still passes; a second snapshot produces a reviewable change report; known duplicate/name-conflict examples remain traceable; stale/withdrawn data is excluded; restart/restore and rollback work; API and graph version IDs agree. A second person can reproduce the results from the runbook and permitted inputs. Missing evidence is a typed failure, not an empty success response.

## 3. Public MVP

Publish a **limited verified coverage area**, not all 1,466 source records. The user can enter origin/destination via coordinates, map selection, or verified place/rank search, request a plausible journey, inspect walking/taxi/transfer legs, and see where to board/change/exit with evidence and freshness. Full address autocomplete is not required.

Acceptance:

- Cleared rights for displayed/served artifacts; correct source/software/map attribution; no unresolved required service claims in the released graph.
- Maintainer signs off current coverage and a documented refresh/expiry policy. Manual withdrawal/review is operational; a live disruption feed is not promised.
- All real corpus tests pass against the exact promoted build. Conduct a small external rider review in the covered area and record issues/resolutions.
- Text itinerary, small-screen/touch operation, keyboard access, readable uncertainty and no-result states; unsupported WebGL still leaves useful text.
- Mobile check on a named ordinary Android device and throttled connection. Provisional targets: useful text response within 5 seconds, API p95 below 3 seconds at five simultaneous journey requests on the chosen host. Record measured results; revise targets with reasons, not silently.
- Demonstrated graph rollback, database/artifact restore, provider/OTP failure handling, bounded request rates and no default storage of precise user trip logs.
- Offline app shell/saved itinerary is labelled saved and dated; new routing requires connectivity. No fabricated precision in fares, departures or arrivals.

## 4. Portfolio-complete V1

Public MVP plus reproducible engineering evidence: architecture/ADRs, source/profile report, conformance and journey test results, reproducible demo using shareable inputs, benchmark/runbook, contribution instructions and a recorded account of a real data defect and its correction. Show what TaxiGraph owns and why OTP/MapLibre were reused.

One well-documented city slice is enough. A second city, a mobile store release, and a bespoke routing algorithm are not portfolio requirements. If data rights prevent sharing real fixtures, share the harness with a synthetic demonstration and clear instructions for obtaining permitted real inputs; do not claim it reproduces the field validation unaided.

## Out of scope through public MVP

Payments/ticketing; bookings; real-time vehicles/capacity; operator dispatch; complete citywide coverage; nationwide expansion; automatic community edits or reputation; crowd tracking; fare optimization; invented ETAs; AI route inference; Flex/continuous pickup; turn-by-turn live navigation; safety guarantees; full offline pathfinding; other transit modes; public bulk redistribution without rights; self-hosted countrywide map/search infrastructure; Kubernetes and generalized plugins.

Scope changes require updating this specification, ROADMAP and ADR. Do not rename an unverified citywide map a routing MVP to bypass the gates.
