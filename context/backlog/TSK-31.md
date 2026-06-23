# TSK-31: Testing Coverage Monitoring and CLI Exclusion Policy

* **Owner / Assignee:** Kalyel Nunes Laurindo / Tech Lead  
* **Estimated Effort:** 2 Hours  
* **Story / Epic Reference:** FT-10 (Architectural Resilience)  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Establish a formal test coverage verification quality gate in the CI/CD pipeline using `pytest-cov` / `coverage`. 
While the TDD-driven core (domain and application layers) is designed to maintain 100% test coverage, the UI presentation layer (`src/infra/cli.py` and `src/infra/shell.py`) is intentionally excluded from unit testing coverage. Testing interactive command prompt loops, ANSI color formatting, and console output structures is brittle and costly to maintain. 

This task implements:
1. Configuration in `pyproject.toml` / `.coveragerc` to ignore CLI adapters from coverage reports.
2. Enforcement of a strict 100% coverage threshold for the core layers (`src/domain/` and `src/app/`).
3. Explicit documentation of the testing policy.

## ✅ Definition of Ready (DoR)

* [x] Pytest suite containing 92 business rule tests is operational.
* [x] Dependencies for testing and code coverage are defined in `pyproject.toml`.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **[Functional - Configuration]:** Add `.coveragerc` or `pyproject.toml` configurations that define the source paths (`src/domain`, `src/app`) and explicitly exclude CLI adapters (`src/infra/cli.py`, `src/infra/shell.py`) from coverage metrics.
* [x] **[Functional - Enforcement]:** Set `--cov-fail-under=100` parameter for the covered core layers so that any untested domain rules or use cases break the pipeline.
* [x] **[Documentation]:** Update the Software Design Document (SDD) to outline the project's testing hierarchy and the rationale for excluding presentation layers.
* [x] **[Verification]:** Executing the test coverage command runs successfully and reports 100% code coverage for the target core modules.
