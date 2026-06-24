# TSK-39: Metadata Headers and Versioning for JSON Database

* **Owner / Assignee:** Kalyel Nunes Laurindo / Tech Lead  
* **Estimated Effort:** 4 Hours  
* **Story / Epic Reference:** FT-04 / Repository Ports & Safe Adapter  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Add metadata structure to the JSON persistence format to support versioning. This prevents data loss when updating domain models or persistence structures in the future:
1. Modify `db_backup.json` structure to include a `metadata` header containing:
   - `schema_version` (integer value, starting at 1).
   - `last_written_at` (ISO 8601 timestamp).
   - `engine_version` (current system software version).
2. Adapt reading and writing code in the `JSONPersistenceAdapter` to handle metadata headers transparently, ensuring that domain model lists remain isolated from database headers.

## ✅ Definition of Ready (DoR)

* [x] JSON persistence adapter is implemented (TSK-08).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **[Testing/Quality - TDD]:** Test cases assert that saving database outputs the correct metadata section, and that reading database without metadata defaults to version 0.
* [x] **[Functional - Database]:** Database JSON file is structured as `{ "metadata": { "schema_version": 1, ... }, "data": { ... } }`.
* [x] **[Verification]:** pytest runs successfully with 100% pass rate.

---
**Author:** Kalyel N. Laurindo / Software Engineer
