# TSK-12: Implement Self-Healing Schema Recovery and Disaster Recovery DRP Suite

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-04 (Repository Ports & Safe Adapter)

## 📖 Description & Objectives

Construct a boot-time database validation and automatic recovery system in `src/infra/adapters.py`. When the application boots, the JSON persistence adapter must read `db_backup.json` and validate its fields against the expected schema. If structural damage or corrupted JSON formatting is detected, the adapter must automatically restore the state from `db_backup.json.bak` and log a warning indicator.

## ✅ Definition of Ready (DoR)

* [ ] Outbound repository adapters are functional.
* [ ] Atomic write replace loops are implemented.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Functional):** The bootloader auto-heals corrupted JSON database states by rolling back to `.bak` files when standard parsing fails.
* [ ] **Criterion 2 (Quality/Test):** Integration tests in `tests/test_persistence.py` simulate structural file corruption and assert that data is successfully recovered from the backup.
* [ ] **Criterion 3 (Security/Resilience):** Warning console logs alert the operator when recovery is triggered.
* [ ] **Criterion 4 (Review):** Implements atomic swaps during the recovery phase to prevent nested write crashes.
