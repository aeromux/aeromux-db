# Changelog

All notable changes to Aeromux Database Builder are documented in this file.

This changelog covers the **builder tool** itself, not the generated database. Each weekly database release has its own record counts and details on the [Releases](https://github.com/nandortoth/aeromux-db/releases) page.

## [1.1.0] — 2026-03-10

### Added

- New data source: [Plane Alert DB](https://github.com/sdr-enthusiasts/plane-alert-db) — community-maintained database of notable aircraft (military, government, VIP). Provides operator names, model descriptions, and military flags.
- Pipeline expanded from 11 to 13 steps to accommodate the new source.
- Registration conflict resolution now covers five sources with updated priority rules.

### Changed

- `operator_name` in `aircraft_view` now resolves through three fallback tiers: `operators` table, `aircraft_fallbackdata`, then `owner_operator` from `aircraft_details`. The `owner_operator` column is no longer exposed as a separate view column.

### Fixed

- Filter out placeholder registrations containing only `?` characters across all five data source parsers.
- Fix majority rule tie-breaking in registration conflict resolution — when multiple values each have 2+ agreeing sources, the group backed by the highest-priority source now wins.

## [1.0.1] — 2026-03-08

### Added

- Retry logic for HTTP downloads with exponential backoff (5 attempts, 1m/2m/4m/8m/16m) and 10s connect timeout to handle transient network failures in CI.
- Unit tests for the download retry mechanism.
- `pytest` as a dev dependency so `uv run pytest` works out of the box.

### Changed

- Scheduled CI build moved from Sunday 06:00 UTC to Sunday 03:15 UTC to reduce network timeout risk during off-peak hours.

## [1.0.0] — 2026-02-22

Initial release of the Aeromux Database Builder.

### Added

- Build a unified SQLite database from four aircraft data sources: Mictronics, ADS-B Exchange, OpenSky Network, and type-longnames.
- Intelligent registration conflict resolution across sources using majority vote, FAA N-number detection, IATA pattern matching, and source priority rules.
- Calendar-based database versioning (`YYYY.Q.wWW_rR`) computed automatically at build time.
- Automated weekly builds via GitHub Actions with database published as a GitHub Release.
- Programmatic access to the latest database version via the GitHub Releases API.

---

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).
