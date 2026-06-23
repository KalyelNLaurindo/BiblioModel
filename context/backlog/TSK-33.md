# TSK-33: UI Presenter CLI Localization Adapter

* **Owner / Assignee:** Kalyel Nunes Laurindo / Tech Lead  
* **Estimated Effort:** 3 Hours  
* **Story / Epic Reference:** FT-10 / i18n Core  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Refactor the BiblioModel UI Presenter layer (`src/infra/cli.py` and `src/infra/shell.py`) to map all console outputs to the dynamic translation service.

Tasks:
1. Extract all hardcoded output messages, tables columns titles, error prompts, and reports layouts into localized key value JSON maps.
2. Update the presenter classes to fetch localized strings using `ITranslationService`.

## ✅ Definition of Ready (DoR)

* [x] i18n Core Translation Service and directories structure are implemented (TSK-32).
* [x] Presentation adapters `cli.py` and `shell.py` exist (TSK-09, TSK-15).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **[Testing/Quality - TDD]:** Unit tests verify that calling Presenter methods prints correct language keys mapping depending on active language mock.
* [x] **[Functional - Presenter]:** All UI screens, tables (`list-books`, `list-readers`, `list-loans`), and output messages are loaded dynamically from locale translation resource files.
* [x] **[Functional - Spacing]:** Renders aligned tabular layouts even when translation keys have varying text lengths.
* [x] **[Verification]:** `pytest` tests pass 100% green.
