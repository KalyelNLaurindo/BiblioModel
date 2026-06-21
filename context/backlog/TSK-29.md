# TSK-29: Structured Transaction Journal Logging (Write-Ahead Log)

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 4 Hours  
* **Story / Epic Reference:** FT-04 / RESILIENCE  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

To achieve maximum data resilience and reduce the risk of state loss during hardware or power failures, implement an append-only transaction journal file (`transaction_journal.log`). Before serializing the full database snapshot to `db_backup.json`, append the structural transaction action payload (e.g., checkout details, return operations, reader registrations) to the log file. In the event of a system crash, boot-up self-healing logic must be able to replay unapplied journal transactions on top of the last valid backup (`db_backup.json.bak`).

## ✅ Definition of Ready (DoR)

* [x] Persistence module `JSONPersistenceAdapter` functional (TSK-08).
* [x] Health checks and backup restoration code are already active (TSK-12).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **[Testing/Quality - TDD]:** Write integration tests verifying that transaction payloads are correctly appended to the journal before snapshot flushes.
* [ ] **[Functional - Logging]:** Implement the append-only write routine inside `JSONPersistenceAdapter` using native file flushes (`fsync`) to ensure the transaction log is safely written to disk.
* [ ] **[Functional - Recovery]:** Extend the startup health check in `adapters.py` to replay transactions from `transaction_journal.log` when restoring from `db_backup.json.bak` after a crash.
* [ ] **[Verification]:** All new and existing unit/integration tests pass 100% green.
