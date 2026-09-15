# Data sources and Cape Town profile

Research date: 2026-09-15. Counts below describe the retrieved snapshot, not the number of operating taxi services. No passenger journeys or stops were field-verified.

## 1. Primary City taxi-route layer

| Property | Observed value |
|---|---|
| Publisher/access | City of Cape Town GIS; public, unauthenticated read queries succeeded |
| Layer | [ODP_SPLIT_6 / FeatureServer / 11](https://citymaps.capetown.gov.za/agsext/rest/services/Theme_Based/ODP_SPLIT_6/FeatureServer/11) |
| Portal | [Taxi Routes](https://odp-cctegis.opendata.arcgis.com/datasets/cctegis::taxi-routes/about); client-rendered page supplied no readable metadata in web retrieval |
| Service item ID | `571ad60d80f64c1cb7e0fa58db562094` (service identifier, not a route ID) |
| Attribution | Western Cape Government, Department of Transport and Public Works (publisher metadata spelling differs) |
| Geometry | `esriGeometryPolyline`; source EPSG:3857/102100; queried EPSG:4326 |
| Formats/capabilities | JSON, GeoJSON, PBF; query/extract; pagination; maxRecordCount 2,000 |
| Layer fields | `OBJECTID` OID; `ORGN` nullable string(100); `DSTN` nullable string(100); `Shape__Length` double |
| Update evidence | No per-feature timestamps, service-day fields, or `editingInfo` value in retrieved metadata; no verified operational update cadence |
| Confidence | High in the reported snapshot/schema measurements; unknown in current operation, direction, boarding and timing |

The layer advertises `NAME` as its display field, but does not expose a NAME attribute. Do not design the importer from that display-field label. `OBJECTID` is a source-local identifier, not a public route number. Deriving a display label from ORGN/DSTN is permissible if it is identified as a generated label.

### Rights: unresolved and restrictive

The directly queried [layer iteminfo](https://citymaps.capetown.gov.za/agsext/rest/services/Theme_Based/ODP_SPLIT_6/FeatureServer/11/iteminfo?f=json) contains `licenseInfo` beginning:

> All rights reserved. No part of this data may be reproduced or transmitted

It goes on to require permission from the City's Strategic Development Information and GIS Department and attribution for map use. The general [City Open Data terms](https://www.capetown.gov.za/General/Terms-of-use-open-data) describe free access and disclaim data accuracy; they do not establish an unambiguous dataset-specific open licence overriding this notice. A portal search restricted to owner `cctegis` returned zero items; that unsuccessful lookup does not negate the live layer.

**Release gate:** record permission or an applicable superseding licence covering storage, modification, derived GTFS/graphs, display and redistribution as needed; otherwise use independently sourced, clearly licensed data. Do not label this dataset CC0, CC-BY, or public domain. Do not commit the downloaded geometry or assume a provincial mirror grants new rights. This architecture task retains aggregate findings and a few record examples, not the full dataset. No permission request was sent.

### Measured profile

Queried count and object IDs separately; fetched all records in an ordered response below the 2,000-record limit. Count = returned records = distinct requested/returned object-ID set: **1,466**. No transfer-limit flag was set. This is a complete retrieval for those checks, but the server did not provide a transactionally frozen revision.

| Measurement | Result |
|---|---:|
| Single-path polylines | 1,466 |
| Multipart features | 0 |
| Vertices | 577,511 |
| Null/empty geometries | 0 |
| Paths with fewer than two distinct coordinates | 0 |
| Non-finite/out-of-world-range coordinates | 0 |
| Invalid lines under Shapely `is_valid` | 0 |
| Non-simple lines under Shapely `is_simple` | 418 |
| Features whose path closes exactly | 3 |
| Metric line length, min/max (EPSG:32734) | 387.36 m / 122,938.60 m |
| Null/empty origin or destination strings before trimming | 0 / 0 |
| Blank origin/destination after trimming | 19 / 19 |
| Distinct raw origin/destination strings | 235 / 489 |
| Distinct raw ordered origin-destination pairs | 1,123 |
| Repeated raw ordered origin-destination groups | 224 |
| Same raw origin and destination | 23 features, including 19 blank pairs |
| Unordered pairs with both label directions present | 147 |
| Groups of exactly identical ordered coordinate sequences | 49 groups, 53 excess records |
| Groups identical allowing full coordinate-sequence reversal | 54 groups, 58 excess records |
| Additional near-duplicate candidate pairs under the test below | 11 |

Non-simple lines can self-cross or retrace; they are not necessarily invalid routes. Geometric validity says nothing about road alignment, legal movement, actual service, or safe walking. Review retracing, loops and direction before generating stop order. Do not “repair” them by splitting at every intersection.

Near-duplicate method: group by trimmed uppercase ordered ORGN/DSTN, omit blank groups, compare the 544 within-group pairs, exclude topologically equal lines, require length difference at most 5% of the longer line, corresponding endpoints within 100 m, and Shapely discrete Hausdorff distance at most 50 m in EPSG:32734. Eleven pairs passed. This is a **limited candidate search**, not a full citywide duplicate count; it misses spelling variants and reverse directions. Thresholds are research heuristics, not merge rules.

Examples: OBJECTIDs 12/866 (NYANGA–WYNBERG, 38.06 m Hausdorff), 207/656 (KHAYELITSHA–SEA POINT, 22.60 m), 475/476 (MELTON ROSE–TUSCANY GLEN, 17.43 m). Preserve both source records until reviewed.

### Sample attributes and a contradiction

| OBJECTID | ORGN | DSTN |
|---:|---|---|
| 1 | BELLVILLE | DURBANVILLE |
| 2 | BELLVILLE | NYANGA |
| 3 | BELLVILLE | KHAYELITSHA |
| 4 | BELLVILLE | MOWBRAY |
| 5 | GUGULETU | CLAREMONT |
| 20 | BONTEHEUWEL | MOWBRAY |
| 127 | BONTEHEUWEL | ATHLONE |
| 1366 | one space | one space |

**20 and 127 have exactly identical geometry but different destination labels.** This directly falsifies “geometry equality proves the same service.” BELLVILLE records 1–4 share the same first coordinate, but no record establishes that coordinate as a verified boarding point. ORGN/DSTN are directional labels; digitized geometry order and reverse-service availability remain unverified.

### Reproduce the measurements

Base URL: the primary layer above. Use HTTP GET with URL-encoded parameters:

```text
Layer metadata: ?f=pjson
Rights metadata: /iteminfo?f=json
Count: /query?where=1%3D1&returnCountOnly=true&f=json
IDs: /query?where=1%3D1&returnIdsOnly=true&f=json
Records: /query?where=1%3D1&outFields=*&outSR=4326&returnGeometry=true&orderByFields=OBJECTID&resultOffset=0&resultRecordCount=2000&f=json
```

For an implementation, prefer object-ID batches with duplicate/missing-ID checks, before/after count/ID checks, bounded retries, response error checks (ArcGIS can return an error inside HTTP 200), metadata capture and raw-byte SHA-256. If the layer changes during extraction, mark the run inconsistent and retry. Never assume 2,000 records will always suffice.

Research used Python 3.13.13, Shapely 2.1.2, pyproj 3.8.0. Exact duplicates used full returned float-coordinate tuples, with no rounding; reverse comparison canonicalized each tuple against its reversed tuple. Attributes used raw strings except the explicitly trimmed near-duplicate grouping. Geometry tests used all records. The SHA-256 of the temporary PowerShell-reserialized route response was `3d6d517765216b65a9e1bfdba98199330acf87d04ea70cde92874f507fb36472`; this is **not** a raw HTTP payload checksum or a retrievable archive reference. Sol must capture a new lawful snapshot and must not treat this hash as downloadable evidence.

## 2. Related City and provincial sources

| Source | Inspected content and provenance | Rights/freshness/limitations |
|---|---|---|
| [City Transport MapServer/5](https://citymaps.capetown.gov.za/agsext/rest/services/Theme_Based/Transport/MapServer/5) | Taxi polylines; ORGN/DSTN/OID and shape length; EPSG:3857; metadata read | Appears related to primary layer; record equivalence not established. Not independent corroboration; no extra service fields |
| [Legacy City FeatureServer/97](https://citymaps.capetown.gov.za/agsext/rest/services/Theme_Based/Open_Data_Service/FeatureServer/97) | Parent service lists Taxi Routes | Layer retrieval timed out; do not use as primary or report a feature count |
| [Western Cape Transportation MapServer/24](https://gis.westerncape.gov.za/server2/rest/services/SpatialDataWarehouse/Transportation/MapServer/24) | Metadata says City download 2021-08-23, publication 2021-05-18; polylines in EPSG:32734; `OBJECTID_1`, original `OBJECTID`, ORGN/DSTN and lengths | Historical mirror, not a current operational survey. Metadata inspected, full records not profiled. Copyright City; no independent licence established |
| [Western Cape NGI Road Transport Facilities/13](https://gis.westerncape.gov.za/server2/rest/services/SpatialDataWarehouse/Transportation/MapServer/13) | Polygon layer includes `FEAT_TYPE=Taxi Rank`; `ENTITY_NAME`, `OP_STATUS`, `SOURCE_CURR`, capture/revision fields and source accuracy | Potential rank-footprint evidence, not a stop-to-route join or boarding entrance. Metadata inspected only; Cape Town subset/count, record dates and reuse terms unverified |
| [City Transport service](https://citymaps.capetown.gov.za/agsext/rest/services/Theme_Based/Transport/MapServer) | Lists MyCiTi stops/routes and railway layers | These are other modes, not evidence of taxi stops. No taxi rank layer found in this service; that does not prove none exists elsewhere |

Do not import another municipality's schema: the search result with `route_id` and `dayofweek` belongs to **Tshwane**, not this Cape Town layer. No present Cape Town field supports an operational-day claim.

## 3. Supporting data

- **OSM streets:** [Geofabrik South Africa PBF](https://download.geofabrik.de/africa/south-africa.html), OSM contributors, [ODbL](https://www.openstreetmap.org/copyright). Download page inspected, extract not downloaded/built. The page listed a roughly 400 MB country PBF and no subregions. Use a buffered corridor/city extract with complete ways via existing extraction tools; preserve extract timestamp/checksum. OTP consumes PBF directly. Missing gates, footways and rank entrances remain a validation risk. Map tiles are a separate product with separate service terms.
- **OSM transit/ranks:** community route relations and stop/transport-facility features are candidates for later evidence and an OSM adapter. No Cape Town relation/rank completeness count was established. Do not interpret all `amenity=taxi` points as minibus ranks. Independently check tags, relation membership, age, and local meaning.
- **Manual verification:** no observations currently supplied. Record location, actual direction, boarding/alighting rules, date/time, observation interval and method, observed departures/travel durations, and review status. An operator statement and a single observed trip have different evidential scope. Keep personal contact details private; store a publishable evidence summary with consent/rights.
- **Other transit feeds:** no current, licensed, ready-to-route Cape Town minibus GTFS feed was verified in this task. A future GTFSAdapter should use a mature parser and preserve feed metadata; it is not an MVP implementation requirement.

## 4. Honest GTFS mapping

The [GTFS reference](https://gtfs.org/documentation/schedule/reference/) defines the interoperability format. The following table is TaxiGraph's proposed mapping/gating policy, not a claim that all these facts are present.

| Concept | Present/derivable | Missing or uncertain; export rule |
|---|---|---|
| Agency/publisher | TaxiGraph can identify itself as feed publisher and set the known city timezone | Actual operating organization absent; do not call the City the operator. Resolve an honest agency representation before real export |
| Route identifier/name/type | Stable internal IDs can be assigned; endpoint label can be generated; minibus mapped to bus mode with original subtype retained | Public route number absent; deduplication/route-family membership requires review |
| Shape | Reprojection and ordered shape points | Orientation, retracing, fidelity and current path unverified |
| Trip/direction | Candidate variant from each source geometry | Physical direction and ordered service pattern need evidence; no automatic return trip |
| Stops and stop sequence | Candidate geometry endpoints; separate rank polygons may help | Route-specific boarding/alighting points, names, entrances and transfer permissions absent |
| Calendar/validity | City timezone is known | Days, holiday exceptions and operating windows absent; absence must block real-service export |
| Frequency | None in layer | `exact_times=0` still needs an evidenced headway and service interval; unknown headway cannot be left as a made-up constant |
| Stop times | Relative offsets can be estimated from measured trips with a declared method | Travel duration/dwell absent; distance divided by arbitrary speed is not an observed taxi runtime |
| Fares | None | Omit fare tables when unknown; never substitute a zero fare |
| Transfers | Candidate proximity from geometry and pedestrian network | Feasibility requires actual boarding locations and accessible walking paths; crossing polylines are insufficient |
| Provenance | URLs, source IDs, retrieval and transform metadata | GTFS cannot carry the full claim history; retain a versioned sidecar manifest and canonical records |

**Conclusion:** the GIS data can seed route shapes and review candidates. It cannot alone generate a truthful operational feed. Supplement a tiny subset with evidence; keep incomplete records outside routing; or deliver a clearly limited geometry catalogue. Artificial software fixtures can test OTP plumbing separately. Flex or a custom router does not remove these information gaps.
