# TaxiGraph

TaxiGraph is a journey-planning project for Cape Town's informal minibus taxi network — the routes, ranks, and boarding practices that formal transit data typically leaves out.

Rather than guessing at schedules or inventing service where none is confirmed, TaxiGraph treats every claim (a route, a stop, a fare, a direction of travel) as evidence that must be sourced, dated, and verified before it reaches a rider. Unknown stays unknown; it is never quietly filled in as zero, daily, or bidirectional.

## Status

**Documentation and architecture only — no implementation yet.** The project is currently at the feasibility-spike stage: proving that a small, manually verified set of real Cape Town journeys can be routed correctly before any database, frontend, or public deployment is built.

No OTP graph has been built and no real journey has been validated. See [docs/MVP-SPEC.md](docs/MVP-SPEC.md) for the exact gates that must pass before that claim can be made.

## How it's meant to work

- **Own the hard part.** TaxiGraph owns source adapters, a canonical data model, identity resolution, provenance, and verification for informal transit data. GTFS is treated as an *export format*, not the source of truth.
- **Reuse the routing engine.** [OpenTripPlanner](https://www.opentripplanner.org/) handles transit routing, transfers, and OSM-based walking directions — it isn't reinvented here.
- **Reuse the map.** [MapLibre GL JS](https://maplibre.org/) will eventually power the client map, once real journeys pass the feasibility gate.
- **Files first, database later.** The feasibility spike works entirely with files. PostGIS is introduced only after real-data feasibility is proven.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full component breakdown and boundaries, and [docs/ADR.md](docs/ADR.md) for the decisions behind them.

## Documentation

| Doc | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) | Ground rules for anyone (human or agent) working in this repo |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Selected architecture, component boundaries, integration contracts |
| [docs/MVP-SPEC.md](docs/MVP-SPEC.md) | The staged milestones and the gates each one must pass |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Sequential implementation tasks |
| [docs/DATA-MODEL.md](docs/DATA-MODEL.md) | Canonical data model |
| [docs/DATA-SOURCES.md](docs/DATA-SOURCES.md) | Source data and rights/licensing notes |
| [docs/RESEARCH.md](docs/RESEARCH.md) | Background research behind the architecture decision |
| [docs/SOL-HANDOFF.md](docs/SOL-HANDOFF.md) | Spec for the current active task (feasibility harness) |

## Principles

- **No invented transport facts.** Schedules, headways, fares, operating days, and boarding permissions are never assumed — only recorded when there's evidence for them.
- **Provenance survives every transformation.** Source, retrieval time, verification time, and evidence status travel with every claim from raw import to public export.
- **Real data and test fixtures never mix.** Synthetic data used to exercise the software is always clearly labelled and kept separate from verified Cape Town data.

## License

[MIT](LICENSE) © 2026 Ubayd Hattas
