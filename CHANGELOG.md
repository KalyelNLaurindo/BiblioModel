# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
