# TSK-07: Create Application Use Case - ReserveUseCase

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 3 Story Points / 12 Hours  
* **Story / Epic Reference:** FT-03 (Use Case Interactors)

## 📖 Description & Objectives

Construct the application use case class `ReserveUseCase` inside `src/app/use_cases.py` following the inbound port interface `IReserveUseCase` defined in `src/app/ports.py`. This class manages the reservation of books that are currently checked out.

## ✅ Definition of Ready (DoR)

* [x] Inbound ports for reservations defined.
* [x] BookEntity hold queue methods implemented.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **Criterion 1 (Functional):** Appends reader to target book's hold queue, shifting status to `Reserved`.
* [x] **Criterion 2 (Domain Invariant):** Prevents readers from reserving books they currently hold, or placing redundant reservations.
* [x] **Criterion 3 (Quality/Test):** Unit tests in `tests/test_use_cases.py` verify queuing and status changes.
* [x] **Criterion 4 (Review):** Layer decoupling rules apply. Pure use case dependencies only.
