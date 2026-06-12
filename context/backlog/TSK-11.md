# TSK-11: Establish pyproject.toml Configuration and Unified Main Entry Point

* **Owner / Assignee:** Developer / Tech Lead  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-01 & FT-05 (Packaging / Execution)

## 📖 Description & Objectives

Define deployment packages and setup the application entry point. Build `pyproject.toml` inside the root workspace folder, setting metadata, dependency ranges, and the CLI execution script `bibliomodel = "src.main:main"`. Develop `src/main.py` executing configurations and parsing command lines.

## ✅ Definition of Ready (DoR)

* [x] Target directory structure is verified.
* [x] Python environment parameters and package versions are defined.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **Criterion 1 (Functional):** Project runs command-line triggers after standard installation (`pip install -e .` followed by `bibliomodel`).
* [x] **Criterion 2 (Quality/Test):** Shell scripts test installation validity and verify configuration loads.
* [x] **Criterion 3 (Security/Resilience):** Entry point recovers gracefully from file directory permission errors.
* [x] **Criterion 4 (Review):** Clean dependencies are kept in `pyproject.toml`, showing zero external package installations.
