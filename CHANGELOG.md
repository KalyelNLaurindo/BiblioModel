# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-06-23

### Added
- **Dynamic Localization (i18n) & Multi-Language Support (TSK-32 & TSK-33)**:
  - Formulated dynamic translations in JSON resources across 5 languages (`pt`, `en`, `fr`, `es`, `de`).
  - Added an override command flag `--lang` to intercept and set language contexts on-the-fly.
  - Localization of CLI outputs, help menus, database schemas, tables headers, and interactive shell structures.
  - Robust isolated testing environment with global mocks in `tests/conftest.py`.
- **Advanced Architecture & Resilience Foundations (Phase 9)**:
  - **Unit of Work (UoW) Pattern (TSK-26)**: Orchestrates transactional consistency across the domain adapters and entities.
  - **Domain Events & Dispatcher (TSK-27)**: Publisher-subscriber mechanism facilitating clean side-effect execution inside domain boundaries.
  - **Dependency Injection (DI) Container (TSK-28)**: Centralized component graphs setup on startup.
  - **Write-Ahead Logging (WAL) / Transaction Journal (TSK-29)**: Resilient crash recovery logging protocol restoring uncommitted repository state.
  - **Single Responsibility Principle (SRP) CLI Refactor (TSK-30)**: Split the CLI controller monolith into modular presenter/use-case routers.

## [1.1.0] - 2026-06-18

### Added
- **Interactive CLI Shell Usability & Colors (TSK-25)**:
  - Enhanced interactive `shell` startup screen with guidelines written in English.
  - Formatted the tip and recommended command shortcuts with ANSI escape color sequences.
- **Fine Waiver & Discount Policy Engine (TSK-24)**:
  - Created `FinePolicyEngine` in `src/domain/policy.py` to calculate fine reductions based on configurable rules.
  - Implemented rules for PCD waiver (100%), institutional system delay waiver (100%), book donation discount (50%), and first offense discount (25%).
  - Integrated policy calculations in `ReturnUseCase.execute` and added prompt confirmation mechanisms in CLI for rules requiring operator approval.
  - Added audit trailing for applied discounts in `bibliomodel.log` and closing records of `loan_history.json`.
- **Book Popularity Ranking & Hold Queue Stats (TSK-23)**:
  - Tracked book usage via `checkout_count` inside `BookEntity`.
  - Added CLI `popularity-report` subcommand showing total checkouts, reservation queue lengths, and underutilized books.
  - Automatic purchase quantity recommendations for titles with high demand.
- **Patron Loan History Report (TSK-22)**:
  - Implemented `LoanHistoryAdapter` persisting finished loans in `loan_history.json`.
  - Created CLI `reader-history` command with filters for overdue-only records, limit lists (`--last-n`), and safe text exporting.
- **Overdue Book Auto-Suspension Engine (TSK-21)**:
  - Automated reader blocking in `CheckoutUseCase` when any late books cross the threshold defined in `config.ini`.
  - Added `check-overdue` subcommand to reconcile all reader suspension states.
- **Reports Exporting, Advanced Search, and Notifications (Phase 7)**:
  - Unified `export` command outputting CSV/HTML status lists.
  - Advanced partial/case-insensitive search for books and readers via `search-books` and `search-readers`.
  - `notify-overdue` command generating mock email notifications in `./notifications/` for late return warnings.

### Modified
- Extended `ReaderEntity` with `reader_type` and `BookEntity` with `checkout_count`.
- Updated `JSONPersistenceAdapter` to serialize/deserialize all newly introduced domain attributes.
- Added `[fine_policy]` configuration section to `config.ini`.

## [1.0.0] - 2026-06-12

### Added
- Pure Python 3.10+ offline-first business rules domain model.
- Core config provider and INI config parser adapter (`config.ini`).
- Domain entities: `BookEntity` (with FIFO hold queue), `ReaderEntity`, and `LoanEntity`.
- Fine calculation domain services (`FineCalculator`).
- Application use cases: `CheckoutUseCase`, `ReturnUseCase`, `ReserveUseCase`, and `WaiveFineUseCase`.
- Data safety with atomic state serialization adapter (`JSONPersistenceAdapter`) featuring temporary file replacement and recovery self-healing.
- Inbound client console routers with argparse parsing, interactive shell mode, and formatted output table rendering.
- Help and dynamic business rules display menu (`help`, `-h`, `--help`).
- Hardened input sanitization pipeline preventing directory traversal attacks (`..`, `/`, `\`), empty fields, and strict regex pattern check on Book/Reader IDs.
- Setuptools configuration in `pyproject.toml` exposing global script `bibliomodel`.

