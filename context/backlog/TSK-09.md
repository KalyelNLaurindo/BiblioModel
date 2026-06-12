# TSK-09: Build CLI Parser and Command Arguments Router

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 3 Story Points / 12 Hours  
* **Story / Epic Reference:** FT-05 (CLI & Alerts Router)

## 📖 Description & Objectives

Construct the console interface handler `CLIController` inside `src/infra/cli.py` using Python's `argparse`. The controller parses operations (e.g. `loan`, `return`, `reserve`, `report`) and routes inputs to use case engines.

## ✅ Definition of Ready (DoR)

* [x] Target use cases `CheckoutUseCase`, `ReturnUseCase`, `ReserveUseCase` are ready.
* [x] Command signatures and parameter formats mapped.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **Criterion 1 (Functional):** Operator executes shell actions (`python main.py loan --reader R101 --book B202`), receiving text response validations.
* [x] **Criterion 2 (Quality/Test):** Integration tests in `tests/test_use_cases.py` (or test_infra.py) verify parser arguments and input validations.
* [x] **Criterion 3 (Security/Resilience):** Command inputs sanitize strings, blocking malformed arguments.
* [x] **Criterion 4 (Review):** Controller decouples logic, translating inputs to use case payloads.

