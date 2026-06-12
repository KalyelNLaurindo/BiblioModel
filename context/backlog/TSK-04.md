# TSK-04: Develop Domain Services - FineCalculator Engine

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-02 (Bounded Domain Objects)

## 📖 Description & Objectives

Construct the pure domain service class `FineCalculator` inside `src/domain/services.py`. This class processes late return events, calculating overdue durations beyond the grace period, and returning fine values based on daily rates loaded from configurations.

## ✅ Definition of Ready (DoR)

* [x] Target namespace `src/domain/services.py` exists.
* [x] Domain entities `ReaderEntity` and `LoanEntity` are completed.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **Criterion 1 (Functional):** Service accurately calculates daily late fees, validating that return dates preceding due dates result in $0.00 fine.
* [x] **Criterion 2 (Domain Invariant):** Calculation respects grace periods (no fees applied if late days are under threshold).
* [x] **Criterion 3 (Quality/Test):** Unit tests inside `tests/test_domain.py` verify fine math against varying dates and grace periods.
* [x] **Criterion 4 (Review):** Layer decoupling is maintained. Service does not import external libraries.

