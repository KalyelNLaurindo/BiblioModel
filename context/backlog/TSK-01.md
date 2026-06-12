# TSK-01: Implement Core Configuration Parser and Logging Setup

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-01 (Bootstrap & Config Setup)

## 📖 Description & Objectives

Implement log setups and the config parser. The configuration parameters (daily fine rates, grace periods, max active loan count) must be externalized inside `config.ini` and loaded using Python standard library `configparser` in `src/infra/adapters.py`. Logging configurations must save reports in `bibliomodel.log`.

## ✅ Definition of Ready (DoR)

* [ ] Directory workspace initialized.
* [ ] Target namespaces `src/infra/` and `src/app/` are defined.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Functional):** System reads settings (`max_loans`, `grace_period_days`, `daily_fine_rate`) from `config.ini` file using `configparser`.
* [ ] **Criterion 2 (Quality/Test):** Unit tests located in `tests/test_persistence.py` check configuration file fallback parsing, asserting correct return of values.
* [ ] **Criterion 3 (Security/Resilience):** Logs in `bibliomodel.log` format transactions cleanly, hiding any user sensitive information.
* [ ] **Criterion 4 (Review):** Zero external library imports are utilized in the config adapters.
