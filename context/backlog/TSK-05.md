# TSK-05: Create Application Use Case - CheckoutUseCase

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 3 Story Points / 12 Hours  
* **Story / Epic Reference:** FT-03 (Use Case Interactors)

## 📖 Description & Objectives

Construct the application use case class `CheckoutUseCase` inside `src/app/use_cases.py` following the inbound port interface `ICheckoutUseCase` defined in `src/app/ports.py`. This class coordinates domain objects to checkout books, verifying user eligibility.

## ✅ Definition of Ready (DoR)

* [ ] Namespace `src/app/` initialized.
* [ ] Inbound port declarations defined.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Functional):** Checkout validates reader eligibility (loan count, suspensions, fines) and book availability before creating a loan record.
* [ ] **Criterion 2 (Domain Invariant):** Blocks checkout if reader is suspended or book is already loaned/reserved.
* [ ] **Criterion 3 (Quality/Test):** Unit tests in `tests/test_use_cases.py` execute checkout workflows under varying reader conditions.
* [ ] **Criterion 4 (Review):** class relies on dependency injection for repository interfaces.
