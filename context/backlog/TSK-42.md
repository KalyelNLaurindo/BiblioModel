# TSK-42: Automatic Compression and Cleanup of Historical Logs

* **Owner / Assignee:** Kalyel Nunes Laurindo / Tech Lead  
* **Estimated Effort:** 3 Hours  
* **Story / Epic Reference:** FT-01 / Bootstrap & Config Setup  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Optimize disk usage by compressing older rotated log files (`.gz` format) and introducing an automated maintenance script:
1. Customize the `RotatingFileHandler` rotater behavior to automatically compress rotated files (`bibliomodel.log.1.gz`, etc.).
2. Add a CLI command or maintenance run `python src/main.py maintenance --clean-logs` to prune backups older than a configurable number of days.
3. Decouple disk operations to ensure that log archiving errors never crash the primary execution flow of the library loan commands.

## ✅ Definition of Ready (DoR)

* [ ] Log rotation using RotatingFileHandler is completed (TSK-41).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **[Testing/Quality - TDD]:** Test cases verify that rotated logs are outputted as compressed gzip archives.
* [ ] **[Functional - Cleanup]:** CLI maintenance command removes log files older than the retention threshold set in config.
* [ ] **[Verification]:** pytest runs successfully with 100% pass rate.

---
**Author:** Kalyel N. Laurindo / Software Engineer
