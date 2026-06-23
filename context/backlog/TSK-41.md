# TSK-41: Size-based Log Rotation in setup_logger

* **Owner / Assignee:** Kalyel Nunes Laurindo / Tech Lead  
* **Estimated Effort:** 2 Hours  
* **Story / Epic Reference:** FT-01 / Bootstrap & Config Setup  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Prevent the log file (`bibliomodel.log`) from growing indefinitely by implementing size-based log file rotation:
1. Update `setup_logger` to replace standard `logging.FileHandler` with `logging.handlers.RotatingFileHandler`.
2. Configure rotation options via `config.ini` under `[logging]`:
   - `max_bytes` (maximum size of a log file before rotating, default: 1MB).
   - `backup_count` (number of rotated log files to retain, default: 5).
3. Ensure the logger configuration falls back safely if `config.ini` variables are missing or corrupted.

## ✅ Definition of Ready (DoR)

* [ ] Configuration adapter and logger setup are implemented (TSK-01).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **[Testing/Quality - TDD]:** Test cases assert that writing logs beyond the configured `max_bytes` rotates the file and creates `bibliomodel.log.1`, `bibliomodel.log.2`, etc.
* [ ] **[Functional - Logging]:** Logger uses `RotatingFileHandler` with limits configured inside `config.ini`.
* [ ] **[Verification]:** pytest runs successfully with 100% pass rate.

---
**Author:** Kalyel N. Laurindo / Software Engineer
