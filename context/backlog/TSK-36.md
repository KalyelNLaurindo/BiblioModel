# TSK-36: Robustness and Boundary Tests for JSONPersistenceAdapter

* **Owner / Assignee:** Kalyel Nunes Laurindo / Tech Lead  
* **Estimated Effort:** 3 Hours  
* **Story / Epic Reference:** FT-10 / Architectural Resilience  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Expose the `JSONPersistenceAdapter` to boundary and robustness checks. Ensure that the database backup mechanism is fully resilient and recovers gracefully when:
1. The JSON database file is completely empty or contains malformed data.
2. The operating system blocks file operations (simulating file locks or permission issues).
3. The atomic write mechanism fails mid-operation, ensuring the backup `.bak` file remains untouched and valid.

## ✅ Definition of Ready (DoR)

* [ ] Database persistence layer is fully implemented (TSK-08 & TSK-12).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **[Testing/Quality - TDD]:** Test cases under `tests/test_persistence.py` simulate disk write failures, permission issues, and empty/invalid databases.
* [ ] **[Functional - Resilience]:** The system correctly restores the `.bak` file if the primary `db_backup.json` is missing or corrupted, raising a domain exception only if both are unavailable/invalid.
* [ ] **[Verification]:** pytest runs successfully with 100% pass rate.

---
**Author:** Kalyel N. Laurindo / Software Engineer
