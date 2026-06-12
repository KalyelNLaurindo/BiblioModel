# TSK-17: Malicious Input Validation and Shell Hardening

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-05 (CLI & Alerts Router)

## 📖 Description & Objectives

Construct security validation checks and input formatting rules in `src/infra/cli.py` and `src/app/use_cases.py`. The system must sanitize all command argument inputs: strip trailing spaces, enforce alphanumeric rules and exact regex patterns on reader IDs (e.g. `R\d{3}`) and book IDs (e.g. `B\d{3}`), block directory traversal characters, and handle empty fields safely without crashing.

## ✅ Definition of Ready (DoR)

* [ ] CLI Controllers and Command Parser are completed.
* [ ] Argument fields are routed to use cases.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Functional):** System rejects invalid inputs (e.g. malformed IDs, spaces, negative numeric values) and returns warning alerts.
* [ ] **Criterion 2 (Quality/Test):** Unit tests in `tests/test_use_cases.py` and `tests/test_domain.py` assert input validation rules against boundaries.
* [ ] **Criterion 3 (Security/Resilience):** Rejects payload strings containing malicious escape patterns or local paths, protecting files from unauthorized tampering.
* [ ] **Criterion 4 (Review):** Sanitization pipeline is decoupled from core domain rules.
