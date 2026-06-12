# TSK-02: Build Domain Entity - BookEntity and FIFO Hold Queue

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 1 Story Point / 4 Hours  
* **Story / Epic Reference:** FT-02 (Bounded Domain Objects)

## 📖 Description & Objectives

Construct the pure domain model class `BookEntity` in `src/domain/entities.py`. This class encapsulates a physical book's status, enforcing state transition validations (e.g. `Available`, `Loaned`, `Reserved`) and managing a first-in-first-out (FIFO) reservation queue of reader IDs.

## ✅ Definition of Ready (DoR)

* [x] Bounded domain package namespace `src/domain/` exists.
* [x] Naming standards for entities defined.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **Criterion 1 (Functional):** `BookEntity` must be built. It encapsulates `book_id` (string), `title` (string), `status` (string), and `hold_queue` (FIFO array/list of reader IDs).
* [x] **Criterion 2 (Domain Invariant):** Changing states or adding users to the hold queue must enforce domain invariants (e.g., a book cannot be loaned if another reader holds the top reservation).
* [x] **Criterion 3 (Quality/Test):** Unit tests in `tests/test_domain.py` verify all states, transitions, and FIFO holds.
* [x] **Criterion 4 (Review):** The entity file is a pure Python implementation and imports zero infrastructure logic.
