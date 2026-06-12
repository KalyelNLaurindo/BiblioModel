# TSK-16: Implement Built-in Help Menu & Documentation System

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 1 Story Point / 4 Hours  
* **Story / Epic Reference:** FT-05 (CLI & Alerts Router)

## 📖 Description & Objectives

Construct a built-in help and documentation command inside `src/infra/cli.py` (e.g. `bibliomodel help` or triggered via `-h`/`--help`). The help system must print detailed command descriptions, parameter types, list of active business rules (loan duration, fine rates, reader constraints), and usage examples.

## ✅ Definition of Ready (DoR)

* [ ] CLI Parser is configured.
* [ ] External rules configurations are loaded.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Functional):** Executing help commands outputs clear descriptions, listing command structures (`loan`, `return`, `reserve`, `report`) and accepted parameters.
* [ ] **Criterion 2 (Quality/Test):** Console output format is verified using test scripts asserting formatting guidelines.
* [ ] **Criterion 3 (Security/Resilience):** Help menu successfully extracts and presents rules from `config.ini` dynamically without raising file read errors.
* [ ] **Criterion 4 (Review):** Decoupled structure maintained, avoiding inline string bloating in core logic components.
