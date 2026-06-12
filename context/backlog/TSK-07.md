# TSK-07: Create Application Use Case - ReserveUseCase

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 3 Story Points / 12 Hours  
* **Story / Epic Reference:** FT-03 (Use Case Interactors)

## 📖 Description & Objectives

Construct the application use case class `ReserveUseCase` inside `src/app/use_cases.py` following the inbound port interface `IReserveUseCase` defined in `src/app/ports.py`. This class manages the reservation of books that are currently checked out.

## ✅ Definition of Ready (DoR)

* [ ] Inbound ports for reservations defined.
* [ ] BookEntity hold queue methods implemented.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Functional):** Appends reader to target book's hold queue, shifting status to `Reserved`.
* [ ] **Criterion 2 (Domain Invariant):** Prevents readers from reserving books they currently hold, or placing redundant reservations.
* [ ] **Criterion 3 (Quality/Test):** Unit tests in `tests/test_use_cases.py` verify queuing and status changes.
* [ ] **Criterion 4 (Review):** Layer decoupling rules apply. Pure use case dependencies only.
