# TSK-08: Develop JSONPersistenceAdapter & Atomic Write Protocol

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 3 Story Points / 12 Hours  
* **Story / Epic Reference:** FT-04 (Repository Ports & Safe Adapter)

## 📖 Description & Objectives

Construct the outbound infrastructure adapter `JSONPersistenceAdapter` inside `src/infra/adapters.py` implementing `ILibraryRepository`. The adapter serializes memory states to `db_backup.json` using atomic replace operations.

## ✅ Definition of Ready (DoR)

* [ ] Outbound repository interfaces in `src/app/ports.py` defined.
* [ ] Namespace `src/infra/` ready.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Functional):** Adapter converts in-memory states to JSON strings and writes them to local disk storage.
* [ ] **Criterion 2 (Resilience):** Writes serialize to `db_backup.tmp` first, then perform an atomic operating system rename to replace `db_backup.json`. Rotates old backup to `db_backup.json.bak` on success.
* [ ] **Criterion 3 (Quality/Test):** Persistence tests in `tests/test_persistence.py` simulate mid-write crashes, asserting that active states are not corrupted.
* [ ] **Criterion 4 (Review):** Implements schemas validating file structures on boot.
