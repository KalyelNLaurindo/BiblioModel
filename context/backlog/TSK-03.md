# TSK-03: Build Domain Entities - ReaderEntity & LoanEntity

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-02 (Bounded Domain Objects)

## 📖 Description & Objectives

Construct the pure domain model classes `ReaderEntity` and `LoanEntity` in `src/domain/entities.py`. These classes encapsulate readers' profiles, active loans lists, borrowing eligibility rules, and loan duration metadata.

## ✅ Definition of Ready (DoR)

* [ ] Target domain module namespace is ready.
* [ ] BookEntity status flows are completed.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **Criterion 1 (Functional):** `ReaderEntity` handles `reader_id`, `name`, `status` (`Active` or `Suspended`), `fine_balance`, and `active_loans`. `LoanEntity` encapsulates loan records.
* [x] **Criterion 2 (Domain Invariant):** Reader status transitions to `Suspended` if any loan date exceeds due rules or unpaid fines accrue.
* [x] **Criterion 3 (Quality/Test):** Tests in `tests/test_domain.py` verify checkout limitations for suspended readers.
* [x] **Criterion 4 (Review):** Layer encapsulation is strictly respected (no imports of persistence/CLI modules).

