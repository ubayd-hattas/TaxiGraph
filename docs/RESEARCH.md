# Research record

Inspected 2026-09-15. **Decision:** use OTP behind TaxiGraph's own data and API boundary; start with a file-based spike. **Finding:** the City route layer alone cannot honestly provide the operational inputs needed for passenger routing. No feed was generated and no OTP instance was run in this architecture task.

## Evidence method

Read public repository trees through GitHub's API, then selected source files at the revisions below through raw URLs/API content responses. Read official documentation and ArcGIS layer metadata; queried all 1,466 City features, count, and object IDs. Used throwaway Python analysis with Shapely 2.1.2 and pyproj 3.8.0 outside the project. Results and reproduction details are in [DATA-SOURCES](DATA-SOURCES.md). Temporary downloads are not repository dependencies or a retained dataset.

Some web query URLs failed even though direct HTTP queries worked. Several later requests stalled and were stopped. Failures are identified below; they are not evidence of an empty dataset. No external repositories were copied into TaxiGraph. No real-world field observations were made.

## Upstream inventory

Revisions are observations, not blanket dependency approvals. For the Trufi entries, SHA links identify the inspected tree; named modules below identify the code actually read.

| System | Inspected revision | Licence evidence | Disposition |
|---|---|---|---|
| [Trufi GTFS builder](https://github.com/trufi-association/trufi-gtfs-builder) | [0cc5b226](https://github.com/trufi-association/trufi-gtfs-builder/tree/0cc5b226078448a9533113e596acdc933528f056), 2026-09-14; package.json 2.16.0 | package.json declares ISC; no root LICENSE in tree, GitHub licence detection null | Study/reuse only behind conformance checks; not the initial exporter dependency |
| [Trufi Core](https://github.com/trufi-association/trufi-core) | [f2057f91](https://github.com/trufi-association/trufi-core/tree/f2057f9196d85be6829fa29a8cd72da0b19fc3d7), 2026-09-13 | GPL-3.0 in repository/README | Reference client/offline design; no code copied into custom web client |
| [Trufi server resources](https://github.com/trufi-association/trufi-server-resources) | [368b5a2f](https://github.com/trufi-association/trufi-server-resources/tree/368b5a2f9275bc52510f144a4355266ac40b26e4), last commit 2024-03-10 | MIT | Archived 2026-02-03; reject as deployment baseline |
| [Trufi server](https://github.com/trufi-association/trufi-server) | [b0d57942](https://github.com/trufi-association/trufi-server/tree/b0d57942ee13d64179a8cf65762b55790a1cb3d4), 2026-05-28 | No root licence detected; README licence section only names Trufi | Reject for MVP: extra .NET gateway and analytics database |
| [Trufi server planner](https://github.com/trufi-association/trufi-server-planner) | [be0342a8](https://github.com/trufi-association/trufi-server-planner/tree/be0342a816b28221934721403f5a3c8452c06b6a), 2026-08-25 | No root licence detected; underlying Core package GPL | Reference only; licence must be resolved before reuse |
| [Trufi server OTP](https://github.com/trufi-association/trufi-server-otp) | [03c3a123](https://github.com/trufi-association/trufi-server-otp/tree/03c3a12386128992d0efece3bcee2aabaa7aa209), 2026-02-04 | No root licence detected | Deployment recipe reference, not copied |
| [OpenTripPlanner](https://github.com/opentripplanner/OpenTripPlanner) | [v2.9.0](https://github.com/opentripplanner/OpenTripPlanner/releases/tag/v2.9.0), release commit [9babe45f](https://github.com/opentripplanner/OpenTripPlanner/commit/9babe45ffc9327933129f705c648137ecd96cdbe) | LICENSE: LGPL-3.0-or-later, incorporated notices | Selected routing engine |
| [MapLibre GL JS](https://github.com/maplibre/maplibre-gl-js) | Latest release observed [v6.9.1](https://github.com/maplibre/maplibre-gl-js/releases/tag/v6.9.1), 2026-09-14; tree/LICENSE inspected at [dda75ad4](https://github.com/maplibre/maplibre-gl-js/tree/dda75ad45d7e9d19f56af30da37780e28bc43a33) | BSD-3-Clause with incorporated-code notices | Selected eventual renderer |

OTP development tree was also inventoried at `a0b62f69fc543e84687752e17dae8a66b01c5e28`; the decision uses release-specific source, not that development branch. Documentation landing-page version selectors and example JAR names lag the release: prefer the release page and tagged `pom.xml`.

## Trufi: findings from implementation

### Builder

Read `src/index.ts`, `src/types.ts`, `src/geojson_to_gtfs/{index,gtfsBuilders,duration,fares}.ts`, package.json, and README. [Pinned builder functions](https://github.com/trufi-association/trufi-gtfs-builder/blob/0cc5b226078448a9533113e596acdc933528f056/src/geojson_to_gtfs/gtfsBuilders.ts), [entry point](https://github.com/trufi-association/trufi-gtfs-builder/blob/0cc5b226078448a9533113e596acdc933528f056/src/index.ts).

Verified:

- The internal GeoJSON conversion consumes collections grouped by route with OSM-style properties and geometry node IDs. Plain ArcGIS GeoJSON is not a drop-in input. The root module exports `osmToGtfs`, OSM readers, and helpers; `geojsonToGtfs` is an internal module, not a root named export.
- `GTFSBuilders` allows injected builder functions internally. A wrapper would need to confirm a supported callable path and preserve TaxiGraph IDs without pretending they are OSM IDs.
- `fakeStops` begins at every OSM way node; subsequent segment merging/gap filling uses a default 100-meter gap threshold. This is computational discretization, not evidence that boarding is possible there.
- `customStops` matches nearby supplied points, with a default 200-meter radius. Unmatched first/last points still create geometry-based stops. `rightSideOnly` is optional and false by default; enabling right-side-only matching blindly would be inappropriate for Cape Town.
- `frequenciesBuilder` writes **`exact_times: 1`**. An informal headway feed needs a deliberate non-exact representation, not this implicit schedule. The alternative expanded-trip mode also creates precise departures.
- Calendar construction uses a reference week, strips public/school-holiday selectors, and emits 2000-01-01 through 2100-01-01. TaxiGraph must supply bounded evidence dates and exceptions instead.
- Defaults include a daily 06:00–23:00 window, 300-second headway and 50 km/h speed fallback (`duration.ts`). These are library defaults, not Cape Town facts.
- Stop times derive from duration or speed, distributed over straight-line distances between retained stops. Sparse stops can therefore underrepresent winding routes. Test shape-distance-based allocation where supported by actual timing evidence.
- Fare functions omit unknown fares, support OSM charges/resolvers, and emit Fares V1. Conflicting variant fares can resolve to a selected lower fare with a warning. TaxiGraph must preserve conflicts rather than silently advertise that resolution.

Judgment: useful reference and possible future OSM adapter dependency, but adapting this OSM-centric pipeline for a tiny curated City dataset introduces avoidable policy overrides. The spike should explicitly map approved canonical records to GTFS tables using ordinary CSV/ZIP tools and validate them with the mature validator. This is a narrow export adapter, not a new GTFS parser. No Trufi fork is planned.

### Core, city configuration, and offline

The current Core is a Flutter/Dart package monorepo. Inspected the tree, README, configuration/composition in `apps/example/lib/main.dart`, OTP 2.8 query file, `trufi_core_planner/lib/src/services/gtfs_routing_service.dart`, and `trufi_core_search_locations/lib/src/services/offline_search_data_service.dart`.

The [example app configuration](https://github.com/trufi-association/trufi-core/blob/f2057f9196d85be6829fa29a8cd72da0b19fc3d7/apps/example/lib/main.dart) sets city/map center, language, routing providers, search services and fare-screen values. It uses a local GTFS planner and MBTiles on non-web platforms; the web branch uses the remote planner and disables those offline map engines. It combines offline search with Photon. The manually configured fare screen is not proof that GTFS fares are automatically displayed, and its example prices are not relevant to Cape Town.

The OTP client has separate providers for 1.5, 2.4, and 2.8; compatibility with 2.9 was **not executed**. The local planner uses GTFS indexes; its route service reports straight-line walking distances and favors fewer transfers. These are not equivalent to OTP's OSM pedestrian paths, especially across railways, divided roads, or inaccessible rank entrances. The newer server-planner exposes that same Dart planner over HTTP; “offline” describes local server data, not a browser magically routing offline.

Offline location search reads bundled compact JSON street/junction data. [osm-search-data-export](https://github.com/trufi-association/osm-search-data-export) (README/root tree inspected, MIT; commit not pinned) accepts PBF/Overpass and emits JSON, compact JSON, and SQLite. It is a possible later search-data tool. Search, map caching, and route computation are separate offline capabilities. Do not port the Dart planner to JavaScript for MVP.

### Server/resource builders

The archived resources tree contains PBF, MBTiles, static tile, GTFS, graph, and Photon builders with country/city configuration and bounding boxes. Its old recommendation to choose OTP 1.5 for informal transport is not a current OTP limitation. The successor server-otp README/tree defaults to OTP 2.8.1/Java 21 and offers version-specific Dockerfiles; TaxiGraph's 2.9 baseline needs Java 25. Its readme's “latest stable” label is stale.

The newer server is a .NET/YARP reverse proxy with PostgreSQL request analytics. It does not supply TaxiGraph's canonical data layer. The modular tile server and Photon services could help a larger self-hosted deployment, but each adds operations and licensing checks. Start with standard reverse proxy/container practices and a contracted map/search provider later. Legacy `geojson-to-gtfs` and `osm-public-transport-export` were linked from Core; direct page retrieval failed, so their implementation was not evaluated or selected.

## OTP: release-specific findings

Selected **2.9.0**, the latest stable release returned by GitHub's release redirect during this research. This is not an assertion of a vendor support SLA. Tagged `pom.xml` sets compiler release 25; tagged Basic Tutorial recommends Java 25. Do not copy Java 21 from the Trufi wrapper. [Tagged tutorial](https://github.com/opentripplanner/OpenTripPlanner/blob/v2.9.0/doc/user/Basic-Tutorial.md), [pom](https://github.com/opentripplanner/OpenTripPlanner/blob/v2.9.0/pom.xml).

- Build a graph from local GTFS ZIP and overlapping OSM PBF; save and serve the resulting artifact. Separate build memory from runtime memory. OTP is in-memory; no PostgreSQL connection is required by its core routing process. Graphs are disposable derived artifacts, version-bound to their engine/config/inputs.
- Use [GTFS GraphQL](https://docs.opentripplanner.org/en/v2.9.0/apis/GTFS-GraphQL-API/) at `/otp/gtfs/v1`. Transmodel GraphQL is another API. Tagged `doc/user/apis/Apis.md` says the old REST API was removed in 2025. Freeze an introspected schema and query fixture in the spike; do not copy OTP1 `/routers/default/plan` calls.
- Read `application/src/main/java/org/opentripplanner/gtfs/mapping/FrequencyMapper.java`, `transit/model/timetable/FrequencyEntry.java`, and `routing/algorithm/raptoradapter/transit/frequency/TripFrequencyBoardSearch.java`. The mapper preserves non-exact frequencies; search calls the frequency implementation. `routingSlack()` adds a full headway for non-exact service. Average-wait behavior is not supported there. [Frequency code](https://github.com/opentripplanner/OpenTripPlanner/blob/v2.9.0/application/src/main/java/org/opentripplanner/transit/model/timetable/FrequencyEntry.java).
- Frequency support does not infer service windows, headways, or travel times. Missing these cannot be repaired by choosing a different API. Departure-when-full behavior may be poorly approximated even by observed average headways.
- OSM supports walking access, egress, and street-based transfers. Correct links and permitted boarding points still need validation. A GTFS shape is not evidence of a transfer wherever it crosses another shape.
- [Flex documentation](https://docs.opentripplanner.org/en/v2.9.0/sandbox/Flex/) supports the March 2024 adopted specification behind `FlexRouting`. Read `application/src/ext/java/org/opentripplanner/ext/flex/README.md`: it describes access/egress and flex-only itineraries, operating-window-based unscheduled trips, and continuous boarding. That internal README still references an older draft. Flex does not establish legal boarding zones, availability, booking rules, or timings from bare lines. No citywide flexible polygons or unrestricted continuous pickup in MVP; revisit only with evidence and a dedicated compatibility experiment.
- [Memory requirements](https://docs.opentripplanner.org/en/v2.9.0/System-Requirements/) depend on extract size and density. No Cape Town RAM, build-time, or latency measurement was made. Budget by measuring a corridor extract first, not by quoting another city's deployment.

## MapLibre and custom PWA

MapLibre GL JS is appropriate for route lines, stop markers, and selectable journey legs in a custom browser client. Official [installation documentation](https://maplibre.org/maplibre-gl-js/docs/) describes WebGL, ESM, and Next.js worker asset handling. v6 requires attention to worker/shared-module deployment; verify production builds, not only the dev server. Lazy-load the client-only map and retain a text itinerary when WebGL fails. MapLibre supplies neither tiles nor routing nor geocoding. Data/style/font rights and offline caching permissions are separate. Mobile performance must be measured on an ordinary Android phone; no benchmark was performed here.

## Other infrastructure and limits

- [MobilityData GTFS validator](https://github.com/MobilityData/gtfs-validator): README, CLI syntax and reports inspected; Apache-2.0. Pin a release and checksum during the spike. It checks feed structure, not whether a taxi actually operates.
- [pgRouting](https://github.com/pgRouting/pgrouting): README algorithm inventory and [GPL v2 licence text](https://github.com/pgRouting/pgrouting/blob/main/LICENSE) inspected, no runtime benchmark. It provides graph algorithms, not an assembled informal-transit passenger planner. Option C would still require state for boarding, vehicle continuity, service, transfers, and pedestrian routing.
- [Geofabrik South Africa](https://download.geofabrik.de/africa/south-africa.html) and [OSM licence](https://www.openstreetmap.org/copyright) inspected. OSM is ODbL; attribution and derived-database obligations need a release review. Keeping datasets separate aids provenance but does not automatically eliminate those obligations.
- Keep application-source, upstream-software, and transport-dataset licences separate. Distributing a modified GPL Core application requires a GPL compliance plan, including corresponding source; shipping OTP binaries/modifications requires retaining its LGPL notices and meeting applicable source obligations. Calling an independently deployed engine over HTTP is a different integration boundary from copying its code. MapLibre's notices must also be retained. Recommend a permissive licence for original TaxiGraph code after dependency review; this task does not create a LICENSE or relicense City data.

## Remaining uncertainty, with owners

| Question | Evidence required next |
|---|---|
| Can real Cape Town service be exported without defaults? | Maintainer/local verifier supplies dated direction, boarding, service-window and timing evidence; Sol enforces missing-input failures |
| Are public derivatives permitted? | Maintainer obtains applicable City permission or a clear superseding licence/replacement source; Sol records scope and gates artifacts |
| Does OTP produce plausible journeys and pedestrian transfers? | Sol runs the fixture evaluation in SOL-HANDOFF against a pinned graph; a local verifier reviews expected journeys |
| Does a headway approximation distort useful journeys? | Sol compares evidence-backed low/central/high timing scenarios and records result-set/rank changes |
| Are inferred stops or Flex needed? | Only after verified fixed boarding locations fail to cover the chosen journeys; do not preemptively add them |
| Is hosting practical for one student? | Measure peak build/runtime memory, artifact size and latency; reduce the covered region before adding infrastructure |
