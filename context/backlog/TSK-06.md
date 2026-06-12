# TSK-06: Create Application Use Case - ReturnUseCase

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 3 Story Points / 12 Hours  
* **Story / Epic Reference:** FT-03 (Use Case Interactors)

## 📖 Description & Objectives

Construct the application use case class `ReturnUseCase` inside `src/app/use_cases.py` following the inbound port interface `IReturnUseCase` defined in `src/app/ports.py`. This class coordinates book returns, invokes fine calculations, and updates hold queues.

## ✅ Definition of Ready (DoR)

* [ ] Target application package ready.
* [ ] FineCalculator engine is tested.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Functional):** Return updates book status to `Available` (or `Reserved` if a hold exists) and applies overdue charges to the reader's record.
* [ ] **Criterion 2 (Domain Invariant):** Auto-suspends readers if outstanding fines accrue.
* [ ] **Criterion 3 (Quality/Test):** Tests in `tests/test_use_cases.py` assert return flow, updates, and fine accrual.
* [ ] **Criterion 4 (Review):** Class depends on outbound interfaces (`ILibraryRepository`) rather than concrete adapters.
